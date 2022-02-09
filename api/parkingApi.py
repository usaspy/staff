from api import app
from service import parkingService
from service import ownerService
from flask import request
from flask import jsonify

'''
地图上搜索附近的停车场 
    @param: location_x 经度
    @param: location_y纬度
    @param: distance 方圆(千米)
    @param: conditions 查询条件 (可选)
        
    @return: 满足条件的停车场json数据，包括：停车场名称、经纬度、状态、运营情况
'''
@app.route('/map/nearbyParkings/<string:location_x>_<string:location_y>_<string:distance>',methods=['GET'])
def nearbyParkings(location_x, location_y, distance):
    try:
        result = parkingService.searchNearByParkings(float(location_x), float(location_y), float(distance))

        parkings = []

        for parking in result:
            rs = {}
            rs['name'] = parking.name
            rs['location_y'] = parking.location_y
            rs['location_x'] = parking.location_x
            rs['address'] = parking.address
            rs['photos'] = parking.photos
            rs['service_spaces'] = parking.service_spaces
            rs['service_kind'] = parking.service_kind
            rs['service_time'] = parking.service_time
            rs['type'] = parking.type
            rs['state'] = parking.state
            rs['uuid'] = parking.uuid
            rs['tag'] = parking.tag
            rs['keywords'] = parking.keywords
            rs['phone'] = parking.phone
            rs['star'] = parking.star
            rs['evaluation'] = parking.evaluation
            parkings.append(rs)
        #print(parkings)
    except Exception as ex:
        print(repr(ex))

    return jsonify({'parkings': parkings})


'''
根据条件查找停车场【列表】
    @param: keyword 查询条件(address、name)

    @return: 满足条件的停车场json数据，包括：停车场名称、经纬度、状态、运营情况
'''
@app.route('/map/findParkings', methods=['GET'])
def findParkings():
    try:
        keyword = request.values.get('keyword')
        result = parkingService.searchParkingsByConditions(keyword)

        parkings = []

        for parking in result:
            rs = {}
            rs['name'] = parking.name
            rs['location_y'] = parking.location_y
            rs['location_x'] = parking.location_x
            rs['address'] = parking.address
            rs['photos'] = parking.photos
            rs['service_spaces'] = parking.service_spaces
            rs['service_kind'] = parking.service_kind
            rs['service_time'] = parking.service_time
            rs['type'] = parking.type
            rs['state'] = parking.state
            rs['uuid'] = parking.uuid
            rs['tag'] = parking.tag
            rs['keywords'] = parking.keywords
            rs['phone'] = parking.phone
            rs['star'] = parking.star
            rs['evaluation'] = parking.evaluation
            parkings.append(rs)
        # print(parkings)
    except Exception as ex:
        print(repr(ex))

    return jsonify({'parkings': parkings})

#根据parking_id查询指定parking
@app.route('/map/parking/<string:parking_id>', methods=['GET'])
def getParking(parking_id):
    parking,parking_rule = parkingService.getParkingByUUID(parking_id)

    parkings = []

    if parking:
        rs = {}
        rs['name'] = parking.name
        rs['location_y'] = parking.location_y
        rs['location_x'] = parking.location_x
        rs['address'] = parking.address
        rs['photos'] = parking.photos
        rs['service_spaces'] = parking.service_spaces
        rs['service_kind'] = parking.service_kind
        rs['service_time'] = parking.service_time
        rs['type'] = parking.type
        rs['state'] = parking.state
        rs['uuid'] = parking.uuid
        rs['tag'] = parking.tag
        rs['keywords'] = parking.keywords
        rs['phone'] = parking.phone
        rs['rule_desc'] = parking_rule.rule_desc
        rs['star'] = parking.star
        rs['evaluation'] = parking.evaluation
        parkings.append(rs)
    return jsonify({"parking": parkings})

