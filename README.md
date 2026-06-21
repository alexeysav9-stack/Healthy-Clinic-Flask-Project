# Healthy Clinic Flask Project

Веб-приложение частной клиники, разработанное на Python с использованием Flask в качестве итогового проекта за первый курс колледжа.

## Возможности

* Регистрация и авторизация пользователей
* Личный кабинет пациента
* Запись на приём к врачу
* Просмотр информации о врачах и услугах
* Административная панель
* Работа с базой данных
* Защита форм от CSRF-атак

## Технологии

* Python 3
* Flask
* Flask-WTF
* SQLAlchemy
* SQLite
* Jinja2
* HTML5
* CSS3
* JavaScript

# Скриншоты

### Главная страница
<img width="1903" height="4019" alt="изображение" src="https://github.com/user-attachments/assets/f8a4c5ba-14dc-4687-9a8f-048f4a5fed14" />

### Страница регистрации
<img width="1903" height="1180" alt="изображение" src="https://github.com/user-attachments/assets/c9151223-3ff4-4dbb-b728-418b84191c81" />

### Личный кабинет
<img width="1903" height="1180" alt="изображение" src="https://github.com/user-attachments/assets/13d7dad7-c1b3-40b1-8713-103be238acc3" />

### Панель администратора
<img width="1903" height="1180" alt="изображение" src="https://github.com/user-attachments/assets/c30d3a7a-9e0c-4903-ad8e-b2967a7a0a54" />

### Страница с врачами
<img width="1903" height="2222" alt="изображение" src="https://github.com/user-attachments/assets/e965ac33-1624-4b65-b3fa-a32647c0b231" />

### Запись к врачу
<img width="1903" height="1180" alt="изображение" src="https://github.com/user-attachments/assets/52309f8d-a938-47b2-9094-8841690163ae" />

### Админ-панель
<img width="1903" height="1180" alt="изображение" src="https://github.com/user-attachments/assets/645d070c-ce39-49ff-80a1-9b570dac2731" />


## Установка и запуск

```bash
git clone https://github.com/alexeysav9-stack/Healthy-Clinic-Flask-Project.git
cd Healthy-Clinic-Flask-Project

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

python app.py
```

После запуска приложение будет доступно по адресу:

```
http://127.0.0.1:5000
```

## Структура проекта
### Краткая:
```text
app/
templates/
static/
instance/
forms.py
models.py
app.py
requirements.txt
```
### Полная:
<img width="261" height="847" alt="изображение" src="https://github.com/user-attachments/assets/6b973a9a-f646-4173-a6db-c530454c0c7d" />


## Чему я научился

Во время разработки проекта я изучил:

* основы веб-разработки на Flask;
* работу с маршрутами и шаблонами;
* взаимодействие с базой данных через SQLAlchemy;
* систему аутентификации пользователей;
* защиту форм с от CSRF-атак;
* организацию структуры веб-приложения;
* основы использования Git и GitHub.

## Автор

Савельев Алексей Вячеславович

Учебный проект, 2026 год.
