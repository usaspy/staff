import pika
import config as cfg
import json

def syncTokenCache_publish(msg):
    cred = pika.PlainCredentials(cfg.MQ_USER, cfg.MQ_PASSWORD)
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=cfg.MQ_HOST, port=cfg.MQ_PORT, virtual_host='/', credentials=cred))

    channelx = conn.channel()

    channelx.exchange_declare(exchange="token_staff", exchange_type="fanout")

    channelx.basic_publish(exchange="token_staff", routing_key="", body=msg)

    conn.close()

def syncTokenCache_consume(TOKENS_CACHE):
    cred = pika.PlainCredentials(cfg.MQ_USER, cfg.MQ_PASSWORD)
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=cfg.MQ_HOST, port=cfg.MQ_PORT, virtual_host='/', credentials=cred))

    channelx = conn.channel()

    channelx.exchange_declare(exchange="token_staff", exchange_type="fanout")

    channelx.queue_declare(cfg.SYSTEM_ID, exclusive=True)

    channelx.queue_bind(exchange="token_staff", queue=cfg.SYSTEM_ID)

    def doit(channelx, methodx, v3, bodyx):
        try:
            msg = json.loads(bodyx.decode())
            if msg["SYSTEM_ID"] == cfg.SYSTEM_ID:
                print("yes i get it, but i don't do anything!")
                return #本机收到不处理
            else:
                if "ADD" in msg:
                    token = msg["ADD"]["key"]
                    info = msg["ADD"]["values"]
                    TOKENS_CACHE[token] = json.loads(info)
                if "DELETE" in msg:
                    TOKENS_CACHE.pop(msg["DELETE"]["key"], None)

            channelx.basic_ack(delivery_tag=methodx.delivery_tag)
        except Exception as ex:
            print(ex)
            print("远端TOKEN同步过程出错...")

    channelx.basic_consume(cfg.SYSTEM_ID, doit, auto_ack=False, )

    channelx.start_consuming()