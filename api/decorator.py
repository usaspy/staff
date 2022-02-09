from flask import make_response
from flask import jsonify, request, redirect, abort, session
from api import app
from api import TOKENS_CACHE

'''
系统装饰器
'''
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error':'Bad Request', 'description': '客户端请求的语法错误'}), 200)

@app.errorhandler(401)
def Unauthorized(error):
    return make_response(jsonify({'error':'Unauthorized', 'description': '请求要求用户的身份认证'}), 200)

@app.errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'error': 'Forbidden', 'description': '服务器收到客户端请求，但是拒绝执行此请求'}), 200)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found', 'description': '请求URL地址有误'}), 200)

@app.before_request
def before_request():
    url = request.path
    print(url)

    if url == '/index':
        return None
    elif url.startswith('/auth'):
        return None
    elif url.startswith('/map'):
        return None
    elif url.startswith('/sys'):
        return None
    elif url.startswith('/api'):
        # if not session.get('token'):
        #    abort(401)
       #if not request.json or not 'token' in request.json:
            #abort(400)
        if request.headers.get("token") is None:
            abort(401)
        if request.headers.get("token") not in TOKENS_CACHE:
            abort(401)
        if request.headers['Content-Type'] != 'application/json':
            abort(403)
        return None
    else:
        return redirect("/index")


#[api list]
@app.route('/index',methods=['GET'])
def you_are_weclome():
    return jsonify({'说明': '熊猫泊车RESTFul-API接口'})
