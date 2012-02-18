from bson.objectid import ObjectId
from flask import Flask, render_template, flash, redirect
from flaskext.login import LoginManager, login_required, login_user, logout_user

import settings
from db import users, comics, Comic, User
from forms import LoginForm

app = Flask(__name__)

app.secret_key = settings.SECRET_KEY

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

#views
@app.route('/')
@login_required
def hello():
    results = [comic for comic in comics.find()]
    return render_template('index.html', comics_list=results)

@app.route('/comic/<id>')
@login_required
def view_comic(id):
    comic = Comic.objects(id=id).first()
    comic.read = True
    comic.save()
    return render_template('comic.html', images=comic.image_filenames)

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
