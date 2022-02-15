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

#预约单状态变更-车辆进场
@app.route('/api/staff/in_confirm/<string:order_id>',methods=['PUT'])
def in_confirm(order_id):
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   staff_id = token_info["uuid"]
   result = orderService.go_in_confirm(staff_id, order_id)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure", "reason":"入场确认出现异常"})
