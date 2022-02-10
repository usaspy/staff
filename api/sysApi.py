from flask import jsonify
from api import app
from common import sysParam
from common import sysDict
import datetime


# [获取系统参数]
@app.route('/sys/initial_data', methods=['GET'])
def get_sys_initial_data():
    envs={}
    envs["DISTANCE"] = sysParam.DISTANCE
    envs["ORDER_STATE"] = sysDict.ORDER_STATE
    envs["PARKING_STATE"] = sysDict.PARKING_STATE
    envs["PARKING_TYPE"] = sysDict.PARKING_TYPE
    envs["PARKING_SERVICE_KIND"] = sysDict.PARKING_SERVICE_KIND
    envs["VEHICLE_COLOR"] = sysDict.VEHICLE_COLOR
    envs["RESERVE_TIME"] = sysParam.RESERVE_TIME
    envs["MESSAGE_TYPE"] = sysDict.MESSAGE_TYPE
    envs["RECEIVE_TYPE"] = sysDict.RECEIVE_TYPE

    envs["TIMESTAMP"] = datetime.datetime.now()

    return jsonify(envs)
