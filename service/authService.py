from model.pmc import *
import requests as req
import datetime
import base64
from common import tools
import config as cfg
from common import mq
import json


#https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html

#调用微信服务器认证接口
#返回认证结果：
# {"session_key":"e61gH+jDmsVmN9up+SO93w==","openid":"o6GxG5baR_Flfh2qIrROnwtF_oM4"}
def __code2Session(code, appid, appSecret):
    kw = {"appid":appid, "secret":appSecret, "grant_type":"authorization_code", "js_code":code}
    url = "https://api.weixin.qq.com/sns/jscode2session?"
    resp = req.get(url, params=kw)

    try:
        session_key = resp.json()["session_key"]
        openid = resp.json()["openid"]

        return True, session_key, openid
    except:
        return False, None, None

#https://www.cnblogs.com/tiger666/articles/9993483.html
def generateToken(code, TOKENS_CACHE, expire = 3600*24):
    status, session_key, openid = __code2Session(code, cfg.APPID, cfg.APPSECRET)

    if status:
        nowTime = datetime.datetime.now()

        #生成new_token
        token_str = str(session_key)
        b64_token = base64.urlsafe_b64encode(token_str.encode("iso8859-1"))
        new_token = b64_token.decode("iso8859-1")

        #车主表新增或车主表更新session_key和token
        owner = OWNER.query.filter_by(open_id=openid).first()

        if owner: #车主已存在
           db.session.query(OWNER).filter(OWNER.uuid == owner.uuid).update({"session_key":session_key, "token": new_token, "updated_at": str(nowTime)})
           db.session.commit()

           TOKENS_CACHE.pop(owner.token, None)  # 从Cache中删除old_token (一定要先删再加，因为在有效期内session_key一样，后面可以改一下token得生成规则)
           TOKENS_CACHE[new_token] = {"uuid":owner.uuid, "session_key":session_key, "open_id": openid, "updated_at": nowTime} #更新Cache中的用户token（因为session_key每次登陆后都会改变）

           # 消息入库并加入到本地TOKEN_CACHE之后
           # 通过消息队列同步到其他主机上的TOKEN_CACHE
           if cfg.TOKEN_SYNC_FLAG:
               message = json.dumps(
                   {'SYSTEM_ID': "%s" % cfg.SYSTEM_ID, 'ADD': "%s" % str({"key": new_token, "values": TOKENS_CACHE[new_token]}), 'DELETE:': "%s" % str({"key": owner.token})})
               try:
                   mq.syncTokenCache_publish(message)
               except Exception as ex:
                   print("同步TOKEN到其他服务器时出错...[%s]" % cfg.SYSTEM_ID)
        else:  #新用户登录
           new_owner = OWNER(uuid=tools.generateUUID(), open_id=openid, session_key=session_key, token=new_token, state=0, created_at=nowTime, updated_at=nowTime)
           new_owner_info = OWNER_INFO(owner_id=new_owner.uuid, wx_phone="unknown", wx_nickname="unknown", wx_avatar_url="unknown")
           db.session.add(new_owner)
           db.session.add(new_owner_info)
           db.session.commit()

           TOKENS_CACHE[new_token] = {"uuid":new_owner.uuid, "session_key":session_key, "open_id": openid, "updated_at": str(nowTime)} #从Cache中增加new_token

           # 消息入库并加入到本地TOKEN_CACHE之后
           # 通过消息队列同步到其他主机上的TOKEN_CACHE
           if cfg.TOKEN_SYNC_FLAG:
               message = json.dumps(
                   {'SYSTEM_ID': "%s" % cfg.SYSTEM_ID,
                    'ADD:': "%s" % str({"key": new_token, "values": TOKENS_CACHE[new_token]})})
               try:
                   mq.syncTokenCache_publish(message)
               except Exception as ex:
                   print("同步TOKEN到其他服务器时出错...[%s]" % cfg.SYSTEM_ID)

        return new_token

    return None


def TokenCache_initialize(TOKENS_CACHE):
   list = STAFF.query.filter_by(state=0).all()

   for staff in list:
      TOKENS_CACHE[staff.token] = {"uuid":staff.uuid, "session_key":staff.session_key, "open_id": staff.open_id, "updated_at": str(staff.updated_at)}

   return len(TOKENS_CACHE)

#用户下线
def removeToken(token, TOKENS_CACHE):
    TOKENS_CACHE.pop(token, None)
    if cfg.TOKEN_SYNC_FLAG:
        message = json.dumps(
            {'SYSTEM_ID': "%s" % cfg.SYSTEM_ID, 'DELETE:': "%s" % str({"key": token})})
        try:
            mq.syncTokenCache_publish(message)
        except Exception as ex:
            print("同步TOKEN到其他服务器时出错...[%s]" % cfg.SYSTEM_ID)

    return True


def identification(code, realname, idcard, phone):
    pass