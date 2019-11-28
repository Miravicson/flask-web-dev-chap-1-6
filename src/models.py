def create_models():

    from app import db

    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(64), unique=True)
        users = db.relationship('User', backref='role', lazy='dynamic')

        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return f'<Role {self.name!r}>'

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(64), unique=True, index=True)
        firstname = db.Column(db.Unicode)
        lastname = db.Column(db.Unicode)
        role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

        def __init__(self, username, role_id=None, role=None):
            self.username = username,
            self.role_id = role_id

        def __repr__(self):
            return f'<User {self.username!r}>'

    return Role, User
