import datetime

from bson.objectid import ObjectId
from flask import Flask, render_template, flash, redirect, request, session
from flaskext.login import LoginManager, login_required, login_user, logout_user

import settings
from db import users, Comic, User, Bookmark
from forms import LoginForm
from mongoengine import *

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
    objects = Comic.objects.all()
    results = []

    for result in objects:
        try:
            bookmark = Bookmark.objects.get(comic=str(result.id), user=session['user_id'])
            if bookmark.page == result.page_count:
                result.read_status = 'completed'
            else:
                result.read_status = 'started'
        except Bookmark.DoesNotExist:
            result.read_status = 'unread'

        results.append(result)

    recent_comics = Comic.objects.filter(id__in=[b.comic for b in Bookmark.objects.filter(updated__exists=True).only('comic').order_by('-updated')[:5]])

    return render_template('index.html', comics_list=results, recent=recent_comics)

@app.route('/comic/<id>')
@login_required
def view_comic(id):
    comic = Comic.objects(id=id).first()
    bookmark, _ = Bookmark.objects.get_or_create(comic=id, user=session['user_id'])
    return render_template('comic.html', images=comic.image_filenames, page=bookmark.page, comic_id=id)

@app.route('/bookmark')
@login_required
def update_bookmark():
    comic_id = request.args.get('comic_id', '', type=str)
    page = request.args.get('page', 0, type=int)
    bookmark, _ = Bookmark.objects.get_or_create(comic=comic_id, user=session['user_id'])
    bookmark.page = page
    bookmark.updated = datetime.datetime.now()
    bookmark.save()
    return "success"

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
