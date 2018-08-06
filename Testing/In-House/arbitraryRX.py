#!/usr/bin/env python
import pika, os
import sys

# This is for CloudAMQP
url = 'amqp://cnplsytz:ST-2S7zCbeV9dknueCgJIzrCZpk0dUGW@termite.rmq.cloudamqp.com/cnplsytz'
params = pika.URLParameters(url)

# this is for our own server
# to set up server: https://goo.gl/P7abHc
# username and password must be setup before this will work
#credentials = pika.PlainCredentials('apsdev', 'dev123')
#serverip = '192.168.1.118'
#params = pika.ConnectionParameters(serverip,
#                                   5672,
#                                   '/',
#                                   credentials)
connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.exchange_declare(exchange='TestExchange',
                         exchange_type='topic',
                         auto_delete=True)

#channel.queue_declare(queue='myqueue')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='TestExchange',
                   queue=result.method.queue,
                   routing_key='TestRoute')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

print('[x] Waiting...')
channel.start_consuming()