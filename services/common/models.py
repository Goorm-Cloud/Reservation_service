from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from sqlalchemy.dialects.mysql import DATETIME

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.Enum("admin", "user", name="role_enum"), nullable=False)

    reservations = db.relationship("Reservation", backref="user", lazy=True)


class ParkingLot(db.Model):
    __tablename__ = "parkinglot"

    parkinglot_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    parkinglot_name = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(20), nullable=False)
    parkinglot_div = db.Column(db.Enum("public", "private", name="parking_div_enum"), nullable=False)
    parkinglot_type = db.Column(db.Enum("indoor", "outdoor", "attached", name="parking_type_enum"), nullable=True)
    parkinglot_num = db.Column(db.Integer, nullable=True)
    parkinglot_cost = db.Column(db.Boolean, nullable=True)
    parkinglot_add = db.Column(db.String(100), nullable=True)
    parkinglot_day = db.Column(db.Enum("mon", "tue", "wed", "thu", "fri", "sat", "sun", name="parking_day_enum"),
                               nullable=True)
    parkinglot_time = db.Column(db.Time, nullable=True)

    reservations = db.relationship("Reservation", backref="parkinglot", lazy=True)


class Reservation(db.Model):
    __tablename__ = "reservation"

    reservation_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    parkinglot_id = db.Column(db.Integer, db.ForeignKey("parkinglot.parkinglot_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    reservation_status = db.Column(db.Enum("confirm", "none", "cancel", name="modified_type_enum"), nullable=True)

    created_at = db.Column(DATETIME(fsp=6), nullable=True)
    created_by = db.Column(db.String(16), nullable=True)
    modified_at = db.Column(DATETIME(fsp=6), nullable=True)
    modified_by = db.Column(db.String(16), nullable=True)