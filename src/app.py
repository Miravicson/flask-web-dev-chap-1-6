import os
from flask import (Flask,
                   request,
                   current_app,
                   g,
                   session,
                   jsonify,
                   make_response,
                   render_template,
                   redirect,
                   url_for,
                   session,
                   flash)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from variables import mydict, mylist, myintvar, myobj
from forms import NameForm
from emails import EmailService
from models import create_models

from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SECRET_KEY'] = 'HARDtoGuessString'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False if os.environ.get(
    'TRACK_MODIFICATIONS') == 0 else True

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT', '25')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = 'FROM FLASKY:'
app.config['FLASKY_MAIL_SENDER'] = 'Victor'
app.config['FLASKY_ADMIN'] = 'victorughonu95@gmail.com'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
mail = Mail(app)
mails = EmailService(app, mail)

# import all the models here

Role, User = create_models()


# Routes and view functions


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, mail=mail)


@app.before_request
def initiate_user():
    user = {
        "name": "Victor Ughonu",
        "age": 24
    }
    g.user = user


@app.route('/', methods=['GET', 'POST'])
def index():
    print(request)
    print(current_app)
    if (request.method == 'POST'):
        # response = {}
        # response['json'] = request.json
        # response['args'] = request.args
        # response['form'] = request.form
        # response['files'] = request.files
        # response['values'] = request.values
        # response = request.environ
        # print(response)

        response = make_response({"name": "victor"})
        response.status_code = 201
        response.content_type = 'Application/json'
        response.set_cookie('name', 'victor')
        return render_template('index.html',
                               mydict=mydict,
                               mylist=mylist,
                               myintvar=myintvar,
                               myobj=myobj
                               )
    return f"<h1>Hello world!:\n Your userAgent is: {request.headers.get('User-Agent')}</h1>"

# registering a view function using app.add_url_rule


def index2():
    return '<h1>Hello world! From index2</h1>'


app.add_url_rule('/2', 'index2', index2)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/images')
def images():
    image_url = url_for('static', filename='images/1.png')
    return redirect(image_url)


@app.route('/form', methods=['GET', 'POST'])
def form_view():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('form.html', form=form, name=name)


@app.route('/form2', methods=['GET', 'POST'])
def form_view2():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('form_view2'))
    return render_template('form.html', form=form, name=session.get('name'))


@app.route('/form-db', methods=['GET', 'POST'])
def form_db():
    """ Render a form for username and save the user name to a db """
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('form_db'))
    return render_template('form.html',
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False))


@app.route('/form-email', methods=['GET', 'POST'])
def form_email():
    form = NameForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                email_job = mails.send_email(
                    app.config['FLASKY_ADMIN'],
                    'New User',
                    'mail/new_user',
                    user=user
                )
                print("email_job", email_job)
        else:
            session['known'] = True
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('form_email'))

    return render_template('form.html',
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False))


@app.route('/user/<int:age>')
def user_age(age):

    return f'<h1> Hello your age is {age}</h1>'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
