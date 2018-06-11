# -*- coding: utf-8 -*-
#
# ITerativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 2018 ITerativ GmbH. All rights reserved.
#
# Created on 06.06.18
# @author: chrigu <christian.cueni@iterativ.ch>

import pika
import json
from detector import find_postits


def init_service():
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('127.0.0.1',
                                           5672,
                                           '/',
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)
    channel.queue_declare(queue='update_queue', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')


    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(" [x] Received %r" % data)
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

        def update_callback(message):

            update_data = {'message': message, 'client_id': data['client_id']}

            channel.basic_publish(exchange='',
                                  routing_key='update_queue',
                                  body=json.dumps(update_data),
                                  properties=pika.BasicProperties(
                                      delivery_mode=2,  # make message persistent
                                  ))

        postits = find_postits(data['image_url'], update_callback)
        update_callback(postits)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue='task_queue')

    channel.start_consuming()


if __name__ == "__main__":
    # execute only if run as a script
    init_service()


# def update_callback(channel, client_id):
#
#     def callback(message):
#
#         update_data = {'message': message, 'client_id': data['client_id']}
#
#         channel.basic_publish(exchange='',
#                               routing_key='update_queue',
#                               body=json.dumps(message),
#                               properties=pika.BasicProperties(
#                                   delivery_mode=2,  # make message persistent
#                               ))