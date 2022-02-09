import math
from model.parking import *
from sqlalchemy.sql import or_
from api import db

def _getSquareFixedPositions(longitude, latitude, distance):
    EARTH_RADIUS = 6371

    #角度转弧度
    def deg2rad(deg):
        return math.radians(deg)

    d_lng = 2 * math.asin(math.sin(distance / (2 * EARTH_RADIUS)) / math.cos(deg2rad(latitude)))
    d_lng = deg2rad(d_lng)
    d_lat = distance / EARTH_RADIUS
    d_lat = deg2rad(d_lat)

    left_top = {'lat': latitude + d_lat, 'lng': longitude - d_lng}
    right_top = {'lat': latitude + d_lat, 'lng': longitude + d_lng}
    left_bottom = {'lat': latitude - d_lat, 'lng': longitude - d_lng}
    right_bottom = {'lat': latitude - d_lat, 'lng': longitude + d_lng}

    return left_top, right_top, left_bottom, right_bottom

#查找附近的停车场
def searchNearByParkings(longitude, latitude, distance=0.5):
    square = _getSquareFixedPositions(longitude, latitude, distance)
    print(square)
    left_top = square[0]
    right_top = square[1]
    left_bottom = square[2]
    right_bottom = square[3]

    #$info_sql = "select id,locateinfo,lat,lng from `lbs_info` where lat<>0 and lat>{$squares['right-bottom']['lat']} " \
    #            "and lat<{$squares['left-top']['lat']} and lng>{$squares['left-top']['lng']} and lng<{$squares['right-bottom']['lng']} ";

    #查询周边满足条件的停车场（最多30个）
    result = db.session.query(PARKING_MEMORY).filter(PARKING_MEMORY.location_y != 1, PARKING_MEMORY.location_y > right_bottom['lat'],
                                              PARKING_MEMORY.location_y < left_top['lat'],
                                              PARKING_MEMORY.location_x > left_top['lng'],
                                              PARKING_MEMORY.location_x < right_bottom['lng']).limit(30)
    #print(result.all())
    return result

#根据条件查询停车场（最多12个）
def searchParkingsByConditions(keyword):
    result = db.session.query(PARKING_MEMORY).filter(or_(PARKING_MEMORY.name.like('%' + keyword + '%'), PARKING_MEMORY.address.like('%' + keyword + '%'), PARKING_MEMORY.tag.like('%' + keyword + '%'))).limit(12)

    return result


def getParkingByUUID(uuid):
    parking, parking_rule = db.session.query(PARKING, PARKING_RULES).filter(
        PARKING.uuid == uuid, PARKING.uuid == PARKING_RULES.parking_id).first()

    return parking,parking_rule

def PARKING_MEMORY_initialize():
    db.session.query(PARKING_MEMORY).delete()

    ls = db.session.query(PARKING).filter(PARKING.deleted_at == None).all()
    for parking in ls:
        parking_mem = PARKING_MEMORY(uuid=parking.uuid, name=parking.name, address=parking.address, pmc=parking.pmc, photos=parking.photos, type=parking.type, service_kind=parking.service_kind,service_time=parking.service_time, service_spaces=parking.service_spaces, location_x=parking.location_x, location_y=parking.location_y, state=parking.state, created_at=parking.created_at, updated_at=parking.updated_at, deleted_at=parking.deleted_at, tag=parking.tag, keywords=parking.keywords, phone=parking.phone, star=parking.star, evaluation=parking.evaluation)
        db.session.add(parking_mem)
    db.session.commit()

    return len(ls)


