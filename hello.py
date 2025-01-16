import os
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

class NameForm(FlaskForm):
    name = StringField('Cadastre a nova disciplina e o semestre associado:', validators=[DataRequired()])
    semester = RadioField('Selecione o semestre:', choices=[
        ('1º semestre', '1º semestre'),
        ('2º semestre', '2º semestre'),
        ('3º semestre', '3º semestre'),
        ('4º semestre', '4º semestre'),
        ('5º semestre', '5º semestre'),
        ('6º semestre', '6º semestre')
    ], validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
     return render_template('index.html', current_time=datetime.utcnow())

@app.route('/ocorrencias')
def ocorrencias():
     return render_template('ocorrencias.html', current_time=datetime.utcnow())

@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():
    form = NameForm()
    user_all = User.query.all()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user_role = Role.query.filter_by(name=form.semester.data).first()
            if not user_role:
                user_role = Role(name=form.semester.data)
                db.session.add(user_role)
                db.session.commit()
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        session['semester'] = form.semester.data
        return redirect(url_for('disciplinas'))
    return render_template('disciplinas.html', form=form, name=session.get('name'),
                           known=session.get('known', False),
                           user_all=user_all)
