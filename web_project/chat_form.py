from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class ChatForm(FlaskForm):
    text = TextAreaField('Сообщение')
    submit = SubmitField('Отправить')
