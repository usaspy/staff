from api import app
from api import TOKENS_CACHE
from flask import request
from service import authService
from flask import jsonify


'''
物业人员首次使用前执行身份识别
识别成功则记录staff，并绑定staff_info得staff_id
返回：识别成功或失败
'''
@app.route('/auth/identification/<string:code>',methods=['POST'])
def identification(code):
   realname = request.json["realname"]
   idcard = request.json["idcard"]
   phone = request.json["phone"]

   result = authService.identification(code, realname, idcard, phone)

   if result:
      return jsonify({"result": "success"})
   else:
      return jsonify({"result": "failure"})

#小程序用户登录认证获取token
#调用此接口将生成TOKEN,并同步到内存TOKEN_CACHE中去
@app.route('/auth/token/<string:code>',methods=['GET'])
def getToken(code):
   token = authService.generateToken(code, TOKENS_CACHE)

   return jsonify({'token': token})


#初始化TOKEN_CACHE
#调用此接口将加载所有TOKEN到内存变量中，后续用户TOKEN验证在内存中完成，不查数据库
@app.route('/auth/token/cache',methods=['GET'])
def TokenCache_initialize():
   TOKENS_CACHE.clear() #清空字典
   len = authService.TokenCache_initialize(TOKENS_CACHE)

   return jsonify({'result':'tokens cache initialized','cache_size': len})

