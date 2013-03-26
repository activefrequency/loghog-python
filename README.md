# LogHog Python Client

This is a Python client for the LogHog log management server (https://github.com/activefrequency/loghogd).
It implements a drop-in LogHandler for the Python logging framework.

Python's built-in logging using the FileHandler family does not prevent multiple processes from
writing to the same log file (often over each other). This is a typical issue with Django running
under apache2.

LogHog solves this by having all the processes log to a central server. The LogHog server takes care
of writing the messages one at a time, rotating and compressing files, deleting old log files, etc.

You can think of LogHog as a very secure and user friendly syslog + logrotate in one package.

## When to use LogHog

There are many situations when LogHog will come in handy. Here are some examples:

 * Your application runs on multiple servers and you want the data in one place
 * You have a multi-process application and you want every process to write to a single log file
 * You want to offload your logging to a different server
 * Your application writes logs

In fact there is almost no reason *not to* use LogHog. It is fast, simple,
secure, and it stays out of your way.

## Quickstart

**Step 1**: Install the LogHog server (loghogd). If you are using Ubuntu, run the following:

    sudo add-apt-repository ppa:activefrequency/ppa
    sudo apt-get update
    sudo apt-get install loghogd

Note: if you are running an older (e.g.: 10.04) release of Ubuntu, you may need to first install
the *python-software-properties* package to get the `add-apt-repository` command.

If you are using Debian, run the following:

    echo 'deb http://ppa.launchpad.net/activefrequency/ppa/ubuntu lucid main' | sudo tee -a /etc/apt/sources.list.d/99-loghogd.list
    echo 'deb-src http://ppa.launchpad.net/activefrequency/ppa/ubuntu lucid main' | sudo tee -a /etc/apt/sources.list.d/99-loghogd.list
    
    gpg --keyserver hkp://keyserver.ubuntu.com/ --recv-keys F96CE604
    gpg -a --export F96CE604 | sudo apt-key add -
    
    sudo apt-get update
    sudo apt-get install loghogd

**Step 2**: List your application in the LogHog logging facilities. Put the following in */etc/loghogd/facilities.conf*:

    [my-first-app]
    rotate = 0 0 * * *
    backup_count = 14

And reload loghog:

    sudo /etc/init.d/loghogd reload

**Step 3**: Install LogHog Python Client (this codebase):

    pip install loghog

**Step 4**: Enable logging in your application. Add the following to your app startup:

    import logging
    from loghog import LoghogHandler

    logger = logging.getLogger()

    handler = LoghogHandler('my-first-app')

    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.info('Hello world!')

Start your app and look at /var/log/loghogd/my-first-app/ to see your application's log."

For more extensive configuration, see the examples directory.

## Configuration

LogHog can do a lot of things for you. It can rotate files based on a schedule or file size,
encrypt traffic between your application and the server using SSL/TLS, sign messages you send
to the server, etc. Take a look a examples/kitchen-sink.py for an example of the usage of
all of these.

Here are some highlights:

    # Specify a remote host
    handler = LoghogHandler('my-app', host='example.com', port=5566)
    
    # Use UDP
    handler = LoghogHandler('my-app', stream=False)
    
    # Use zlib compression to save on bandwidth
    handler = LoghogHandler('my-app', compression=True)
    
    # Sign messages using HMAC
    handler = LoghogHandler('my-app', secret='12345')
    
    # Use a different hostname than reported by the hostname(1) command
    handler = LoghogHandler('my-app', hostname='foo')
    
    # Tell LoghogHandler that you want it to print connection errors to stdout
    # NOTE: this does nothing if stream=False
    handler = LoghogHandler('my-app', print_debug=True)
    
    # Use SSL
    ssl_info = {
        'pemfile': '/PATH/TO/CLIENT.pem',
        'cacert': '/etc/loghogd/certs/loghogd-ca.cert',
    }
    
    handler = LoghogHandler('my-app', ssl_info=ssl_info)

For configuring the LogHog server, see https://github.com/activefrequency/loghogd.

## License

This code is released under the Apache 2 license. See *LICENSE* for more details.

## Contributing

Feel free to fork this code and submit pull requests. If you are new to GitHub,
feel free to send patches via email to igor@activefrequency.com.

## Credits

Credit goes to Active Frequency, LLC (http://activefrequency.com/) for sponsoring this project.


