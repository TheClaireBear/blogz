from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

db_name = 'blogs'
db_user = 'blogs'
db_pass = 'passwords'


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogs:abc123@localhost:8889/blogs'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'abc123'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return self.username

def validate_username(username):
    if len(username) >= 3 and len(username) < 20:
        if " " not in username:
            return False
        else:
            username_error = True
            flash('Spaces are not allowed in username!', 'error')
            username = ''
            return username_error
    else:
        username_error = True
        flash('Username must be between 3 and 20 characters long!', 'error')
        username = ""
        return username_error

def validate_password(password, verify):
    if len(password) >= 3 and len(password) <= 20:
        if " " not in password:
            if password == verify:
                return False
            else:
                password_error = True
                flash('Passwords do not match!', 'error')
                return password_error
        else:
            password_error = True
            flash('Spaces are not allowed in password!', 'error')
            return password_error
    else:
        password_error = True
        flash('Password must be between 3 and 20 characters long!', 'error')
        return password_error

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        username_error = validate_username(username)
        password_error = validate_password(password, verify)

        if not username_error and not password_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('This user already exists', 'error')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/newpost', methods=['GET', 'POST'])
def new_blog():

    return render_template('newpost.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args.get('id'):
        id = request.args.get('id')
        blog = Blog.query.get(id)
        title = blog.title
        body = blog.body
        return render_template('individual.html', title=title, body=body)
    if request.args.get('user'):
        user_id = request.args.get('user')
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleuser.html', blogs=blogs)
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog = request.form['blog']
        owner = User.query.filter_by(username=session['username']).first()
        if not blog or not blog_title:
            flash('enter a title or a body', 'error')
            return render_template('newpost.html')
        else:
            new_blog = Blog(blog_title, blog, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
    
    blogs = Blog.query.all()
    users = User.query.all()

    return render_template('blog.html', blogs=blogs, users=users)


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


if __name__=='__main__':
    app.run()