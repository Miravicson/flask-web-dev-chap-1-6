from threading import Thread
from flask import render_template, Flask
from flask_mail import Message, Mail


class EmailService:
    def __init__(self, app, mail):
        assert isinstance(app, Flask), "App must be a flask application"
        assert isinstance(mail, Mail), "App must be an instance of flask_mail"
        self.app = app
        self.mail = mail

    def send_async_email(self, msg):
        with self.app.app_context():
            self.mail.send(msg)

    def send_email(self, to, subject, template, **kwargs):
        msg = Message(
            self.app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
            sender=self.app.config['FLASKY_MAIL_SENDER'],
            recipients=[to])
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        thr = Thread(target=self.send_async_email, args=[msg])
        thr.start()
        return thr
