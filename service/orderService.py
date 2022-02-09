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
from common import pay

from common import tools

def getOrderByOrderId(uuid):
    try:
        order_info = db.session.query(ORDER).filter(ORDER.uuid== uuid).first()
        vehicle_info = db.session.query(VEHICLE).filter(VEHICLE.id== order_info.vehicle_id).first()
        order_process_infos = db.session.query(ORDER_PROCESS).filter(ORDER_PROCESS.order_id== uuid).order_by(ORDER_PROCESS.timestamp.desc()).all()
        parking_info,parking_rule_info  = db.session.query(PARKING,PARKING_RULES).filter(PARKING.uuid== order_info.parking_id, PARKING.uuid== PARKING_RULES.parking_id).first()
        parking_process = db.session.query(PARKING_PROCESS).filter(PARKING_PROCESS.order_id == uuid).first()

    except Exception as ex:
        print(ex)
        return None,None,None,None,None,None

    return order_info, order_process_infos, vehicle_info, parking_info,parking_rule_info,parking_process


def createOrder(owner_id, vehicle_number, parking_id, state):
    try:
        uuid = tools.generateUUID()
        #查询该停车场得计费规则
        rule = db.session.query(PARKING_RULES).filter(PARKING_RULES.parking_id == parking_id, PARKING_RULES.deleted_at == None).first()

        #刷新车牌使用情况
        rs = db.session.query(VEHICLE.id).filter(VEHICLE.owner_id == owner_id, VEHICLE.vehicle_number == vehicle_number, VEHICLE.deleted_at == None).first()
        if rs:
            db.session.query(VEHICLE).filter(VEHICLE.id == rs[0]).update(
                {"used_at": datetime.datetime.now()})
        else:
            vehicle = VEHICLE(owner_id= owner_id, vehicle_number= vehicle_number, vehicle_info= None , created_at= datetime.datetime.now(), used_at= datetime.datetime.now())
            db.session.add(vehicle)
            rs = db.session.query(VEHICLE.id).filter(VEHICLE.owner_id == owner_id, VEHICLE.vehicle_number == vehicle_number, VEHICLE.deleted_at == None).first()
        #创建新订单
        order = ORDER(uuid= uuid, vehicle_id= rs[0], parking_id= parking_id, rule_id= rule.id, state= state,
                                created_at=datetime.datetime.now())
        order_process = ORDER_PROCESS(order_id= uuid, state= state, timestamp= datetime.datetime.now(), executor= owner_id, executor_type= 'owner')

        #在途订单绑定到用户
        owner_last_order = OWNER_LAST_ORDER(owner_id= owner_id, the_last_order= uuid)

        db.session.add(order)
        db.session.add(order_process)
        db.session.add(owner_last_order)
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True

'''
当车辆入场时，用户扫描二维码 后完成入场
1.记录
'''
def go_in(owner_id, order_id, qr):
    try:
        parking_id = qr.split("_")[0]
        gate_id = qr.split("_")[1]

        gate = db.session.query(PARKING_GATES).filter(PARKING_GATES.id == gate_id, PARKING_GATES.parking_id == parking_id).first()
        if gate and gate.category == 1: #这个门存在,并且是入口
            parking_process = PARKING_PROCESS(parking_id=parking_id, in_gate_id=gate_id, vehicle_id=None,
                                              in_at=datetime.datetime.now(), order_id=order_id)

            db.session.query(ORDER).filter(ORDER.uuid == order_id).update(
                {"state": 1, "updated_at": datetime.datetime.now()})

            order_process = ORDER_PROCESS(order_id=order_id, state=1, timestamp=datetime.datetime.now(),
                                          executor=owner_id,
                                          executor_type='owner')
            db.session.add(parking_process)
            db.session.add(order_process)
            db.session.commit()
        else:
            return False
    except Exception as ex:
        print(ex)
        return False

    return True


'''
当车辆离场时，用户打开小程序，显示当前停放的时间和停车费用，用户点击“扫码离场”，扫描物业展示的出场二维码，点击确认后完成缴费和离场动作
'''
def go_out(owner_id, order_id, qr):
    try:
        parking_id = qr.split("_")[0]
        gate_id = qr.split("_")[1]

        gate = db.session.query(PARKING_GATES).filter(PARKING_GATES.id == gate_id, PARKING_GATES.parking_id == parking_id).first()
        if gate and gate.category == 2: #这个门存在,并且是出口
            # 计算费用，生成账单
            bill = __generate_bill(order_id)
            # 调用缴费接口
            pay_completed = __pay_ok(bill)
            if pay_completed:
                db.session.query(PARKING_PROCESS).filter(PARKING_PROCESS.parking_id == parking_id,PARKING_PROCESS.vehicle_id==None, PARKING_PROCESS.order_id == order_id).update(
                    {"out_gate_id": gate_id, "out_at": datetime.datetime.now()})

                db.session.query(ORDER).filter(ORDER.uuid == order_id).update(
                    {"state": 3, "updated_at": datetime.datetime.now()})

                order_process = ORDER_PROCESS(order_id=order_id, state=3, timestamp=datetime.datetime.now(),
                                              executor=owner_id,
                                              executor_type='owner')

                db.session.query(OWNER_LAST_ORDER).filter(OWNER_LAST_ORDER.owner_id==owner_id, OWNER_LAST_ORDER.the_last_order==order_id).delete()
                db.session.add(order_process)
                db.session.add(bill)
                db.session.commit()
            else:
                return False
        else:
            return False
    except Exception as ex:
        print(ex)
        return False

    return True

'''
取消预约单
'''
def cancel(owner_id, order_id):
    try:
        db.session.query(ORDER).filter(ORDER.uuid == order_id).update(
            {"state": 9, "updated_at": datetime.datetime.now()})

        order_process = ORDER_PROCESS(order_id=order_id, state=9, timestamp=datetime.datetime.now(),
                                      executor=owner_id,
                                      executor_type='owner')
        db.session.query(OWNER_LAST_ORDER).filter(OWNER_LAST_ORDER.owner_id==owner_id, OWNER_LAST_ORDER.the_last_order==order_id).delete()
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
    order_process = db.session.query(ORDER_PROCESS).filter(ORDER_PROCESS.order_id == order_id, ORDER_PROCESS.state.in_([1])).first()
    template_id = rule.template_id  #规则模板
    vars = rule.vars  #规则参数
    rule_id = rule.id #规则id
    go_in_time = order_process.timestamp
    now_time=  datetime.datetime.now()
    fee_1 = pay.calculate_fee(template_id,vars,go_in_time,now_time)

    bill = BILL()
    bill.order_id = order_id
    bill.start_time = go_in_time.strftime("%Y-%m-%d %H:%M:%S")
    bill.end_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
    bill.duration = (now_time - go_in_time).total_seconds()
    bill.rule_id = rule_id
    bill.fee_mode = 1
    bill.fee_1 = fee_1

    return bill



def __pay_ok(bill):
    print(bill)
    return True

#查询车主最近一次的预约单
def getLatestOrder(owner_id):
    _, latest_order,parking = db.session.query(VEHICLE,ORDER,PARKING).filter(VEHICLE.owner_id == owner_id, VEHICLE.id == ORDER.vehicle_id, PARKING.uuid == ORDER.parking_id).order_by(ORDER.created_at.desc()).first()

    return latest_order, parking