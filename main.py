from bson.objectid import ObjectId
from flask import Flask, render_template, flash, redirect
from flaskext.login import LoginManager, login_required, login_user, logout_user

import settings
import util
from db import users, comics, Comic
from models import User
from forms import LoginForm

app = Flask(__name__)

app.secret_key = util.SECRET_KEY

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.session_protection = None
login_manager.setup_app(app)


@login_manager.user_loader
def load_user(userid):
    result = users.find_one({'_id': ObjectId(userid)})
    if result:
        user = User(result)
    return user

# utility functions
def getComicUrls(comic):
    files = []

    for i in range(1, comic['page_count'] + 1):
        seq = '%(num)03d' % {'num':i}
        filename = '%s_%s.jpg' % (str(comic['_id']), seq)
        files.append(filename)

    return files

#views
@app.route('/')
@login_required
def hello():
    results = [comic for comic in comics.find()]
    return render_template('index.html', comics_list=results)

@app.route('/comic/<id>')
@login_required
def view_comic(id):
    comic = comics.find_one({'_id': ObjectId(id)})
    Comic.objects(id=ObjectId(id)).update_one(set__read=True)
    return render_template('comic.html', images=getComicUrls(comic))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User(form.admin.data)
        login_user(user)
        flash("Logged in successfully.")

        return redirect('/')
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')

if __name__ == "__main__":
    app.debug = settings.DEBUG
    app.run()
