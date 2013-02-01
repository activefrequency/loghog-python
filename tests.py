'''
This module contains unit test for the Python LogHog client.
'''

import unittest, logging, os, struct, zlib, hashlib, hmac, json
from loghog import LoghogHandler

class LoghogClientTest(unittest.TestCase):

    HEADER_FORMAT = '!LL'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    MSG_FORMAT_PROTO = '%ds'
    
    REQUIRED_FIELDS = ['version', 'stamp', 'nsecs', 'app_id', 'module', 'body', ]
    HASHABLE_FIELDS = ['app_id', 'module', 'stamp', 'nsecs', 'body']

    HMAC_DIGEST_ALGO = hashlib.md5

    def setUp(self):
        self.rec = logging.LogRecord('web.requests', logging.INFO, os.path.abspath(__file__), 10, 'test message', tuple(), None)
    
    def validate_msg(self, msg):
        '''Adapted from loghogd.processor.'''

        for field in self.REQUIRED_FIELDS:
            self.assertTrue(field in msg, 'Invalid message: "{}" is not in the message.'.format(field))

    def verify_signature(self, secret, msg):
        '''Adapted from loghogd.processor.'''

        if secret:
            self.assertTrue('signature' in msg, 'Security alert: message signature is required but not present')

            hashable = u''.join(unicode(msg[field]) for field in self.HASHABLE_FIELDS).encode('utf-8')
            signature = hmac.new(secret, hashable, self.HMAC_DIGEST_ALGO).hexdigest()

            self.assertEqual(signature, msg['signature'], "Message signature is invalid.")

    def parse_message(self, data):
        '''Adapted from loghogd.processor.'''

        msg = json.loads(data)

        self.validate_msg(msg)

        return msg

    def check_message_content(self, msg):
        self.assertEqual(msg['app_id'], 'test-app')
        self.assertEqual(msg['module'], 'web.requests')
        self.assertEqual(msg['body'], 'test message')

    def unpack_payload(self, data):
        size, flags = struct.unpack(self.HEADER_FORMAT, data[:self.HEADER_SIZE])
        return struct.unpack(self.MSG_FORMAT_PROTO % size, data[self.HEADER_SIZE:size+self.HEADER_SIZE])[0]

    def test_encode(self):
        handler = LoghogHandler('test-app')
        data = handler._encode(self.rec)

        payload = self.unpack_payload(data)
        msg = self.parse_message(payload)
        
        self.check_message_content(msg)

    def test_encode_with_zlib(self):
        handler = LoghogHandler('test-app', compression=True)
        data = handler._encode(self.rec)

        payload = self.unpack_payload(data)
        payload = zlib.decompress(payload)
        msg = self.parse_message(payload)

        self.check_message_content(msg)

    def test_encode_secret(self):
        handler = LoghogHandler('test-app', secret='qqq123')
        data = handler._encode(self.rec)

        payload = self.unpack_payload(data)
        msg = self.parse_message(payload)

        self.check_message_content(msg)

        self.verify_signature('qqq123', msg)

tests_all = unittest.TestLoader().loadTestsFromTestCase(LoghogClientTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(tests_all)