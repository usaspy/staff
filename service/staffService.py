import datetime

from api import db
from model.pmc import *
from model.parking import *
from model.owner import *
from model.order import *
from model.message import MESSAGE
from common import tools

#更新员工的手机号码
def updatePhoneNumber(phonenumber, staff_id):
    try:
        db.session.query(STAFF_INFO).filter(STAFF_INFO.staff_id== staff_id).update({"wx_phone": phonenumber})
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True

def updateAvatarNickname(avatarUrl, nickName, staff_id):
    try:
        db.session.query(STAFF_INFO).filter(STAFF_INFO.staff_id== staff_id).update({"wx_avatar_url": avatarUrl,"wx_nickname":nickName})
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True

def getParkingInfo(parking_id):
    parking = db.session.query(PARKING).filter(PARKING.uuid == parking_id).first()
    parking_gates = db.session.query(PARKING_GATES).filter(PARKING_GATES.parking_id == parking.uuid, PARKING_GATES.deleted_at == None).all()

    return parking, parking_gates

def getOrdersVehicles(parking_id,state):
    order, vehicle = db.session.query(ORDER,VEHICLE).filter(ORDER.parking_id == parking_id, ORDER.vehicle_id == VEHICLE.id, ORDER.state == state).all()

    return order, vehicle

def getCounts_Orders(parking_id,state):
    orders_count = db.session.query(ORDER).filter(ORDER.parking_id == parking_id, ORDER.state == state).count()

    return orders_count

#查询员工信息
def getStaffInfo(staff_id):
    staff_info = db.session.query(STAFF_INFO).filter(STAFF_INFO.staff_id == staff_id).first()

    return staff_info

def list_messages(staff_id):
    result = db.session.query(MESSAGE).filter(MESSAGE.receiver == staff_id, MESSAGE.deleted_at == None).order_by(
        MESSAGE.created_at.desc()).limit(50)
    return result

def list_messages_no_read(staff_id):
    result = db.session.query(MESSAGE).filter(MESSAGE.receiver == staff_id, MESSAGE.deleted_at == None, MESSAGE.read_at == None).order_by(
        MESSAGE.created_at.desc()).count()
    return result

def show_message(message_id):
    message = db.session.query(MESSAGE).filter(MESSAGE.id == message_id).first()
    return message

def read_all_messages(staff_id):
    try:
        db.session.query(MESSAGE).filter(MESSAGE.receiver == staff_id, MESSAGE.deleted_at == None).update({"read_at": datetime.datetime.now()})
        db.session.commit()
    except Exception as ex:
        print(ex)
        return False

    return True