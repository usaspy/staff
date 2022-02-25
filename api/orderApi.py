from api import app
from api import TOKENS_CACHE
from flask import request
from service import orderService
from flask import jsonify
from common.sysDict import ORDER_STATE
from common import tools
import base64
from common import mq_message
import json

#预约单状态变更-车辆进场-确认
@app.route('/api/staff/in_confirm/<string:order_id>',methods=['PUT'])
def in_confirm(order_id):
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   staff_id = token_info["uuid"]
   result = orderService.go_in_confirm(staff_id, order_id)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure", "reason":"入场确认出现异常"})


#预约单状态变更-场内车辆-离场-显示费用
@app.route('/api/staff/pay_manual/<string:order_id>', methods=['PUT'])
def pay_manual(order_id):
   #token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   bill, vehicle = orderService.go_out_pay_manual(order_id)

   return jsonify({"vehicle_number":vehicle.vehicle_number, "fee_1": str(bill.fee_1),"start_time":bill.start_time,"end_time":bill.end_time,"duration":bill.duration,"pay_state":bill.pay_state})


#预约单状态变更-场内车辆-离场-人工收费后放行
@app.route('/api/staff/out_confirm/<string:order_id>', methods=['PUT'])
def out_confirm(order_id):
   token_info = tools.getTokenInfo(request, TOKENS_CACHE)

   staff_id = token_info["uuid"]
   gate_id = request.json["gate_id"]

   result = orderService.go_out_confirm(staff_id, order_id, gate_id)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure", "reason": "离场确认出现异常"})


#预约单状态变更-当前离场-人工放行确认
@app.route('/api/staff/out_confirm_20/<string:order_id>',methods=['PUT'])
def out_confirm_20(order_id):
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   staff_id = token_info["uuid"]
   gate_id = request.json["gate_id"]

   result = orderService.go_out_confirm_20(staff_id, order_id, gate_id)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure", "reason":"离场确认出现异常"})
