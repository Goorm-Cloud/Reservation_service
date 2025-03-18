from flask import Blueprint, send_from_directory, current_app
from .views.reservation_view import reserve_parking, static_files
import os

# 📌 블루프린트 생성
reservation_bp = Blueprint(
    'reservation_bp',
    __name__,
    static_folder='static',
    template_folder='templates'
)

# 📌 예약 페이지 라우트 등록
@reservation_bp.route('/<int:parkinglot_id>/reserve', methods=['GET', 'POST'])
def reserve_parking_route(parkinglot_id):  # ✅ 다른 함수명을 사용해서 충돌 방지
    return reserve_parking(parkinglot_id)

@reservation_bp.route("/static/<path:filename>")
def static_files(filename):
    """ 정적 파일 제공 라우트 """
    static_dir = os.path.join(current_app.root_path, "static")
    return send_from_directory(static_dir, filename)

# map_bp.route("/", endpoint="index")(home_view)
# map_bp.route("/static/<path:filename>")(static_files)
# map_bp.route("/api/parking-lots")(get_parking_lots)