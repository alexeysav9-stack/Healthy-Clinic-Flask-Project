from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    FileField,
    DateField,
    TimeField,
    SelectField,
)
from wtforms.validators import DataRequired, Email


class RegisterForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Войти')


class CreateDoctorForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    specialization = StringField("Специальность", validators=[DataRequired()])
    description = TextAreaField("Описание")
    photo = FileField('Фото', validators=[FileAllowed(['jpg', 'png'])])


class CreateSlotForm(FlaskForm):

    date = DateField(
        'Дата',
        format='%Y-%m-%d'
    )

    time = TimeField(
        'Время'
    )

    submit = SubmitField('Создать слот')


class AppointmentForm(FlaskForm):
    slot = SelectField('Доступное время',coerce=int)
    comment = TextAreaField('Комментарий')
    submit = SubmitField('Записаться')


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    author_name = StringField('Автор')
    image = FileField('Изображение', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Создать')


class BranchForm(FlaskForm):
    name = StringField('Название филиала', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    working_hours = StringField('Рабочие часы', validators=[DataRequired()])
    branch_photo = FileField('Фото филиала', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Добавить филиал')