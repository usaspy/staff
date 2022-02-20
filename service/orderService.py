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

from pay import pay
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

        return True
    except Exception as ex:
        print(ex)

    return False


'''
当车辆离场时，如果车主手机没电了，需要线下缴费，并由门岗端点击“离场放行”
1.此时显示要交的费用
2.后续需门卫确认（go_in_confirm），并修改订单状态为order_state=1
'''
def go_out_pay_manual(order_id):
    try:
        # 1.计算费用，生成账单
        bill = __generate_bill(order_id)
        # 先删掉旧的账单（如果存在）
        db.session.query(BILL).filter(BILL.order_id == order_id).delete()
        # 生成新的账单
        db.session.add(bill)
        db.session.commit()

        _, vehicle = db.session.query(ORDER,VEHICLE).filter(ORDER.uuid == order_id, ORDER.vehicle_id == VEHICLE.id).first()

        return bill, vehicle
    except Exception as ex:
        print(ex)
    return None,None

'''
当车辆离场时，如果车主手机没电了，需要线下缴费，并由门岗端点击“离场放行”
1.此时已经开始计费
2.后续需门卫确认（go_in_confirm），并修改订单状态为order_state=1
'''
def go_out_confirm(staff_id, order_id):
    try:
        db.session.query(PARKING_PROCESS).filter(PARKING_PROCESS.order_id == order_id).update(
            {"out_confirm": 1})

        db.session.query(ORDER).filter(ORDER.uuid == order_id).update(
            {"state": 3, "updated_at": datetime.datetime.now()})

        order_process = ORDER_PROCESS(order_id=order_id, state=3, timestamp=datetime.datetime.now(),
                                          executor=staff_id,
                                          executor_type='staff')

        db.session.query(BILL).filter(BILL.order_id == order_id).update(
            {"pay_state": 1, "pay_at": datetime.datetime.now()})

        db.session.query(OWNER_LAST_ORDER).filter(OWNER_LAST_ORDER.the_last_order == order_id).delete()
        db.session.add(order_process)
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True


##计算费用，生成账单
def __generate_bill(order_id):
    order = db.session.query(ORDER).filter(ORDER.uuid == order_id).first()
    rule = db.session.query(PARKING_RULES).filter(PARKING_RULES.parking_id == order.parking_id).first()
    #order_process = db.session.query(ORDER_PROCESS).filter(ORDER_PROCESS.order_id == order_id, ORDER_PROCESS.state.in_([1])).first()
    parking_process = db.session.query(PARKING_PROCESS).filter(PARKING_PROCESS.order_id == order_id).first() #注意：不管门岗是否确认：in_confirm=1,都开始计算费用
    template_id = rule.template_id  #规则模板
    vars = rule.vars  #规则参数
    rule_id = rule.id #规则id
    go_in_time = parking_process.in_at
    now_time = datetime.datetime.now()
    fee_1 = pay.calculate_fee(template_id, vars, go_in_time, now_time)

    bill = BILL()
    bill.order_id = order_id
    bill.start_time = go_in_time.strftime("%Y-%m-%d %H:%M:%S")
    bill.end_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
    bill.duration = (now_time - go_in_time).total_seconds()
    bill.rule_id = rule_id
    bill.fee_mode = 1
    bill.fee_1 = fee_1
    bill.pay_state = 0  #待支付
    bill.created_at = now_time

    return bill
