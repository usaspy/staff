import datetime

from api import db
from model.owner import *
from model.parking import *
from model.order import *
from model.message import MESSAGE
from common import tools

#增加车主常用车辆
def addVehicle(owner_id, vehicle_number, vehicle_info= ""):
    try:
        exist = db.session.query(VEHICLE).filter(VEHICLE.owner_id== owner_id,VEHICLE.vehicle_number==vehicle_number,VEHICLE.deleted_at == None).first()
        if exist == None:
            vehicle = VEHICLE(owner_id= owner_id, vehicle_number= vehicle_number, vehicle_info= vehicle_info , created_at= datetime.datetime.now())
            db.session.add(vehicle)
            db.session.commit()
        else:
            return False
    except Exception as ex:
        print(ex)
        return False

    return True

#刷新车辆使用时间
def updateVehicleUsedTime(vehicle_id):
    try:
        db.session.query(VEHICLE).filter(VEHICLE.id== vehicle_id).update({"used_at": datetime.datetime.now()})
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True

#查询车主名下得车辆信息
def getVehiclesByOwnerId(owner_id):
    result = db.session.query(VEHICLE).filter(VEHICLE.owner_id == owner_id, VEHICLE.deleted_at == None).order_by(VEHICLE.used_at.desc()).limit(3)
    vehicles = []
    for vehicle in result:
        vehicles.append({"vehicle_id":vehicle.id,"vehicle_number":vehicle.vehicle_number,"owner_id":vehicle.owner_id,"vehicle_info":vehicle.vehicle_info})
    return vehicles

#删除车主常用车
def deleteVehicle(id):
    try:
        exist = db.session.query(ORDER).filter(ORDER.vehicle_id == id,ORDER.state.in_([0,1,5])).first()
        if exist == None:
            db.session.query(VEHICLE).filter(VEHICLE.id== id).update({"deleted_at": datetime.datetime.now()})
            db.session.commit()
        else:
            return False
    except Exception as ex:
        print(ex)
        return False

    return True


#更新微信用户的手机号码
def updatePhoneNumber(phonenumber, owner_id):
    try:
        db.session.query(OWNER_INFO).filter(OWNER_INFO.owner_id== owner_id).update({"wx_phone": phonenumber})
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True

def updateAvatarNickname(avatarUrl, nickName, owner_id):
    try:
        db.session.query(OWNER_INFO).filter(OWNER_INFO.owner_id== owner_id).update({"wx_avatar_url": avatarUrl,"wx_nickname":nickName})
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True

#加入停车场收藏
def addFavorite(parking_id, owner_id):
    try:
        exist = db.session.query(OWNER_PARKING).filter(OWNER_PARKING.owner_id == owner_id,
                                                       OWNER_PARKING.parking_id == parking_id,
                                                       OWNER_PARKING.deleted_at == None).first()
        if exist == None:
            owner_parking = OWNER_PARKING(owner_id=owner_id, parking_id=parking_id, created_at=datetime.datetime.now())
            db.session.add(owner_parking)
            db.session.commit()
        else:
            return False
    except Exception as ex:
        print(ex)
        return False

    return True

#移出停车场收藏
def delFavorite(ids):
    try:
        for id in ids:
            db.session.query(OWNER_PARKING).filter(OWNER_PARKING.id == id).update({"deleted_at": datetime.datetime.now()})

        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True

#查询车主收藏得停车场
def getFavoriteByOwnerId(owner_id):
    result = db.session.query(OWNER_PARKING, PARKING).filter(OWNER_PARKING.parking_id == PARKING.uuid, OWNER_PARKING.owner_id == owner_id, OWNER_PARKING.deleted_at == None).all()
    favorites = []
    for owner_parking, parking in result:
        favorites.append({"owner_parking_id":owner_parking.id, "uuid":parking.uuid,"parking_name":parking.name,"address":parking.address,"service_time":parking.service_time,"service_kind":parking.service_kind,"tag":parking.tag,"star":parking.star})

    return favorites

