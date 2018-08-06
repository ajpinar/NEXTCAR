#!/usr/bin/env python
import pika, os
import sys

# This is for CloudAMQP
url = 'amqp://cnplsytz:ST-2S7zCbeV9dknueCgJIzrCZpk0dUGW@termite.rmq.cloudamqp.com/cnplsytz'
params = pika.URLParameters(url)

# this is for our own server
# to set up server: https://goo.gl/P7abHc
# username and password must be setup before this will work
#credentials = pika.PlainCredentials('beta1', 'beta1')
#serverip = '166.152.103.250'
#serverip = '35.54.5.207'
#serverip = '141.219.181.216' #Kuilin's cloud IP
#params = pika.ConnectionParameters(serverip,
#                                   5672,
#                                   'StationTx',
#                                   credentials)
connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.exchange_declare(exchange='TestExchange',
                         exchange_type='topic',
                         auto_delete=True)

#channel.queue_declare(queue='myqueue')

message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(exchange='TestExchange',
                      routing_key='TestRoute',
                      body=message)

print(" [x] Sent %r" % message)
connection.close()