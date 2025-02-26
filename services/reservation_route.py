from flask import Blueprint
from .views.reservation_view import reserve_parking, static_files

# 📌 블루프린트 생성
reservation_bp = Blueprint('reservation_bp', __name__)

# 📌 예약 페이지 라우트 등록
@reservation_bp.route('/<int:parkinglot_id>/reserve', methods=['GET', 'POST'])
def reserve_parking_route(parkinglot_id):  # ✅ 다른 함수명을 사용해서 충돌 방지
    return reserve_parking(parkinglot_id)

reservation_bp.route("/static/<path:filename>")(static_files)

# map_bp.route("/", endpoint="index")(home_view)
# map_bp.route("/static/<path:filename>")(static_files)
# map_bp.route("/api/parking-lots")(get_parking_lots)