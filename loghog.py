
from __future__ import print_function, unicode_literals
import socket, hmac, hashlib, struct, zlib, ssl, random, select
import logging, logging.handlers
from collections import deque

try:
    import json
except ImportError:
    import simplejson as json

class LoghogHandler(logging.handlers.SocketHandler):

    VERSION = 1

    _FLAGS_GZIP = 0x01

    FORMAT_PROTO = '!LL {0}s'

    HMAC_DIGEST_ALGO = hashlib.md5

    def __init__(self, app_name, host='localhost', port=5566, stream=True, secret=None, compression=False, hostname=None, ssl_info=None, max_buffer_size=1024, print_debug=False):
        '''Initializes the LoghogHandler instance.

        param app_name : basestring
            Name of your app. This should be listed in loghogd.conf
        param host : basestring
            A hostname or an IP address. IPv6 addresses should not have brackets around them
        param port : int
            Port number
        param stream : bool
            Whether to use a stream or a datagram protocol
        param secret : bytestring
            Hashable secret shared with the server. Used for message signing
        param hostname : str
            Local hostname. If not bool(hostname) it is determined automatically
        param ssl_info : dict
            A dictionary containing two keys: pemfile and cacert. These should be paths to the
            SSL certificates necessary to talk to the server
        param max_buffer_size : positive int
            How many messages to queue up if the server is down, before dropping the oldest ones.
        param print_debug : bool
            This argument controls whether errors are suppressed silently, or printed to stdout.
            Use this if you are using SSL to view connection errors.
        '''

        logging.Handler.__init__(self)

        self.app_name = app_name
        self.address = (host, port)
        self.use_stream = stream
        self.secret = secret
        self.compression = compression 
        self.hostname = hostname
        self.max_buffer_size = max_buffer_size
        self.print_debug = print_debug

        self.pemfile = None
        self.cacert = None

        if ssl_info:
            self.pemfile = ssl_info['pemfile']
            self.cacert = ssl_info['cacert']

        if not hostname:
            self.hostname = socket.gethostname()

        self.flags = 0
        if self.compression:
            self.flags |= self._FLAGS_GZIP

        self.sock = None
        self.closeOnError = 0
        self.retryTime = None
        self.buffer = deque()
        #
        # Exponential backoff parameters.
        #
        self.retryStart = 1.0
        self.retryMax = 30.0
        self.retryFactor = 2.0

    def _resolve_addr(self, address, use_stream):
        '''Resolves the given address and mode into a randomized address record.'''

        socktype = socket.SOCK_STREAM if use_stream else socket.SOCK_DGRAM
        res = socket.getaddrinfo(address[0], address[1], 0, socktype)
        random.shuffle(res)
        return res[0]

    def makeSocket(self, timeout=1.0):
        '''Makes a connection to the socket.'''

        af, socktype, proto, cannonname, sa = self._resolve_addr(self.address, self.use_stream)
        
        s = socket.socket(af, socktype, proto)

        if hasattr(s, 'settimeout'):
            s.settimeout(timeout)

        if self.use_stream and self.pemfile:
            s = ssl.wrap_socket(s,
                keyfile=self.pemfile,
                certfile=self.pemfile,
                ca_certs=self.cacert,
                server_side=False,
                cert_reqs=ssl.CERT_REQUIRED
            )

        try:
            s.connect(sa)
        except Exception as e:
            if self.print_debug:
                print(e)

        return s

    def _encode(self, record):
        '''Encodes a log record into the loghog on-wire protocol.'''

        data = {
            'version': self.VERSION,
            'app_id': self.app_name,
            'module': record.name,
            'stamp': int(record.created),
            'nsecs': int(record.msecs * 10**6),
            'hostname': self.hostname,
            'body': self.format(record),
        }

        if self.secret:
            hashable_fields = ['app_id', 'module', 'stamp', 'nsecs', 'body']
            hashable = ''.join('{0}'.format(data[field]) for field in hashable_fields).encode('utf-8')
            data['signature'] = hmac.new(self.secret.encode('utf-8'), hashable, self.HMAC_DIGEST_ALGO).hexdigest()

        payload = json.dumps(data).encode('utf-8')

        if self.compression:
            payload = zlib.compress(payload)

        size = len(payload)
        return struct.pack(self.FORMAT_PROTO.format(size).encode('ascii'), size, self.flags, payload)

    def emit(self, record):
        '''Encodes and sends the messge over the network.'''

        if len(self.buffer) >= self.max_buffer_size:
            self.buffer.popleft() # Drop the oldest message to make room

        self.buffer.append(self._encode(record))
        self.send()

    def send(self):
        '''Attempts to create a network connection and send the data.'''

        if self.sock is None:
            self.createSocket()

        if not self.sock:
            return

        try:
            while self.buffer:
                data = self.buffer.popleft()

                # Detect if we can read and write to/from socket
                r, w, _ = select.select([self.sock], [self.sock], [], 0.25)

                # If select says we can't write, bail
                if self.sock not in w:
                    raise socket.error('Cannot write to socket.')

                # Normally, the server does not write anything to us. However,
                # if the server gracefully closed the socket, then we get a 
                # zero byte sequence here. Reading zero bytes means the other
                # side is down. Thus we can shut down now.
                if self.sock in r:
                    if not (self.sock.recv(1)):
                        raise socket.error('Detected a closed socket.')

                if self.use_stream:
                    self.sock.sendall(data)
                else:
                    self.sock.sendto(data, self.address)
        except socket.error:
            self.sock.close()
            self.sock = None
            self.buffer.appendleft(data) # Add the log message back to the queue

