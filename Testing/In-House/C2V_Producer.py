#################################################
#   Author: Sam Celani                          #
#   Date:   5/18/18                             #
#                                               #
#   File:   C2V_Producer.py                     #
#                                               #
#   Description:                                #
#                                               #
#                                               #
#################################################


#
#
#   USAGE
#       py C2V_Producer.py local
#           - sends messages from localhost
#       py C2V_Producer.py
#           - sends messages from Kuilin's server
#
#

import pika
import time
import datetime
import configInit
import sys
import struct

if len(sys.argv) is 2:
    datum = configInit.init(True, False)
else:
    datum = configInit.init(True, True)




dataFormat = '!Hdddiiddddddddddi'
message = struct.pack(dataFormat,
                      123,
                      0.1,
                      1.6,
                      5,
                      16,
                      5,
                      35,
                      35,
                      35,
                      35,
                      35,
                      25,
                      25,
                      25,
                      25,
                      25,
                      1)

data2 = '!id'
mess = struct.pack(data2,20,10.5)
#print(sys.argv[1])
print(datum)
print(datum[3][0])

SERVERIP = datum[0][0]
if len(sys.argv) is 1:
    CREDENTIALS = pika.PlainCredentials(datum[1][0], datum[1][1])
    print(CREDENTIALS)

UNIQUE_ROUTING_KEY = datum[2][0]
EXCHANGE_NAME = datum[3][0]


while True:
    if len(sys.argv) is 2:
        #connection = pika.BlockingConnection(pika.ConnectionParameters(host = '127.0.0.1'))
        # This is for CloudAMQP
        url = 'amqp://cnplsytz:ST-2S7zCbeV9dknueCgJIzrCZpk0dUGW@termite.rmq.cloudamqp.com/cnplsytz'
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
    else:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host = SERVERIP,
                                                                       port = 5672,
                                                                       virtual_host = '/',
                                                                       credentials = CREDENTIALS))
    
    channel = connection.channel()

    channel.exchange_declare(exchange = EXCHANGE_NAME,
                             exchange_type = 'topic')

    q = channel.queue_declare(exclusive = True)
    qName = q.method.queue

    channel.queue_bind(exchange = EXCHANGE_NAME,
                       queue = qName,
                       routing_key = UNIQUE_ROUTING_KEY)


    try:
        channel.basic_publish(exchange = EXCHANGE_NAME,
                              routing_key = UNIQUE_ROUTING_KEY,
                              body = mess)
        print(' [x] %s Sent' % mess)
        time.sleep(5)
    except KeyboardInterrupt:
        exit()
