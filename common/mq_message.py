from model.message import MESSAGE
import datetime
from api import db
import pika
import config as cfg
import base64
import json

def write_message_1(message_body, receiver, receive_type=1):
    message = MESSAGE(message_type=1, message_body=message_body, receiver=receiver,receive_type=receive_type,
                      created_at=datetime.datetime.now())
    db.session.add(message)
    db.session.commit()

def message_publish(msg):
    cred = pika.PlainCredentials(cfg.MQ_USER, cfg.MQ_PASSWORD)
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=cfg.MQ_HOST, port=cfg.MQ_PORT, virtual_host='/', credentials=cred))

    channelx = conn.channel()

    channelx.queue_declare(queue="message",durable=True)

    channelx.basic_publish(exchange="", routing_key="message", body=msg)

    conn.close()

def message_consume():
    cred = pika.PlainCredentials(cfg.MQ_USER, cfg.MQ_PASSWORD)
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=cfg.MQ_HOST, port=cfg.MQ_PORT, virtual_host='/', credentials=cred))

    channelx = conn.channel()

    channelx.queue_declare(queue="message", durable=True)

    def doit(channelx, methodx, v3, bodyx):
        try:
            msg = json.loads(bodyx.decode())
            message_type = msg['message_type']
            if message_type == 1:  #系统通知
                message_body = msg['message_body']
                receiver = msg['receiver']
                write_message_1(message_body, receiver)
            else:
                print("消息格式不正确[%s]"% msg)
        except Exception as ex:
            print(ex)
        finally:
            channelx.basic_ack(delivery_tag=methodx.delivery_tag)

    channelx.basic_consume('message',doit)

    channelx.start_consuming()