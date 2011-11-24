from flaskext.wtf import Form, TextField, validators

from db import users

class LoginForm(Form):
    admin = TextField('Admin', [validators.Required()])
#    password = PasswordField('Password', [])

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        print self.admin
        admin = users.find_one({'login': self.admin.data})
        if admin is None:
            self.admin.errors.append('Unknown admin')
            return False

#        if not admin.check_password(self.password.data):
#            self.password.errors.append('Invalid password')
#            return False

        self.admin = admin
        return True
