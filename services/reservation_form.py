from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email

class ReservationForm(FlaskForm):
    email = EmailField('이메일', validators=[
        DataRequired('이메일은 필수 입력 항목입니다.'),
        Email('유효한 이메일 주소를 입력하세요.')
    ])
    submit = SubmitField('예약 완료')