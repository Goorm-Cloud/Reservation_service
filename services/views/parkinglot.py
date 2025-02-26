from flask import render_template, request
from services.common.models import db, ParkingLot

def parking_lots():
    """
    주차장 목록을 가져와서 템플릿에 전달하는 함수
    """
    page = request.args.get('page', 1, type=int)
    per_page = 8  # 한 페이지당 표시할 주차장 개수
    parking_lots = ParkingLot.query.with_entities(
        ParkingLot.parkinglot_id,
        ParkingLot.parkinglot_name,
        ParkingLot.parkinglot_add,
        ParkingLot.parkinglot_type,
        ParkingLot.parkinglot_cost
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('parking_lots.html', parking_lots=parking_lots)

def parking_lot_detail(parkinglot_id):
    """
    특정 주차장의 상세 정보를 가져와 템플릿에 전달하는 함수
    """
    parking_lot = db.session.query(
        ParkingLot.parkinglot_id,
        ParkingLot.parkinglot_name,
        ParkingLot.parkinglot_add,
        ParkingLot.parkinglot_type,
        ParkingLot.parkinglot_cost
    ).filter_by(parkinglot_id=parkinglot_id).first()

    if not parking_lot:
        return "주차장을 찾을 수 없습니다.", 404

    return render_template('parking_lot_detail.html', parking_lot=parking_lot)