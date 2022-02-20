from api import db

#停车场信息
class PARKING(db.Model):
    __tablename__='WX_PARKING'
    uuid = db.Column(db.String(36),primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    pmc = db.Column(db.String(36))
    photos = db.Column(db.String(255))
    type = db.Column(db.Integer)
    service_kind = db.Column(db.Integer)
    service_time = db.Column(db.String(255))
    service_spaces = db.Column(db.Integer)
    location_x = db.Column(db.Float(8))
    location_y = db.Column(db.Float(8))
    state = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    tag = db.Column(db.String(255))
    keywords = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    star = db.Column(db.String(3))
    evaluation = db.Column(db.String(20))

#停车场信息-内存
class PARKING_MEMORY(db.Model):
    __tablename__='WX_PARKING_MEMORY'
    uuid = db.Column(db.String(36),primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    pmc = db.Column(db.String(36))
    photos = db.Column(db.String(255))
    type = db.Column(db.Integer)
    service_kind = db.Column(db.Integer)
    service_time = db.Column(db.String(255))
    service_spaces = db.Column(db.Integer)
    location_x = db.Column(db.Float(8))
    location_y = db.Column(db.Float(8))
    state = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    tag = db.Column(db.String(255))
    keywords = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    star = db.Column(db.String(3))
    evaluation = db.Column(db.String(20))


#停车场收费规则
class PARKING_RULES(db.Model):
    __tablename__='WX_PARKING_RULES'
    id = db.Column(db.INT,primary_key=True, autoincrement=True)
    parking_id = db.Column(db.String(36))
    template_id = db.Column(db.String(36))
    vars = db.Column(db.String(500))
    rule_desc = db.Column(db.String(500))
    created_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

#停车场进出情况
class PARKING_PROCESS(db.Model):
    __tablename__='WX_PARKING_PROCESS'
    id = db.Column(db.INT,primary_key=True, autoincrement=True)
    parking_id = db.Column(db.String(36))
    vehicle_id = db.Column(db.String(36))
    in_gate_id = db.Column(db.Integer)
    out_gate_id = db.Column(db.Integer)
    in_at = db.Column(db.DateTime)
    out_at = db.Column(db.DateTime)
    order_id = db.Column(db.String(36))
    in_confirm = db.Column(db.Integer)
    out_confirm = db.Column(db.Integer)


#停车场道闸
class PARKING_GATES(db.Model):
    __tablename__='WX_PARKING_GATES'
    id = db.Column(db.INT,primary_key=True, autoincrement=True)
    parking_id = db.Column(db.String(36))
    category = db.Column(db.Integer)
    name = db.Column(db.String(36))
    device_id = db.Column(db.String(36))
    qr_image_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    description = db.Column(db.String(255))