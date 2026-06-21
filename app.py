from flask import Flask, render_template, redirect, url_for, flash, abort, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import date, time, datetime
from sqlalchemy import or_, and_

from config import Config
from models import db, User, Doctor, Appointment, Post, Branch, Slot
from forms import RegisterForm, LoginForm, CreateDoctorForm, AppointmentForm, PostForm, BranchForm, CreateSlotForm

from dotenv import load_dotenv
load_dotenv()

import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/')
def index():
    posts = Post.query\
        .filter_by(is_published=True)\
        .order_by(Post.created_at.desc())\
        .limit(3)\
        .all()
    return render_template('index.html', posts=posts)


@app.route('/about')
def about():
    branches = Branch.query.all()
    return render_template('about.html', branches=branches)


@app.route('/doctors')
def doctors():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)


@app.route('/doctor/<int:doctor_id>')
def doctor_detail(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template('doctor_detail.html', doctor=doctor)


@app.route('/profile')
@login_required
def profile():
    if current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        return render_template('profile.html', doctor=doctor)
    elif current_user.role == 'admin':
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('appointments'))


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')



# Создание маршрута для записи на прием к врачу
@app.route('/doctor/<int:doctor_id>/book', methods=['GET', 'POST'])
@login_required # Требуем авторизацию для записи на прием
def book_appointment(doctor_id):
    # Получаем врача по ID или возвращаем 404, если не найден
    doctor = Doctor.query.get_or_404(doctor_id)
    # Создаем экземпляр формы записи на прием
    form = AppointmentForm()
    # Получаем все доступные слоты для данного врача, которые не заняты
    # и сортируем их по дате и времени, не показывая слоты из прошлого
    available_slots = Slot.query.filter(
        Slot.doctor_id == doctor.id,
        Slot.is_booked == False,
        or_(Slot.date > date.today(),
            and_(
                Slot.date == date.today(),
                Slot.time >= datetime.now().time()
            )
        )
    ).order_by(
        Slot.date, Slot.time
    ).all()
    # Заполняем выпадающий список формы доступными слотами
    form.slot.choices = [
        (
            slot.id,
            f'{slot.date.strftime("%d.%m.%Y")} — {slot.time.strftime("%H:%M")}'
        )
        for slot in available_slots
    ]
    # Обрабатываем отправку формы
    if form.validate_on_submit():

        slot = db.session.get(Slot, form.slot.data)

        if not slot or slot.is_booked:
            flash('Слот уже занят', 'danger')

            return redirect(
                url_for(
                    'book_appointment',
                    doctor_id=doctor.id
                )
            )
        # Создаем новую запись на прием с данными из 
        # формы и текущим пользователем
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor.id,
            date=slot.date,
            time=slot.time,
            comment=form.comment.data
        )
        # Отмечаем слот как занятый
        slot.is_booked = True
        # Сохраняем запись на прием и обновление слота в базе данных
        db.session.add(appointment)
        db.session.commit()
        # Перенаправляем на страницу врача
        return redirect(
            url_for(
                'doctor_detail',
                doctor_id=doctor.id
            )
        )
    # Если форма не прошла валидацию или это GET-запрос, 
    # отображаем страницу записи на прием с формой и информацией о враче
    return render_template(
        'book_appointment.html',
        form=form,
        doctor=doctor
    )


@app.route('/doctor/<int:doctor_id>/create_slot', methods=['GET', 'POST'])
@login_required
def create_slot(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)

    form = CreateSlotForm()

    if form.validate_on_submit():

        existing_slot = Slot.query.filter_by(
            doctor_id=doctor.id,
            date=form.date.data,
            time=form.time.data
        ).first()

        if existing_slot:
            flash('Такой слот уже существует', 'danger')
            return redirect(url_for('create_slot', doctor_id=doctor.id))
        

        slot = Slot(
            doctor_id=doctor.id,
            date=form.date.data,
            time=form.time.data
        )

        db.session.add(slot)
        db.session.commit()

        flash('Слот создан', 'success')

        return redirect(
            url_for(
                'create_slot',
                doctor_id=doctor.id
            )
        )

    return render_template(
        'create_slot.html',
        form=form,
        doctor=doctor
    )


@app.route('/appointments')
@login_required
def appointments():

    if current_user.role != 'patient':
        abort(403)

    user_appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(
        Appointment.date,
        Appointment.time
    ).all()
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    return render_template('appointments.html', appointments=user_appointments)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Эта почта уже занята", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(form.password.data)

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            patronymic=form.patronymic.data,
            email=form.email.data,
            password_hash=hashed_password,
            role="patient"
        )

        db.session.add(user)
        db.session.commit()

        flash("Регистрация успешна", "success")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/doctor/appointments')
