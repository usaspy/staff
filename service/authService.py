from model.pmc import *
import requests as req
import datetime
import base64
from common import tools, wx_tools
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
        staff = STAFF.query.filter_by(open_id=openid).first()

        if staff: #员工存在
           db.session.query(STAFF).filter(STAFF.uuid == staff.uuid).update({"session_key":session_key, "token": new_token, "updated_at": str(nowTime)})
           db.session.commit()

           TOKENS_CACHE.pop(staff.token, None)  # 从Cache中删除old_token (一定要先删再加，因为在有效期内session_key一样，后面可以改一下token得生成规则)
           TOKENS_CACHE[new_token] = {"uuid":staff.uuid, "session_key":session_key, "open_id": openid, "updated_at": nowTime} #更新Cache中的用户token（因为session_key每次登陆后都会改变）

           # 消息入库并加入到本地TOKEN_CACHE之后
           # 通过消息队列同步到其他主机上的TOKEN_CACHE
           if cfg.TOKEN_SYNC_FLAG:
               message = json.dumps(
                   {'SYSTEM_ID': "%s" % cfg.SYSTEM_ID, 'ADD': "%s" % str({"key": new_token, "values": TOKENS_CACHE[new_token]}), 'DELETE:': "%s" % str({"key": staff.token})})
               try:
                   mq.syncTokenCache_publish(message)
               except Exception as ex:
                   print("同步TOKEN到其他服务器时出错...[%s]" % cfg.SYSTEM_ID)

           return new_token
        else:  #该员工不存在，需要先完成绑定身份操作
           return 2
    else:
        return 1


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

#员工首次使用前身份验证
def verify(code, encryptedData, vinum):
    status, session_key, openid = __code2Session(code, cfg.APPID, cfg.APPSECRET)

    if status:
        # 解密手机号
        pc = wx_tools.WXBizDataCrypt(cfg.APPID, session_key)
        mobile_obj = pc.decrypt(encryptedData, vinum)
        mobile = mobile_obj['phoneNumber']

        # 比对信息，匹配身份信息
        staff_info = db.session.query(STAFF_INFO).filter(STAFF_INFO.wx_phone == mobile).first()

        if staff_info:
            nowTime = datetime.datetime.now()
            uuid = tools.generateUUID()
            # 生成new_token
            token_str = str(session_key)
            b64_token = base64.urlsafe_b64encode(token_str.encode("iso8859-1"))
            new_token = b64_token.decode("iso8859-1")

            new_staff = STAFF(uuid=uuid, open_id=openid, session_key=session_key, token=new_token,
                              state=0, created_at=nowTime, updated_at=nowTime)
            db.session.add(new_staff)
            db.session.query(STAFF_INFO).filter(STAFF_INFO.id == staff_info.id).update(
                {"staff_id": uuid, "updated_at": str(nowTime)})
            db.session.commit()

            return 0
        else:
            return 2   #匹配失败，系统内无该员工信息
    else:
        return 1  # 调用微信服务器认证接口失败