from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from os  import environ

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile(".env")
SECRET_KEY = environ.get('SECRET_KEY')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
flask_bcrypt = Bcrypt(app)
from models import Blog, User


@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(id=session['user_id']).first()
    blog_posts = Blog.query.filter_by(user_id=user.id).all()
    return render_template('index.html', user=user, blog_posts=blog_posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form['username']
        user = User.query.filter_by(username=email).first()
        password= request.form['password']

        if user is not None and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = flask_bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(username=username, password_hash=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']

        new_post = Blog(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('create.html')


@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
def update(post_id):
    post = Blog.query.get(post_id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('update.html', post=post)


@app.route('/delete/<int:post_id>')
def delete(post_id):
    post = Blog.query.get(post_id)
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
