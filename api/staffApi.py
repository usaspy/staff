from api import app
from api import TOKENS_CACHE
from flask import request
from service import staffService
from service import authService
from flask import jsonify
from common import wx_tools
import config
from common import tools
import datetime

# [获取员工初始信息]
@app.route('/api/staff/initial_data', methods=['GET'])
def get_staff_initial_data():
   token_info = tools.getTokenInfo(request, TOKENS_CACHE)
   staff_id = token_info["uuid"]

   staff_data={}
   staff_data["MESSAGES"] = staffService.list_messages_no_read(staff_id)

   # 获得员工信息
   staff_info = staffService.getStaffInfo(staff_id)
   staff_data["STAFF_INFO"] = {"realname": staff_info.realname, "sex": staff_info.sex, "idcard": staff_info.idcard, "pmc": staff_info.pmc, "wx_phone": staff_info.wx_phone, "wx_avatar_url":staff_info.wx_avatar_url, "wx_nickname":staff_info.wx_nickname, "parking_id":staff_info.parking_id}

   # 获得停车场信息
   parking, parking_gates = staffService.getParkingInfo(staff_info.parking_id)
   gs = []
   for gate in parking_gates:
       g = {}
       g["id"] = gate.id
       g["category"] = gate.category
       g["name"] = gate.name
       g["device_id"] = gate.device_id
       g["qr_image_id"] = gate.qr_image_id
       gs.append(g)

   staff_data["PARKING_INFO"] = {"parking_id": parking.uuid, "parking_name": parking.name, "parking_address": parking.address, "service_time": parking.service_time,
                               "service_spaces": parking.service_spaces, "service_kind": parking.service_kind, "state": parking.state,
                               "gates": gs}

   staff_data["TIMESTAMP"] = datetime.datetime.now()
   staff_data["说明"] = "{'MESSAGES':'我得消息','STAFF_INFO':'用户资料','PARKING_INFO':'分管停车场信息','STAFF_INFO':'用户资料'}"
   print(staff_data)
   return jsonify(staff_data)

#调用此接口更新用户的微信手机号
##https://blog.csdn.net/Lovehanxiaoyan/article/details/96600165
@app.route('/api/staff/phonenumber',methods=['PUT'])
def phoneNumber():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   encryptedData = request.json["encryptedData"]
   vinum = request.json["vinum"]

   # 处理加密的手机号
   #encryptedData = encryptedData + '=='

   # 处理加密向量
   #iv = vinum + '=='

   # 解密手机号
   pc = wx_tools.WXBizDataCrypt(config.APPID, token_info["session_key"])
   mobile_obj = pc.decrypt(encryptedData, vinum)
   mobile = mobile_obj['phoneNumber']

   print(mobile)

   staffService.updatePhoneNumber(mobile, token_info["uuid"])

   return jsonify({'phoneNumber': mobile})

#调用此接口更新用户的昵称和头像
@app.route('/api/staff/avatar_nickname',methods=['PUT'])
def avatar_nickname():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   avatarUrl = request.json["avatarUrl"]
   nickName = request.json["nickName"]

   staffService.updateAvatarNickname(avatarUrl, nickName, token_info["uuid"])

   return jsonify({'avatarUrl': avatarUrl,"nickName":nickName})

#我的消息
@app.route('/api/staff/message/list',methods=['GET'])
def my_messages():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   my_messages = staffService.list_messages(token_info["uuid"])

   messages = []
   for msg in my_messages:
      messages.append({"message_id":msg.id,"message_type":msg.message_type,"message_body":msg.message_body,"created_at":msg.created_at,"read_at":msg.read_at})

   return jsonify({"my_messages": messages})

#查看我的消息
@app.route('/api/staff/message/<string:message_id>',methods=['GET'])
def show_message(message_id):
   #token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   msg = staffService.show_message(message_id)

   return jsonify({"message_id":msg.id,"message_type":msg.message_type,"message_body":msg.message_body,"created_at":msg.created_at,"read_at":msg.read_at})


#所有已读
@app.route('/api/staff/message/read_all',methods=['GET'])
def read_all_messages():
   token_info = tools.getTokenInfo(request, TOKENS_CACHE)

   result = staffService.read_all_messages(token_info["uuid"])

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure"})


# [查找处于预约状态的订单和车牌]
@app.route('/api/staff/<string:parking_id>/0/lists', methods=['GET'])
def get_0_lists(parking_id):
   order, vehicle = staffService.getOrders(parking_id, 0)
   ls = []
   for o,v in order, vehicle:
       obj = {}
       obj["order_id"] = o.uuid
       obj["vehicle_id"] = v.id
       obj["vehicle_number"] = v.vehicle_number
       obj["vehicle_info"] = v.vehicle_info
       ls.append(obj)

   return jsonify({"lists": ls})


# [查找已进场得订单和车牌]
@app.route('/api/staff/<string:parking_id>/1/lists', methods=['GET'])
def get_1_lists(parking_id):
   order, vehicle = staffService.getOrdersVehicles(parking_id, 1)
   ls = []
   for o, v in order, vehicle:
      obj = {}
      obj["order_id"] = o.uuid
      obj["vehicle_id"] = v.id
      obj["vehicle_number"] = v.vehicle_number
      obj["vehicle_info"] = v.vehicle_info
      ls.append(obj)

   return jsonify({"lists": ls})

'''
用户退出登录
1.清楚缓存中的用户登录数据
>> /auth/token/<string:code>  登录接口
'''
@app.route('/api/owner/logout',methods=['DELETE'])
def logout():
   #token_info = tools.getTokenInfo(request, TOKENS_CACHE)
   token = request.headers.get("token")
   result = authService.removeToken(token,TOKENS_CACHE)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure"})