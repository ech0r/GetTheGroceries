from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from decimal import *

app = Flask(__name__)
app.debug = True

#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'yourpasswordhere'
app.config['MYSQL_DB'] = 'MealPlanner'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#init MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['Get', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #create cursor
        cur = mysql.connection.cursor()

        #get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #get stored hash
            data = cur.fetchone()
            password = data['password']

            #compare passwords
            if sha256_crypt.verify(password_candidate,password):
                #passed login
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Login'
                return render_template('login.html', error=error)

            #close sql connection
            cur.close()

        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

#check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

# Recipe Form Class
class RecipeForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    description = TextAreaField('Description', [validators.Length(min=30)])
    ingredient = StringField('Ingredient', [validators.Length(min=1, max=200)])
    amount = StringField('Amount', [validators.Length(min=1, max=5)])
    unit = SelectField(u'Unit of Measurement', choices=[('kg', 'kg'),
                                                        ('g', 'g'),
                                                        ('ml', 'ml'),
                                                        ('L', 'L'),
                                                        ('lb', 'lb'),
                                                        ('Tblsp', 'Tblsp'),
                                                        ('tsp', 'tsp'),
                                                        ('cup', 'cup'),
                                                        ('box', 'box'),
                                                        ('jar', 'jar'),
                                                        ('pkg', 'pkg')
                                                        ])

@app.route('/add_recipe', methods=['GET','POST'])
@is_logged_in
def add_recipe():
    form = RecipeForm(request.form)
    if request.method == 'POST' and form.validate():
        user = session['username']
        title = form.title.data
        description = form.description.data
        ingredient = form.ingredient.data
        amount = form.amount.data
        unit = form.amount.data

        #create cursor
        cur = mysql.connection.cursor()

        #execute
        cur.execute("""SELECT user_id FROM users WHERE username = %s""", [user])
        user_id = cur.fetchone()
        cur.execute("""INSERT INTO recipes(user_id, title, description) VALUES(%s, %s, %s)""", (int(user_id['user_id']), title, description))
        mysql.connection.commit()
        cur.execute("""SELECT recipe_id FROM recipes WHERE title = %s""", [title])
        recipe_id = cur.fetchone()
        cur.execute("""INSERT INTO ingredients(user_id, recipe_id, name, amount, unit) VALUES(%s, %s, %s, %s, %s)""", (int(user_id['user_id']), int(recipe_id['recipe_id']), ingredient, Decimal(amount), unit))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()

        flash('Recipe Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_recipe.html', form=form)



if __name__ == '__main__':
    app.secret_key='thisiswherethesecrekeygoes'
    app.run()