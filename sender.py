#!/usr/bin/env python
import pika
import json

queue = 'update_queue'

credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters('127.0.0.1',
                                       5672,
                                       '/',
                                       credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue=queue, durable=True)

message = {'url': 'some', 'clientId': 12}
channel.basic_publish(exchange='',
                      routing_key=queue,
                      body=json.dumps(message),
                      properties=pika.BasicProperties(
                         delivery_mode=2, # make message persistent
                      ))
print(" [x] Sent %r" % message)
connection.close()