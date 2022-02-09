from api import app
from api import TOKENS_CACHE
from flask import request
from service import orderService
from flask import jsonify
from common.sysDict import ORDER_STATE
from common import tools
from common import pay
import base64
from common import mq_message
import json

#查看订单详情
@app.route('/api/order/detail/<string:order_id>',methods=['GET'])
def getOrder(order_id):
   #token_info = tools.getOwnerInfo(request,TOKENS_CACHE)

   order_info, order_process_infos, vehicle_info, parking_info, parking_rule_info,parking_process = orderService.getOrderByOrderId(order_id)
   ois = {}
   ois["uuid"] = order_info.uuid
   ois["vehicle_id"] = order_info.vehicle_id
   ois["parking_id"] = order_info.parking_id
   ois["rule_id"] = order_info.rule_id
   ois["state"] = order_info.state
   ois["created_at"] = order_info.created_at

   vis = {}
   vis["vehicle_number"] = vehicle_info.vehicle_number
   vis["vehicle_info"] = vehicle_info.vehicle_info
   vis["owner_id"] = vehicle_info.owner_id

   opis = []
   for op in order_process_infos:
      opi = {}
      opi["state"] = op.state
      opi["timestamp"] = op.timestamp
      opi["executor"] = op.executor
      opi["executor_type"] = op.executor_type
      opis.append(opi)

   pis = {}
   pis["name"] = parking_info.name
   pis["address"] = parking_info.address
   pis["photos"] = parking_info.photos
   pis["service_kind"] = parking_info.service_kind
   pis["service_time"] = parking_info.service_time
   pis["location_x"] = parking_info.location_x
   pis["location_y"] = parking_info.location_y
   pis["type"] = parking_info.type
   pis["phone"] = parking_info.phone
   pis["service_spaces"] = parking_info.service_spaces
   pis["state"] = parking_info.state
   pis["tag"] = parking_info.tag
   pis["star"] = parking_info.star
   pis["evaluation"] = parking_info.evaluation

   pris = {}
   pris["rule_desc"] = parking_rule_info.rule_desc

   #如果是入场状态，计算费用，显示入场时长
   if order_info.state == 1:
      ois["in_at"] = parking_process.in_at
      ois["fee_about"] = orderService.__generate_bill(order_id).fee_1
   return jsonify({"order_info": ois, "order_process_infos": opis, "vehicle_info": vis, "parking_info": pis,  "parking_rule_info": pris})


#发起预约单
@app.route('/api/order',methods=['POST'])
def createOrder():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   vehicle_number = request.json["vehicle_number"] #车牌号，无论存不存在都是必填
   parking_id = request.json["parking_id"]
   state = 0

   result = orderService.createOrder(token_info["uuid"], vehicle_number, parking_id, state)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure"})


#预约单状态变更-车辆进场
@app.route('/api/order/<string:order_id>',methods=['PUT'])
def processOrder(order_id):
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   state = request.json["state"]
   if state == 1: #入场
      qr = request.json["qr"]  # qr 扫码结果：<停车场uuid_通道uuid>
      result = orderService.go_in(token_info["uuid"], order_id, qr)

      if result:
         message = json.dumps(
            {'message_type': 2, 'order_id': "%s" % order_id, 'receiver': "%s" % token_info["uuid"]})
         mq_message.message_publish(message)

         return jsonify({"result": "success"})
      else:
         return jsonify({"result": "failure","reason":"【入场】二维码不正确或其他原因"})
   elif state == 3: #离场
      qr = request.json["qr"]  # qr 扫码结果：<停车场uuid_通道uuid>
      result = orderService.go_out(token_info["uuid"], order_id, qr)

      if result:
         message = json.dumps(
            {'message_type': 3, 'order_id': "%s" % order_id, 'receiver': "%s" % token_info["uuid"]})
         mq_message.message_publish(message)

         return jsonify({"result": "success"})
      else:
         return jsonify({"result": "failure","reason":"缴费不成功或【出场】二维码不正确"})
   elif state == 9: #取消
      result = orderService.cancel(token_info["uuid"], order_id)

      if result:
         return jsonify({"result": "success"})
      else:
         return jsonify({"result": "failure", "reason": "预约单取消失败"})
   else:
      return jsonify({"result": "unknown","state":state})


#查询车主最近一次的预约单[any state]
@app.route('/api/owner/order/latest',methods=['GET'])
def getLatestOrder():
   token_info = tools.getTokenInfo(request, TOKENS_CACHE)

   latest_order, parking = orderService.getLatestOrder(token_info["uuid"])

   if latest_order:
      return jsonify({"order_id":latest_order.uuid, "order_state":latest_order.state, "parking_id": parking.uuid, "parking_name": parking.name, "order_created_at":latest_order.created_at})
   else:
      return jsonify({})
