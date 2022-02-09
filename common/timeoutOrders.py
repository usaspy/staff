import time
import sqlalchemy
import json
from model.order import ORDER
from model.order import ORDER_PROCESS
from model.owner import VEHICLE
import datetime
from common import mq_message
from common.sysParam import RESERVE_TIME

#订单超时检测
def check(db):
    while True:
        #查询所有状态为“已预约=0”但超时的预约单
        ls = db.session.query(ORDER,VEHICLE).filter(ORDER.state == 0, sqlalchemy.func.TIMESTAMPDIFF(sqlalchemy.text('SECOND'), ORDER.created_at, datetime.datetime.now()) > RESERVE_TIME, VEHICLE.id == ORDER.vehicle_id).all()
        #将超时的预约单状态设为5，并记录到order_process表
        for order, _ in ls:
            db.session.query(ORDER).filter(ORDER.uuid == order.uuid).update({"state": 5,"updated_at": datetime.datetime.now()})
            order_process = ORDER_PROCESS(order_id=order.uuid, state=5, timestamp=datetime.datetime.now(),
                                          executor='sys',
                                          executor_type='sys')
            db.session.add(order_process)
        db.session.commit()

        for order, vehicle in ls:
            #生成消息message——超时通知
            message = json.dumps(
                {'message_type': 4, 'order_id': "%s" % order.uuid, 'receiver': "%s" % vehicle.owner_id})

            mq_message.message_publish(message)

        time.sleep(60)