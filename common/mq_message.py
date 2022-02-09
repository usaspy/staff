from model.message import MESSAGE
from model.parking import PARKING_PROCESS
from model.parking import PARKING
from model.order import ORDER
from model.order import BILL
from model.owner import VEHICLE
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

def write_message_2(order_id, receiver, receive_type=1):
    ord = db.session.query(ORDER).filter(ORDER.uuid == order_id).first()
    veh = db.session.query(VEHICLE).filter(VEHICLE.id == ord.vehicle_id).first()
    pp = db.session.query(PARKING_PROCESS).filter(PARKING_PROCESS.order_id == order_id).first()
    p = db.session.query(PARKING).filter(PARKING.uuid == ord.parking_id).first()
    vehicle_number = veh.vehicle_number
    in_at = pp.in_at
    parking_name = p.name

    message_body = "您得爱车[%s]于[%s]入场停放在[%s],本停车场非全天可停，请记得17点之前开走哦，避免产生额外得费用"%(vehicle_number, str(in_at), parking_name)

    message = MESSAGE(message_type=2, message_body=message_body, receiver=receiver,receive_type=receive_type,
                      created_at=datetime.datetime.now())
    db.session.add(message)
    db.session.commit()

def write_message_3(order_id, receiver, receive_type=1):
    ord = db.session.query(ORDER).filter(ORDER.uuid == order_id).first()
    veh = db.session.query(VEHICLE).filter(VEHICLE.id == ord.vehicle_id).first()
    pp = db.session.query(PARKING_PROCESS).filter(PARKING_PROCESS.order_id == order_id).first()
    p = db.session.query(PARKING).filter(PARKING.uuid == ord.parking_id).first()
    bi = db.session.query(BILL).filter(BILL.order_id == order_id).first()

    vehicle_number = veh.vehicle_number
    duration = str(datetime.timedelta(seconds=bi.duration))
    fee_1 = bi.fee_1
    end_time = pp.out_at
    parking_name = p.name

    message_body = "您的爱车[%s]已于[%s]离开[%s],共计停放时长[%s],本次实缴费[%s]元"%(vehicle_number,end_time,parking_name,duration, str(fee_1))

    message = MESSAGE(message_type=3, message_body=message_body, receiver=receiver,receive_type=receive_type,
                      created_at=datetime.datetime.now())
    db.session.add(message)
    db.session.commit()

def write_message_4(order_id, receiver, receive_type=1):
    ord = db.session.query(ORDER).filter(ORDER.uuid == order_id).first()
    p = db.session.query(PARKING).filter(PARKING.uuid == ord.parking_id).first()
    parking_name = p.name

    message_body = "您在停车场[%s]预约的停车位快到时间了！"%(parking_name)

    message = MESSAGE(message_type=4, message_body=message_body, receiver=receiver,receive_type=receive_type,
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
            elif message_type == 2: #车辆入场通知
                order_id = msg['order_id']
                receiver = msg['receiver']
                write_message_2(order_id, receiver)
            elif message_type == 3: #缴费离场通知
                order_id = msg['order_id']
                receiver = msg['receiver']
                write_message_3(order_id, receiver)
            elif message_type == 4: #超时通知
                order_id = msg['order_id']
                receiver = msg['receiver']
                write_message_4(order_id, receiver)
            else:
                print("消息格式不正确[%s]"% msg)
        except Exception as ex:
            print(ex)
        finally:
            channelx.basic_ack(delivery_tag=methodx.delivery_tag)

    channelx.basic_consume('message',doit)

    channelx.start_consuming()