from api import db

#停车订单
class MESSAGE(db.Model):
    __tablename__='WX_MESSAGE'
    id = db.Column(db.INT, primary_key=True, autoincrement=True)
    message_type = db.Column(db.Integer)
    message_body = db.Column(db.String(500))
    created_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    receiver = db.Column(db.String(36))
    receive_type = db.Column(db.Integer)