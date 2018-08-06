import pika, os, sys

credentials = pika.PlainCredentials('aps-lab','aps-lab')
serverip = '141.219.205.25'
params=pika.ConnectionParameters(serverip,
                                 5672,
                                 '/',
                                 credentials)
connection=pika.BlockingConnection(params)

channel=connection.channel()
result=channel.queue_declare(exclusive=True)
queue_name=result.method.queue
message=' '.join(sys.argv[1:]) or "Hello!"
channel.basic_publish(exchange='cacc_test_exchange',
                      routing_key='cloud_cacc',
                      body=message)
print(" [x] Sent %r" % message)
connection.close()