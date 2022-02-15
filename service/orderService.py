import datetime

from api import db
from model.order import ORDER
from model.order import ORDER_PROCESS
from model.owner import VEHICLE
from model.owner import OWNER_LAST_ORDER
from model.parking import PARKING
from model.parking import PARKING_RULES
from model.parking import PARKING_PROCESS
from model.parking import PARKING_GATES
from model.order import BILL

from common import tools

'''
当车辆入场时，车主扫描入场码 ，状态变更为==2..待入场（已扫码）
1.此时已经开始计费
2.后续需门卫确认（go_in_confirm），并修改订单状态为order_state=1
'''
def go_in_confirm(staff_id, order_id):
    try:
        db.session.query(PARKING_PROCESS).filter(PARKING_PROCESS.order_id == order_id).update(
            {"in_confirm": 1})

        db.session.query(ORDER).filter(ORDER.uuid == order_id).update(
            {"state": 1, "updated_at": datetime.datetime.now()})

        order_process = ORDER_PROCESS(order_id=order_id, state=1, timestamp=datetime.datetime.now(),
                                          executor=staff_id,
                                          executor_type='staff')
        db.session.add(order_process)
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True