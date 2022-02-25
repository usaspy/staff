from api import db

#车主信息
class OWNER(db.Model):
    __tablename__='WX_OWNER'
    uuid = db.Column(db.String(36),primary_key=True)
    open_id = db.Column(db.String(255))
    session_key = db.Column(db.String(255))
    unionid = db.Column(db.String(255))
    token = db.Column(db.String(255))
    app_id = db.Column(db.String(255))
    state = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

#常用停车场
class OWNER_PARKING(db.Model):
    __tablename__='WX_OWNER_PARKING'
    id = db.Column(db.INT,primary_key=True, autoincrement=True)
    owner_id = db.Column(db.String(36))
    parking_id = db.Column(db.String(36))
    created_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

#车主常用车辆信息
class VEHICLE(db.Model):
    __tablename__='WX_VEHICLE'
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.INT,primary_key=True, autoincrement=True)
    owner_id = db.Column(db.String(36))
    vehicle_number = db.Column(db.String(255))
    vehicle_info = db.Column(db.Text(65536))
    created_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    used_at = db.Column(db.DateTime)

#车主当前订单（未关闭的）
class OWNER_CURRENT_ORDER(db.Model):
    __tablename__='V_OWNER_CURRENT_ORDER'
    status = db.Column(db.INT)
    owner_id = db.Column(db.String(36),primary_key=True)
    current_order = db.Column(db.String(36))

#车主附加信息
class OWNER_INFO(db.Model):
    __tablename__='WX_OWNER_INFO'
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.INT,primary_key=True, autoincrement=True)
    owner_id = db.Column(db.String(36))
    wx_nickname = db.Column(db.String(255))
    wx_avatar_url = db.Column(db.String(255))
    wx_phone = db.Column(db.String(255))


#车主评分表
class EVALUATION(db.Model):
    __tablename__='WX_ORDER_EVALUATION'
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.INT,primary_key=True, autoincrement=True)
    owner_id = db.Column(db.String(36))
    order_id = db.Column(db.String(36))
    parking_id = db.Column(db.String(36))
    parking_star = db.Column(db.String(3))
    parking_evaluation = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)