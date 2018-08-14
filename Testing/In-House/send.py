import pika
import struct


def fullSend( sl, rg, serverIP = None, creds = None, xch = None, rtk = None):

    ##  This is probably redundant, but I fear it might be necessary    -Sam
    if not serverIP is None:
        ##  This doesn't seem to be the most accurate way to find a URL,
        ##  but at the same time, I can't imagine having too many different
        ##  URL's too have to choose from   -Sam
        if serverIP.contains('@'):
            params = pika.URLParameters(serverIP)       ##  Create parameters from URL
        else:
            ##  Create parameters from IP and credentials
            params = pika.ConnectionParameters(host = serverIP,
                                               port = 5672,
                                               virtual_host = '/',
                                               credentials = creds)
                                               
    
    connection = pika.BlockingConnection(params)        ##  Create connection from params
    channel = connection.channel()                      ##  Create channel from connection

    ##  Declare exchange using xch argument
    channel.exchange_declare(exchange = xch,
                             exchange_type = 'topic',
                             auto_delete = True)
    
    
    q = channel.queue_declare(exclusive = True)     ##  Declare random queue
    qName = q.method.queue                          ##  Get random queue's name

    ##  Bind queue to exhange xch using routing key rtk, from arguments
    channel.queue_bind(exchange = xch,
                       queue = qName,
                       routing_key = rtk)

    ##  Wrapped publish in a try-except block as an attempt
    ##  at a graceful exit from a Keyboard Interrupt.
    try:        ##  It will probably never actually happen, but it's here.
        channel.basic_publish(exchange = xch,                   ##  Over the exchange xch,
                              routing_key = rtk,                ##  using routing key rtk,
                              body = struct.pack('!id',sl,rg))  ##  publish, a message that
                                                                ##  contains speed limit and road grade
        print(' [x] %s Sent' % struct.pack('!id',sl,rg))        ##  Print the message
    except KeyboardInterrupt:
        exit()                                                  ##  Exeunt


