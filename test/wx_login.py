
import requests
#developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
#{"session_key":"e61gH+jDmsVmN9up+SO93w==","openid":"o6GxG5baR_Flfh2qIrROnwtF_oM4"}
#微信小程序登录流程
def code2Session(code, appid, appSecret):
    #https://api.weixin.qq.com/sns/jscode2session?appid=APPID&secret=SECRET&js_code=JSCODE&grant_type=authorization_code
    kw= {"appid":appid,"secret":appSecret,"grant_type":"authorization_code","js_code":code}
    url = "https://api.weixin.qq.com/sns/jscode2session?"
    resp = requests.get(url,params=kw)

    print(resp.text)




if __name__ == "__main__":
    code2Session("063WShll2ldNk84MpBnl2foZf03WShlX","wx3eb56946f427e979","efaf9c63776a12807e9dcef29987e138")