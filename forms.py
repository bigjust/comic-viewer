from flaskext.wtf import Form, TextField, validators, PasswordField

from db import User

class LoginForm(Form):
    admin = TextField('Admin', [validators.Required()])
    password = PasswordField('Password', [])

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        print self.admin
        user = User(self.admin.data)
        if user is None:
            self.admin.errors.append('Unknown admin')
            return False

        if not user.check_password(self.password.data):
           self.password.errors.append('Invalid password')
           return False

        return True
