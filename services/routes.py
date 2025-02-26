from flask import Blueprint
from .views.parkinglot import parking_lots, parking_lot_detail

# 📌 블루프린트 생성
parkinglot_bp = Blueprint('parkinglot_bp', __name__)

# 📌 주차장 목록 라우트 등록 (올바른 URL prefix 적용)
@parkinglot_bp.route('/', methods=['GET'])
def parking_lots_route():
    return parking_lots()

# 📌 주차장 상세 정보 라우트 등록
@parkinglot_bp.route('/<int:parkinglot_id>', methods=['GET'])
def parking_lot_detail_route(parkinglot_id):
    return parking_lot_detail(parkinglot_id)