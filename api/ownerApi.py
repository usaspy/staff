from api import app
from api import TOKENS_CACHE
from flask import request
from service import ownerService
from service import authService
from flask import jsonify
from common import wx_tools
import config
from common import tools
import datetime



# [获取用户初始信息]
@app.route('/api/owner/initial_data', methods=['GET'])
def get_owner_initial_data():
   token_info = tools.getTokenInfo(request, TOKENS_CACHE)
   owner_id = token_info["uuid"]

   owner_data={}
   owner_data["MESSAGES"] = ownerService.list_messages_no_read(owner_id)
   # 获得用户当前预约中的订单信息
   the_last_order = ownerService.getLastOrderByOwnerId(owner_id)
   owner_data["LAST_ORDER"] = the_last_order

   # 获得用户信息
   owner_info = ownerService.getOwnerInfo(owner_id)
   owner_data["OWNER_INFO"] = {"wx_phone": owner_info.wx_phone,"wx_avatar_url":owner_info.wx_avatar_url,"wx_nickname":owner_info.wx_nickname}

   #获取该车主名下得所有车辆
   vehicles = ownerService.getVehiclesByOwnerId(owner_id)
   owner_data["MY_VEHICLES"] = vehicles

   # 获取该车主收藏得停车场
   favorites = ownerService.getFavoriteByOwnerId(owner_id)
   owner_data["MY_FAVORITES"] = favorites

   owner_data["TIMESTAMP"] = datetime.datetime.now()
   owner_data["说明"] = "{'LAST_ORDER':'在途预约单','MESSAGES':'我的消息','MY_VEHICLES':'我的车辆','MY_FAVORITES':'我收藏的停车场','OWNER_INFO':'我的用户资料'}"
   print(owner_data)
   return jsonify(owner_data)

#调用此接口更新用户的微信手机号
##https://blog.csdn.net/Lovehanxiaoyan/article/details/96600165
@app.route('/api/owner/phonenumber',methods=['PUT'])
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

   ownerService.updatePhoneNumber(mobile, token_info["uuid"])

   return jsonify({'phoneNumber': mobile})

#调用此接口更新用户的昵称和头像
@app.route('/api/owner/avatar_nickname',methods=['PUT'])
def avatar_nickname():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   avatarUrl = request.json["avatarUrl"]
   nickName = request.json["nickName"]

   ownerService.updateAvatarNickname(avatarUrl, nickName, token_info["uuid"])

   return jsonify({'avatarUrl': avatarUrl,"nickName":nickName})

#停车场加入车主收藏
@app.route('/api/owner/favorite/parking',methods=['POST'])
def add_favorite_parking():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   parking_id = request.json["parking_id"]

   result = ownerService.addFavorite(parking_id, token_info["uuid"])

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure"})


#停车场从车主收藏中删除
@app.route('/api/owner/favorite/parking',methods=['DELETE'])
def delete_favorite_parking():
   #token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   owner_parking_id = request.json["owner_parking_id"]
   result = ownerService.delFavorite(owner_parking_id)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure"})


#添加常用车辆
@app.route('/api/owner/favorite/vehicle',methods=['POST'])
def add_favorite_vehicle():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   vehicle_number = request.json["vehicle_number"]
   #NER = request.json["ner"] #是否新能源
   #vehicle_type = request.json["vehicle_type"] #车辆类型  SUV  小车
   #horsepower = request.json["horsepower"] #排量 1.5 2.0
   #vehicle_color = request.json["vehicle_color"] #排量 1.5 2.0

   vehicle_info = {}
   vehicle_info["NER"] = None
   vehicle_info["vehicle_type"] = None
   vehicle_info["horsepower"] = None
   vehicle_info["vehicle_color"] = None

   result = ownerService.addVehicle(token_info["uuid"], vehicle_number, vehicle_info)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure","reason":"车牌[%s]已存在"% vehicle_number})

