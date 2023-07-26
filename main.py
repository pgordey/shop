import binascii
import hashlib
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, validators
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
import os
from FDataBase import FDataBase

DATABASE = '/tmp/site.db'
DEBUG = True
SECRET_KEY = 'fhgfdjrt45y3654h'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)

app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'site.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'site.db')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class RegisterForm(FlaskForm):
    name = StringField('Name', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/general')
def general():
    return render_template('general.html')


@app.route('/check')
def check():
    user = User.query.filter_by(email='omofuh@mail.ru').first()
    if user:
        return f'The user with email {user.email} already exists!'
    else:
        return 'The user does not exist'


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if len(name) > 4 and len(email) > 4 and len(password) > 4 and password == confirm_password:
            # хешируем пароль для сохранения в базе данных
            salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
            password_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
            password_hash = binascii.hexlify(password_hash)

            # добавляем пользователя в базу данных
            if dbase.addUser(name, email, password_hash, salt):
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm(request.form)
#     if request.method == 'POST' and form.validate():
#         name = form.name.data
#         email = form.email.data
#         password = form.password.data
#
#         new_user = User(name=name, email=email, password=password)
#         db.session.add(new_user)
#         db.session.commit()
#
#         return redirect(url_for('profile'))
#
#     return render_template('register.html', form=form)


# @app.route('/register_handler', methods = ['POST'])
# def reg_hand():
#     email = request.form['email']
#     password = request.form['password']
#     confirm_password = request.form['confirm_password']
#     if password == confirm_password:
#         db = SQLighter('site.db')
#         db.add_user(email, password)
#         return redirect('/profile')
#     else:
#         return redirect('/register')


@app.route('/profile')
# @login_required
def profile():
    return render_template('profile.html')  # user=current_user)


if __name__ == "__main__":
    app.run(debug=True)
