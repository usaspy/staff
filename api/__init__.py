from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config as cfg
from collections import defaultdict
from common import mq
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://%s:%s@%s/%s" % (cfg.MYSQL_LOGINNAME, cfg.MYSQL_PASSWORD, cfg.MYSQL_HOST, cfg.DATABASE)

db = SQLAlchemy(app)

TOKENS_CACHE = defaultdict(int)

from api import authApi
from api import staffApi
from api import orderApi
from api import decorator
from api import sysApi
from service import authService
from common import mq_message

#初始化token_cache
len = authService.TokenCache_initialize(TOKENS_CACHE)
print("*** Token缓存加载完成...%s"% len)

#启动主机间缓存同步服务
mqthread = threading.Thread(target=mq.syncTokenCache_consume, args=(TOKENS_CACHE, ))
mqthread.start()
print("*** 主机间Token缓存同步服务已启动...%s"% cfg.SYSTEM_ID)

#消息处理服务已启动
msthread = threading.Thread(target=mq_message.message_consume, args=())
msthread.start()
print("*** 消息处理服务已启动...%s"% cfg.SYSTEM_ID)