#删除常用车辆
@app.route('/api/owner/favorite/vehicle',methods=['DELETE'])
def delete_favorite_vehicle():
   #token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   vehicle_id = request.json["vehicle_id"]

   result = ownerService.deleteVehicle(vehicle_id)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure","reason":"该车牌有正在进行中的预约单"})


#查询车主得预约记录
@app.route('/api/owner/orders',methods=['GET'])
def owner_orders():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   my_orders = ownerService.getOwnerOrders(token_info["uuid"])

   return jsonify({"my_orders": my_orders})

#查询车主得缴费记录
@app.route('/api/owner/bill/list',methods=['GET'])
def owner_orders_fee():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   my_bills = ownerService.getOwnerBills(token_info["uuid"])

   return jsonify({"my_bills": my_bills})

#我的消息
@app.route('/api/owner/message/list',methods=['GET'])
def my_messages():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   my_messages = ownerService.list_messages(token_info["uuid"])

   messages = []
   for msg in my_messages:
      messages.append({"message_id":msg.id,"message_type":msg.message_type,"message_body":msg.message_body,"created_at":msg.created_at,"read_at":msg.read_at})

   return jsonify({"my_orders_fee": messages})

#查看我的消息
@app.route('/api/owner/message/<string:message_id>',methods=['GET'])
def show_message(message_id):
   #token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   msg = ownerService.show_message(message_id)

   return jsonify({"message_id":msg.id,"message_type":msg.message_type,"message_body":msg.message_body,"created_at":msg.created_at,"read_at":msg.read_at})


#所有已读
@app.route('/api/owner/message/read_all',methods=['GET'])
def read_all_messages():
   token_info = tools.getTokenInfo(request, TOKENS_CACHE)

   result = ownerService.read_all_messages(token_info["uuid"])

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure"})

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

#查询车主的开票记录
@app.route('/api/owner/invoice/list',methods=['GET'])
def owner_invoice_list():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   lists = ownerService.list_invoices(token_info["uuid"])

   invoices = []
   for invoice in lists:
      invoices.append({"invoice_id": invoice.id, "invoice_info": invoice.invoice_info, "owner_id": invoice.owner_id,
                       "created_at": invoice.created_at, "updated_at": invoice.updated_at})

   return jsonify({"my_invoices": invoices})


#申请开票
@app.route('/api/owner/invoice',methods=['POST'])
def owner_invoice_create():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   bill_ids = request.json["bill_ids"]

   invoice = {}
   invoice["invoice_type"] = request.json["invoice_type"]
   invoice["invoice_topic"] = request.json["invoice_topic"]
   invoice["taxes_number"] = request.json["taxes_number"]
   invoice["invoice_content"] = request.json["invoice_content"]
   invoice["invoice_amount"] = request.json["invoice_amount"]
   invoice["more_info"] = request.json["more_info"]

   receiver = {}
   receiver["receiver_name"] = request.json["receiver_name"]
   receiver["receiver_phone"] = request.json["receiver_phone"]
   receiver["receiver_email"] = request.json["receiver_email"]

   result = ownerService.create_invoices(token_info["uuid"], eval(bill_ids), invoice, receiver)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure"})


#车主评价
@app.route('/api/order/evaluation',methods=['POST'])
def order_evaluation():
   token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   order_id = request.json["order_id"]
   parking_id = request.json["parking_id"]
   owner_id = token_info["uuid"]

   parking_star = request.json["parking_star"]
   parking_evaluation = request.json["parking_evaluation"]
   result = ownerService.order_evaluation(order_id, owner_id, parking_id, str(parking_star), str(parking_evaluation))

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure"})

#查看车主评价
@app.route('/api/order/evaluation/<string:order_id>',methods=['GET'])
def get_order_evaluation(order_id):
   #token_info = tools.getTokenInfo(request,TOKENS_CACHE)

   result = ownerService.getOrderEvaluation(order_id)

   if result:
      return jsonify({"order_id": result.order_id,"parking_star":result.parking_star,"parking_evaluation":result.parking_evaluation})
   else:
      return jsonify({"order_id": None,"parking_star": None,"parking_evaluation": None})