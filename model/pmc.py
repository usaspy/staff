from api import db

#物业公司信息
class PMC(db.Model):
    __tablename__ = 'WX_PMC'
    uuid = db.Column(db.String(36),primary_key=True)
    name = db.Column(db.String(255))

#物业员工
class STAFF(db.Model):
    __tablename__ = 'WX_STAFF'
    uuid = db.Column(db.String(36), primary_key=True)
    open_id = db.Column(db.String(255))
    session_key = db.Column(db.String(255))
    unionid = db.Column(db.String(255))
    token = db.Column(db.String(255))
    app_id = db.Column(db.String(255))
    state = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)


#物业员工附加信息表
class STAFF_INFO(db.Model):
    __tablename__ = 'WX_STAFF_INFO'
    id = db.Column(db.INT,primary_key=True, autoincrement=True)
    staff_id = db.Column(db.String(36))
    realname = db.Column(db.String(255))
    sex = db.Column(db.String(255))
    idcard = db.Column(db.String(255))
    pmc = db.Column(db.String(32))
    wx_nickname = db.Column(db.String(255))
    wx_avatar_url = db.Column(db.String(255))
    wx_phone = db.Column(db.String(255))
    parking_id = db.Column(db.String(36))
    gates_now = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
