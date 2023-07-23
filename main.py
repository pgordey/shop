import app as app
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

from flask import request, current_app



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)
    text = db.Column(db.Text, nullable=False)



class registration(db.Model):
    sr_firstname = db.Column(db.Integer, primary_key=True)
    sr_lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.Integer, nullable=False)
    password = db.Column(db.Boolean, default=True)


@app.route('/')
def index():
        return render_template('index.html',)


@app.route('/general')
def general():
        return render_template('general.html',)




@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == "POST":
        sr_firstname = request.form['sr_firstname']
        sr_lastname = request.form['sr_lastname']
        email = request.form['email']
        password = request.form['password']

        registration = required(sr_firstname=sr_firstname, sr_lastname=sr_lastname, email=email, password=password)

        try:
            db.session.add(registration)
            db.session.commit()
            return redirect('/')
        except:
            return 'Ошибка'
    else:
        return render_template("registration.html")

        return render_template('registration.html',)




@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']

        item = Item(title=title, price=price)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Получилась ошибка"


    else:
        return render_template('create.html')

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(debug=True)