import pika
import struct


def fullSend( sl, rg ):
    
    url = 'amqp://cnplsytz:ST-2S7zCbeV9dknueCgJIzrCZpk0dUGW@termite.rmq.cloudamqp.com/cnplsytz'
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)

    EXCHANGE_NAME = 'cacc_test_exchange'    # MIGHT BE 'aps_xchg'
    UNIQUE_ROUTING_KEY = 'controller_1'     # MIGHT BE 'controller_1', 'controller_2', 'vehicle_1'

    channel = connection.channel()

    channel.exchange_declare(exchange = EXCHANGE_NAME,
                             exchange_type = 'topic', #IN CASE OF AUTO_DELETE ERROR
                             auto_delete = True)
    
    q = channel.queue_declare(exclusive = True)
    qName = q.method.queue

    channel.queue_bind(exchange = EXCHANGE_NAME,
                       queue = qName,
                       routing_key = UNIQUE_ROUTING_KEY)

    try:
        channel.basic_publish(exchange = EXCHANGE_NAME,
                              routing_key = UNIQUE_ROUTING_KEY,
                              body = struct.pack('!id',sl,rg))
        print(' [x] %s Sent' % struct.pack('!id',sl,rg))
    except KeyboardInterrupt:
        exit()


