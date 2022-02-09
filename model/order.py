from api import db

#停车订单
class ORDER(db.Model):
    __tablename__='WX_ORDER'
    uuid = db.Column(db.String(36),primary_key=True)
    vehicle_id = db.Column(db.INT)
    parking_id = db.Column(db.String(36))
    rule_id = db.Column(db.INT)
    state = db.Column(db.INT)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

#订单执行情况
class ORDER_PROCESS(db.Model):
    __tablename__='WX_ORDER_PROCESS'
    id = db.Column(db.INT,primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(36))
    state = db.Column(db.INT)
    timestamp = db.Column(db.DateTime)
    executor = db.Column(db.String(36))
    executor_type = db.Column(db.String(10))

#缴费账单
class BILL(db.Model):
    __tablename__='WX_BILL'
    id = db.Column(db.INT,primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(36))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.BIGINT)
    rule_id = db.Column(db.INT)
    fee_1 = db.Column(db.DECIMAL)
    fee_2 = db.Column(db.DECIMAL)
    fee_mode = db.Column(db.INT)
    invoice_id = db.Column(db.String(36))

#发票
class INVOICE(db.Model):
    __tablename__='WX_INVOICE'
    uuid = db.Column(db.String(36),primary_key=True)
    created_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    invoice_info = db.Column(db.String(255))
    owner_id = db.Column(db.String(36))
    receiver_info = db.Column(db.String(255))