#查询车主当前预约中的订单
def getLastOrderByOwnerId(owner_id):
    rs = db.session.query(OWNER_LAST_ORDER.the_last_order).filter(OWNER_LAST_ORDER.owner_id == owner_id).first()

    if rs:
        return rs[0]
    return None

#查询用户信息
def getOwnerInfo(owner_id):
    owner_info = db.session.query(OWNER_INFO).filter(OWNER_INFO.owner_id == owner_id).first()

    return owner_info

#查询车主得预约记录
def getOwnerOrders(owner_id):
    result = db.session.query(ORDER,VEHICLE,PARKING).filter(ORDER.vehicle_id == VEHICLE.id, PARKING.uuid == ORDER.parking_id,VEHICLE.owner_id == owner_id).order_by(ORDER.created_at.desc()).all()
    my_orders = []
    for order, vehicle,parking in result:
        my_orders.append({"parking_name":parking.name,"parking_id": parking.uuid, "parking_address":parking.address,"order_create_at":order.created_at,"vehicle_number":vehicle.vehicle_number,"order_state":order.state,"order_id":order.uuid})

    return my_orders

#查询车主得缴费记录
def getOwnerBills(owner_id):
    result = db.session.query(ORDER,VEHICLE,PARKING,BILL).filter(ORDER.vehicle_id == VEHICLE.id, PARKING.uuid == ORDER.parking_id,ORDER.uuid == BILL.order_id,VEHICLE.owner_id == owner_id,ORDER.state ==3).order_by(ORDER.created_at.desc()).all()
    my_bills = []
    for order, vehicle,parking,bill in result:
        my_bills.append({"parking_name":parking.name,"parking_address":parking.address,"order_id":order.uuid,"vehicle_number":vehicle.vehicle_number,"fee_1":bill.fee_1,"duration":bill.duration,"start_time":bill.start_time,"end_time":bill.end_time,"invoice_id":bill.invoice_id,"bill_id":bill.id})

    return my_bills


def list_messages(owner_id):
    result = db.session.query(MESSAGE).filter(MESSAGE.receiver == owner_id, MESSAGE.deleted_at == None).order_by(
        MESSAGE.created_at.desc()).limit(50)
    return result

def list_messages_no_read(owner_id):
    result = db.session.query(MESSAGE).filter(MESSAGE.receiver == owner_id, MESSAGE.deleted_at == None, MESSAGE.read_at == None).order_by(
        MESSAGE.created_at.desc()).count()
    return result

def show_message(message_id):
    message = db.session.query(MESSAGE).filter(MESSAGE.id == message_id).first()
    return message

def read_all_messages(owner_id):
    try:
        db.session.query(MESSAGE).filter(MESSAGE.receiver == owner_id, MESSAGE.deleted_at == None).update({"read_at": datetime.datetime.now()})
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True


def list_invoices(owner_id):
    result = db.session.query(INVOICE).filter(INVOICE.owner_id == owner_id).order_by(
        INVOICE.created_at.desc()).all()
    return result


def create_invoices(owner_id,bill_ids, invoice, receiver):
    try:
        invoice_uuid = tools.generateUUID()
        for bill_id in bill_ids:
            db.session.query(BILL).filter(BILL.id == bill_id).update({"invoice_id": invoice_uuid})

        invoice = INVOICE(uuid=invoice_uuid, invoice_info=invoice, receiver_info=receiver, owner_id=owner_id, created_at=datetime.datetime.now())
        db.session.add(invoice)
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True


def order_evaluation(order_id, owner_id, parking_id, parking_star, parking_evaluation):
    try:
        evaluation = EVALUATION(parking_id=parking_id, owner_id=owner_id, order_id=order_id, parking_star=parking_star, parking_evaluation=parking_evaluation, created_at=datetime.datetime.now())
        db.session.add(evaluation)
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True

#查询车主订单评价
def getOrderEvaluation(order_id):
    result = db.session.query(EVALUATION).filter(EVALUATION.order_id == order_id).first()

    return result