@login_required
def doctor_appointments():

    if current_user.role != 'doctor':
        abort(403)

    doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()

    appointments = Appointment.query.filter_by(
        doctor_id=doctor.id
    ).order_by(
        Appointment.date,
        Appointment.time
    ).all()

    return render_template(
        'doctor_appointments.html',
        appointments=appointments,
        doctor=doctor
    )





@app.route('/appointment/<int:id>/approve')
@login_required
def approve_appointment(id):

    appointment = Appointment.query.get_or_404(id)

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()

    if not doctor or appointment.doctor_id != doctor.id:
        abort(403)

    appointment.status = 'approved'
    db.session.commit()

    flash("Запись подтверждена")
    return redirect(url_for('doctor_appointments'))


@app.route('/appointment/<int:id>/reject')
@login_required
def reject_appointment(id):

    appointment = Appointment.query.get_or_404(id)

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()

    if not doctor or appointment.doctor_id != doctor.id:
        abort(403)

    appointment.status = 'rejected'
    db.session.commit()

    flash("Запись отклонена")
    return redirect(url_for('doctor_appointments'))


# Создаем маршрут для входа в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # Проверяем отправку формы и корректность данных
    if form.validate_on_submit():
        # Ищем пользователя по email
        user = User.query.filter_by(email=form.email.data).first()

        # Если пользователь не найден:
        if not user:
            flash('Пользователь с таким email не найден', 'danger')
            return redirect(url_for('login'))

        # Если введен неверный пароль:
        if not check_password_hash(user.password_hash, form.password.data):
            flash('Неверный пароль', 'danger')
            return redirect(url_for('login'))

        # Все проверки пройдены, выполняем вход:
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    # Если форма не прошла валидацию, отображаем страницу входа
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из аккаунта', 'success')
    return redirect(url_for('login'))


@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        abort(403)

    return render_template('admin.html')


@app.route('/admin/create_doctor', methods=['GET', 'POST'])
@login_required
def create_doctor():
    if current_user.role != 'admin':
        abort(403)

    form = CreateDoctorForm()

    if form.validate_on_submit():
        print(form.errors)

        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email уже используется", 'danger')
            return redirect(url_for('create_doctor'))

        file = form.photo.data
        filename = None

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            patronymic=form.patronymic.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role="doctor"
        )

        db.session.add(user)
        db.session.commit()

        doctor = Doctor(
            user_id=user.id,
            specialization=form.specialization.data,
            description=form.description.data,
            photo=filename
        )

        db.session.add(doctor)
        db.session.commit()

        flash("Врач создан")
        return redirect(url_for('create_doctor'))

    return render_template("create_doctor.html", form=form)


@app.route('/admin/delete_doctor/<int:doctor_id>', methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    if current_user.role != 'admin':
        abort(403)

    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user

    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()

    flash("Врач удалён", "success")
    return redirect(url_for('doctors'))


@app.route('/admin/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(doctor_id):
    if current_user.role != 'admin':
        abort(403)

    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user

    form = CreateDoctorForm(obj=doctor)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.patronymic = form.patronymic.data
        user.email = form.email.data

        doctor.specialization = form.specialization.data
        doctor.description = form.description.data

        db.session.commit()

        flash("Врач обновлён", "success")
        return redirect(url_for('doctor_detail', doctor_id=doctor.id))

    return render_template('edit_doctor.html', form=form, doctor=doctor)


@app.route('/admin/create_branch', methods=['GET', 'POST'])
@login_required
def create_branch():
    if current_user.role != 'admin':
        abort(403)

    form = BranchForm()

    if form.validate_on_submit():
        file = form.branch_photo.data

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            filename = None

        branch = Branch(
            name=form.name.data,
            address=form.address.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            working_hours=form.working_hours.data,
            branch_photo=filename
        )

        db.session.add(branch)
        db.session.commit()

        flash("Филиал создан", "success")
        return redirect(url_for('about'))

    return render_template('create_branch.html', form=form)


@app.route('/admin/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    if not current_user.role == 'admin':
        abort(403)

    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')

        db.session.commit()
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('admin/edit_post.html', post=post)


@app.route('/admin/posts/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    if not current_user.role == 'admin':
        abort(403)

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('posts'))


@app.route('/admin/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if not current_user.role == 'admin':
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        file = form.image.data

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            filename = None
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author_name=form.author_name.data,
            image=filename
        )

        
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('posts'))

    return render_template('create_post.html', form=form)


@app.route('/posts')
def posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('posts.html', posts=posts)


@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)






@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
