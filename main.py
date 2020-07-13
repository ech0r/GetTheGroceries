from flask import Flask, render_template, flash, redirect, url_for, session, request, make_response
from flask_mail import Mail, Message
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import pbkdf2_sha256
from functools import wraps
from flask_recaptcha import ReCaptcha
import MySQLdb
import random
import json
import secrets
import time


app = Flask(__name__)
app.secret_key = secrets.secret_key
recaptcha = ReCaptcha(app=app)
recaptcha.site_key = secrets.recaptcha_sitekey
recaptcha.secret_key = secrets.recaptcha_secretkey
recaptcha.is_enabled = True
recaptcha.theme = 'light'
recaptcha.type = 'image'
recaptcha.size = 'normal'
recaptcha.tabindex = 0
app.debug = True

# password crypto
pepper = secrets.pepper

# email stuff
app.config.update(dict(
    MAIL_SERVER = 'smtp.googlemail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'getthegroceries.io',
    MAIL_PASSWORD = secrets.email_password
))

mail = Mail(app)

# Init MySQL
def my_sql_init():
    connection = MySQLdb.connect(host="mysql-docker", user=secrets.db_user, passwd=secrets.db_password)
    cursor = connection.cursor()
    cursor.execute("USE " + secrets.db_name)
    return cursor, connection

def my_sql_close(connection,cursor):
    cursor.close()
    connection.close()

# Initialize db connection and verify schema
connection = MySQLdb.connect(host="mysql-docker", user=secrets.db_user, passwd=secrets.db_password)

cursor = connection.cursor()
sql0 = secrets.sql0
sql1 = secrets.sql1
sql2 = secrets.sql2
sql3 = secrets.sql3
sql4 = secrets.sql4
sql5 = secrets.sql5

#Execute MySQL setup
cursor.execute(sql0)
cursor.execute(sql1)
cursor.execute(sql2)
cursor.execute(sql3)
cursor.execute(sql4)
cursor.execute(sql5)

my_sql_close(connection,cursor)

#Classes
class Recipe:
    def __init__(self, recipe_id, user_id, name, description, ingredients, amounts, units):
        self.id = recipe_id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.ingredients = []
        self.amounts = []
        self.units = []
        for loc, ingredient in enumerate(ingredients):
            self.addingredient(ingredient, amounts[loc], units[loc])
    def addingredient(self,ingredient,amount,unit):
            self.ingredients.append(ingredient)
            self.amounts.append(amount)
            self.units.append(unit)

class AccountForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


class RecipeForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    description = TextAreaField('Description', [validators.Length(min=10)])


# Functions
# decorators
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

def get_all_recipes(user_id):
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    recipe_query = "SELECT * FROM recipes WHERE user_id = %s"
    ingredient_query = "SELECT * FROM ingredients where recipe_id = %s"
    cursor.execute(recipe_query, [user_id])
    cursor.fetchall()
    recipes = {}
    #iterate through recipes
    for row in cursor:
        #create new cursor object to do ingredient queries
        cursor2 = connection.cursor()
        cursor2.execute(ingredient_query,[row[0]])
        cursor2.fetchall()
        ingredient_list = []
        amount_list = []
        unit_list = []
        for ingredient in cursor2:
            ingredient_list.append(ingredient[3])
            amount_list.append(ingredient[4])
            unit_list.append(ingredient[5])
        cursor2.close()
        recipes[row[0]] = Recipe(row[0], row[1], row[2], row[3], ingredient_list, amount_list, unit_list)
    my_sql_close(connection,cursor)
    return recipes


def reverse_string(str):
    return str[::-1]


def recoverykey():
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_[]<>?>+=/*.,!@#$%^&()~'
    string = ""
    for i in range(random.randint(20,50)):
        string += random.choice(characters)
        hashy = pbkdf2_sha256.hash(string)
        return hashy[21:]


def encrypt(password, username):
    salt = username + reverse_string(username)
    seasonedbeef = salt + password + pepper
    hashy = pbkdf2_sha256.hash(seasonedbeef)
    return hashy


def userReport():
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    getnumberofusers = "SELECT * FROM verifiedusers"
    cursor.execute(getnumberofusers)
    numberofusers = str(len(cursor.fetchall()))
    message = "There are now " +  numberofusers + " users using GetTheGroceries\n\nAwesome!"
    subject = "USER REPORT: GetTheGroceries has a new user!"
    msg = Message(subject=subject, body=message, sender='getthegroceries.io@gmail.com', recipients=['getthegroceries.io@gmail.com'])
    mail.send(msg)
    my_sql_close(connection,cursor)


def passwordverify(username, storedhash, password_candidate):
    salt = username + reverse_string(username)
    password_candidate = salt + password_candidate + pepper
    if pbkdf2_sha256.verify(password_candidate, storedhash):
        return True
    else:
        return False


# Flask routes
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/delete_recipe', methods=['GET'])
@is_logged_in
def delete_recipe():
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    recipe_id = request.args.get('recipe')
    deletesql = "DELETE r.*, i.* FROM recipes r INNER JOIN ingredients i WHERE r.recipe_id=i.recipe_id AND r.recipe_id=%s AND r.user_id=(SELECT id FROM verifiedusers WHERE username=%s)"
    affected_count = cursor.execute(deletesql, [recipe_id, session['username']])
    connection.commit()
    my_sql_close(connection,cursor)
    if affected_count > 0:
        flash('Recipe deleted', 'success')
    else:
        flash("You're not allowed to delete recipe", 'danger')
    return redirect(url_for('dashboard'))
    

@app.route('/edit_recipe', methods=['GET', 'POST'])
@is_logged_in
def edit_recipe():

    recipe = request.args.get('recipe')
    user = session['username']

    # declare cursor/db connection
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]

    # sql queries
    get_recipe = "SELECT r.title, r.description, i.name, i.amount, i.unit, r.user_id, r.recipe_id FROM recipes r LEFT OUTER JOIN ingredients i ON r.recipe_id = i.recipe_id WHERE r.recipe_id=%s AND r.user_id = (SELECT id FROM verifiedusers WHERE username=%s)" 

    # get recipe
    cursor.execute(get_recipe, [recipe, user])
    # transpose recipe data
    recipe_data = list(map(list, zip(*cursor.fetchall())))
    if not recipe_data:
        flash("You're not allowed to edit this recipe", 'danger')
        return redirect(url_for('dashboard')) 

    # form stuff
    form = RecipeForm(request.form)
    form.title.data = recipe_data[0][0]
    form.description.data = recipe_data[1][0]
    ingredients = recipe_data[2]
    amounts = recipe_data[3]
    units = recipe_data[4]
    user_id = recipe_data[5][0]
    recipe_id = recipe_data[6][0]
    unittype = ['kg', 'g', 'lb', 'oz', 'L', 'mL', 'Tblsp', 'tsp', 'cup', 'quart', 'gallon', 'package', 'jar', 'qty']

    if request.method == 'POST' and form.validate():
        # Get all the form data
        newtitle = request.form['title']
        newdescription = request.form['description'] 
        ingredients = request.form.getlist('ingr_name')
        amounts = request.form.getlist('amount')
        units = request.form.getlist('unit')
        # checks for duplicate recipe 
        cursor.execute("SELECT * FROM recipes WHERE user_id=%s AND title=%s", [user_id, newtitle])
        if (newtitle.lower() == recipe_data[0][0]) or (cursor.fetchall() is None):
            # updates recipe data in SQL tables
            recipeupdate = "UPDATE recipes SET title=%s, description=%s WHERE recipe_id=%s;"
            cursor.execute(recipeupdate, [newtitle, newdescription, recipe_id])
            connection.commit()
            dropoldingredients = "DELETE FROM ingredients WHERE recipe_id=%s"
            cursor.execute(dropoldingredients, [recipe_id])
            connection.commit()
            for i in range(len(ingredients)):
                ingredientinsert = "INSERT INTO ingredients (ingr_id, user_id, recipe_id, name, amount, unit) VALUES (UUID(), %s, %s, %s, %s, %s)"
                cursor.execute(ingredientinsert, [user_id, recipe_id, ingredients[i], amounts[i], units[i]])
            # commit to db
            connection.commit()
            flash('Recipe Updated', 'success')
            my_sql_close(connection,cursor)
            return redirect(url_for('dashboard'))
        else:
            flash('The title "' + newtitle + '" has already been used by you, pick a different title.', 'danger')
            return render_template('edit_recipe.html', form=form, ingredients=ingredients, amounts=amounts, units=units, unittype=unittype)
    else:
        my_sql_close(connection,cursor)
        return render_template('edit_recipe.html', form=form, id=recipe_id, ingredients=ingredients, amounts=amounts, units=units, unittype=unittype)




@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if recaptcha.verify():
            message = request.form['message']
            email = request.form['email']
            subject = "CONTACT FORM: " + request.form['subject']
            message = message + "\n\n\nFROM: " + email
            msg = Message(subject=subject, body=message, sender='getthegroceries.io@gmail.com', recipients=['getthegroceries.io@gmail.com'])
            mail.send(msg)
            flash('Email sent successfully. Thanks for contacting us, we will be in touch soon.', 'success')
        else:
            flash('Make sure recaptcha is completed correctly.', 'danger')
    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        if recaptcha.verify():
            name = request.form['name']
            email = request.form['email']
            username = request.form['username']
            newusernamequery = '''SELECT * FROM newusers WHERE username = %s'''
            newemailquery = '''SELECT * FROM newusers WHERE email = %s'''
            verifiedusernamequery = '''SELECT * FROM verifiedusers WHERE username = %s'''
            verifiedemailquery = '''SELECT * FROM verifiedusers WHERE email = %s'''
            cursor.execute(newusernamequery, [username])
            newusernamedata = cursor.fetchone()
            cursor.execute(newemailquery, [email])
            newemaildata = cursor.fetchone()
            cursor.execute(verifiedusernamequery, [username])
            verifiedusernamedata = cursor.fetchone()
            cursor.execute(verifiedemailquery, [email])
            verifiedemaildata = cursor.fetchone()
            if newemaildata or verifiedemaildata:
                flash("That email is already in use with another account, pick something different.", 'danger')
                my_sql_close(connection,cursor)
                return render_template('register.html', form=form)
            if newusernamedata or verifiedusernamedata:
                flash("That username is already in use, pick something different.", 'danger')
                my_sql_close(connection,cursor)
                return render_template('register.html', form=form)
            else:
                password = encrypt(request.form['password'], username)
                key = recoverykey()
                cursor.execute("INSERT INTO newusers(id, name, email, username, password, confirmation) VALUES(UUID(),%s, %s, %s, %s, %s)", (name, email, username, password, key))
                # Commit to DB
                connection.commit()
                message = "Click the link below to activate your account: \n\n" + "https://getthegroceries.io/confirm?key=" + key + "\n\n\n Thanks, \n\n -GetTheGroceries Team"
                msg = Message(subject="Get The Groceries Account Confirmation", body=message,
                              sender='getthegroceries.io@gmail.com', recipients=[email])
                mail.send(msg)
                flash('You are now registered. Please check your email to activate your account', 'success')
        else:
            flash('Make sure recaptcha is completed correctly.', 'danger')
    my_sql_close(connection,cursor)
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    if request.method == 'POST':
        button = request.form['button']
        if button == 'forgot':
            return redirect(url_for('forgot'))
        if recaptcha.verify():
            # get form fields
            username = request.form['username']
            email = username
            password_candidate = request.form['password']
            # get user by username
            cursor.execute("SELECT * FROM verifiedusers WHERE username = %s OR email = %s", [username, email])
            result = cursor.fetchone()
            cursor.execute("SELECT * FROM newusers WHERE username = %s OR email = %s", [username, email])
            newresult = cursor.fetchone()
            if result:
                # get stored hash
                storedhash = result[4]
                print(storedhash)
                print(result)
                # compare passwords
                if passwordverify(username, storedhash, password_candidate):
                    # passed login
                    session['logged_in'] = True
                    session['username'] = username
                    flash('You are now logged in', 'success')
                    my_sql_close(connection,cursor)
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid Login','danger')
            elif newresult:
                flash('Please activate your account first.','danger')
            else:
                flash('Username Not Found','danger')
        else:
            flash('Make sure recaptcha is completed correctly.', 'danger')
    my_sql_close(connection,cursor)
    return render_template('login.html')


# logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# account confirmation
@app.route('/confirm', methods = ['GET'])
def confirm():
    if request.method == 'GET':
        sqldb = my_sql_init()
        cursor = sqldb[0]
        connection = sqldb[1]
        key = request.args.get('key')
        confirmsql = "SELECT * from newusers WHERE confirmation = %s"
        cursor.execute(confirmsql, [key])
        confirmation = cursor.fetchone()
        if confirmation:
            identity = confirmation[0]
            name = confirmation[1]
            email = confirmation[2]
            username = confirmation[3]
            password = confirmation[4]
            cursor.execute("INSERT INTO verifiedusers(id, name, email, username, password) VALUES(UUID(), %s, %s, %s, %s)",(name, email, username, password))
            cursor.execute("DELETE FROM newusers WHERE id = %s", [identity])
            connection.commit()
            session['logged_in'] = True
            session['username'] = username
            userReport()
            my_sql_close(connection,cursor)
            return redirect(url_for('dashboard'))
        else:
            session.clear()
            flash('Cannot use an old key.', 'danger')
            my_sql_close(connection,cursor)
            return redirect(url_for('index'))
    else:
        session.clear()
        flash("Don't do that. Your IP has been logged.", 'danger')
        my_sql_close(connection,cursor)
        return redirect(url_for('index'))


@app.route('/delete', methods=['GET', 'POST'])
@is_logged_in
def delete():
    if request.method == 'POST':
        deleted = request.form['delete']
        print(delete)
        if deleted == 'delete':
            sqldb = my_sql_init()
            cursor = sqldb[0]
            connection = sqldb[1]
            username = session['username']
            getdetails = "SELECT id, name, email FROM verifiedusers WHERE username = %s"
            cursor.execute(getdetails, [username])
            results = cursor.fetchone()
            identity = results[0]
            deleteaccount = "DELETE FROM verifiedusers WHERE id = %s"
            deleteingredients = "DELETE FROM recipes WHERE user_id = %s"
            deleterecipes = "DELETE FROM ingredients WHERE user_id = %s"
            cursor.execute(deleteaccount, [identity])
            cursor.execute(deleterecipes, [identity])
            cursor.execute(deleteingredients, [identity])
            session.clear()
            connection.commit()
            my_sql_close(connection,cursor)
            error = 'Your Account has been deleted.'
            return render_template('login.html', error=error)
        else:
            error = "You must type 'delete' to delete your account."
            return render_template('delete.html', error=error)
    else:
        return render_template('delete.html')


@app.route('/account', methods=['GET', 'POST'])
@is_logged_in
def account():
    form = AccountForm(request.form)
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    username = session['username']
    getdetails = "SELECT id, name, email FROM verifiedusers WHERE username = %s"
    cursor.execute(getdetails, [username])
    results = cursor.fetchone()
    identity = results[0]
    form.name.data = results[1]
    form.email.data = results[2]
    form.username.data = username
    if request.method == 'POST' and form.validate():
        newname = request.form['name']
        newuser = request.form['username']
        newemail = request.form['email']
        newquery = "SELECT * FROM newusers WHERE username = %s OR email = %s"
        cursor.execute(newquery, [newuser, newemail])
        newdata = cursor.fetchall()
        verifiedquery = "SELECT * FROM verifiedusers WHERE username = %s OR email = %s"
        cursor.execute(verifiedquery, [newuser, newemail])
        verifieddata = cursor.fetchall()
        if verifieddata:
            if verifieddata[0][0] is not identity:
                flash("That email or username is already in use with another account, pick something different.", 'danger')
                my_sql_close(connection,cursor)
                return render_template('account.html', form=form)
        if newdata:
            if newdata[0][0] is not identity:
                flash("That email or username is already in use with another account, pick something different.",'danger')
                my_sql_close(connection,cursor)
                return render_template('account.html', form=form)
        else:
            # encrypt new password
            hashedpassword = encrypt(request.form['password'], username)
            updateuser = "UPDATE verifiedusers SET name = %s, username = %s, email = %s, password = %s WHERE id = %s"
            cursor.execute(updateuser, [newname, newuser, newemail, hashedpassword, identity])
            flash("Profile Updated", 'success')
            connection.commit()
    my_sql_close(connection,cursor)
    return render_template('account.html', form=form)


@app.route('/reset', methods=['GET'])
def reset():
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    if request.method == 'GET':
        # get key from GET request
        key = request.args.get('key')
        getusername = "SELECT username FROM verifiedusers WHERE recovery = %s"
        # find user that corresponds to key
        cursor.execute(getusername, [key])
        username = cursor.fetchone()
        if username:
            session['logged_in'] = True
            session['username'] = username[0]
            deleterecovery = "UPDATE verifiedusers SET recovery = NULL WHERE username = %s"
            cursor.execute(deleterecovery, [username[0]])
            flash("logging you in, redirecting you to account page to reset password", 'success')
            connection.commit()
            my_sql_close(connection,cursor)
            return redirect(url_for('account'))

        else:
            flash("Invalid key, redirecting to login page.", 'danger')
            my_sql_close(connection,cursor)
            return redirect(url_for('login'))



@app.route('/forgot', methods = ['GET', 'POST'])
def forgot():
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    if request.method == 'POST':
        if recaptcha.verify():
            usernamequery = "SELECT id from verifiedusers WHERE username = %s OR email = %s"
            emailuser = request.form['username']
            cursor.execute(usernamequery, [emailuser, emailuser])
            result = cursor.fetchone()
            if result:
                getuseremail = "SELECT email FROM verifiedusers WHERE id = %s"
                cursor.execute(getuseremail, [result])
                email = cursor.fetchone()
                # create recovery key
                key = recoverykey()
                updateuser = "UPDATE verifiedusers SET recovery = %s WHERE id = %s"
                cursor.execute(updateuser, [key, result])
                # send user email with recovery key
                message = "Click here to reset your password: \n\n" + "https://getthegroceries.io/reset?key=" + key + "\n\n\n Thanks, \n\n -GetTheGroceries Team"
                msg = Message(subject="Get The Groceries Password Reset", body=message, sender='getthegroceries.io@gmail.com', recipients=[email[0]])
                mail.send(msg)
                flash("User account exists. Sent email to reset password.", 'success')
                connection.commit()
            else:
                flash("User account does not exist. Try again.", 'danger')
        else:
            flash('Make sure captcha is completed correctly.', 'danger')
    my_sql_close(connection,cursor)
    return render_template('forgot.html')


# dashboard
@app.route('/dashboard', methods = ['GET', 'POST'])
@is_logged_in
def dashboard():
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    user = session['username']
    user_id_query = "SELECT id FROM verifiedusers WHERE username = %s"
    cursor.execute(user_id_query, [user])
    data = cursor.fetchone()
    user_id = data[0]
    recipes = get_all_recipes(user_id)
    my_sql_close(connection,cursor)
    ids = []
    names = []
    descriptions = []
    recipedict = {}
    for i in recipes:
        ids.append(recipes[i].id)
        names.append(recipes[i].name)
        descriptions.append(recipes[i].description)
        list = [recipes[i].ingredients, recipes[i].amounts, recipes[i].units]
        recipedict[recipes[i].name] = list
    recipejson = json.dumps(recipedict)
    return render_template('dashboard.html', ids=ids, names=names, descriptions=descriptions, recipedict=recipejson)


@app.route('/add_recipe', methods=['GET', 'POST'])
@is_logged_in
def add_recipe():
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    form = RecipeForm(request.form)
    units = ['kg', 'g', 'lb', 'oz', 'L', 'mL', 'Tblsp', 'tsp', 'cup', 'quart', 'gallon', 'package', 'jar', 'qty']
    if request.method == 'POST' and form.validate():
        # Get all the form data
        user = session['username']
        title = form.title.data
        description = form.description.data
        ingredients = request.form.getlist('ingr_name')
        amounts = request.form.getlist('amount')
        units = request.form.getlist('unit')
        usernamequery = "SELECT id FROM verifiedusers WHERE username = %s"
        cursor.execute(usernamequery, [user])
        user_id = cursor.fetchone()
        # checks for duplicate recipe names
        cursor.execute("SELECT * FROM recipes WHERE user_id=%s AND title=%s", [user_id, title])
        if cursor.fetchall():
            flash('Recipe title has already been used by you, pick a different title.', 'danger')
            return redirect(url_for('add_recipe'))
        else:
            # insert recipe data into SQL tables
            recipeinsert = "INSERT INTO recipes(recipe_id, user_id, title, description) VALUES(UUID(), %s, %s, %s)"
            cursor.execute(recipeinsert, [user_id[0], title, description])
            connection.commit()
            recipequery = "SELECT recipe_id FROM recipes WHERE title = %s"
            cursor.execute(recipequery, [title])
            recipe_id = cursor.fetchone()
            for i, ingredient in enumerate(ingredients):
                ingredientinsert = "INSERT INTO ingredients(ingr_id, user_id, recipe_id, name, amount, unit) VALUES(UUID(), %s, %s, %s, %s, %s)"
                cursor.execute(ingredientinsert, [user_id[0], recipe_id[0], ingredient, amounts[i], units[i]])
            # commit to db
            connection.commit()
            flash('Recipe Created', 'success')
            my_sql_close(connection,cursor)
            return redirect(url_for('dashboard'))
    else:
        if request.args.get('recipe'):
            recipe_id = request.args.get('recipe')
            copy_recipe = "INSERT INTO recipes (recipe_id, user_id, title, description) SELECT UUID(), (SELECT id FROM verifiedusers WHERE username=%s), CASE WHEN (SELECT title FROM recipes WHERE recipe_id=%s) IN (SELECT title FROM recipes) THEN CONCAT((SELECT title FROM recipes WHERE recipe_id=%s),'-',UUID()) ELSE title END, description FROM recipes WHERE recipe_id=%s"
            recipe_copy = cursor.execute(copy_recipe, [session['username'], recipe_id, recipe_id, recipe_id, recipe_id])
            copy_ingredients = "INSERT INTO ingredients (ingr_id, user_id, recipe_id, name, amount, unit) SELECT UUID(), (SELECT id FROM verifiedusers WHERE username=%s), (SELECT recipe_id FROM recipes WHERE recipe_id=%s), name, amount, unit FROM ingredients WHERE recipe_id=%s"
            ingredients_copy = cursor.execute(copy_ingredients, [session['username'], recipe_id, recipe_id])
            if (recipe_copy + ingredients_copy) > 0:
                flash('Recipe added to Your Recipes', 'success')
                return redirect(url_for('activity'))
        my_sql_close(connection,cursor)
        return render_template('add_recipe.html', form=form, units=units)

# activity stream
@app.route('/activity', methods = ['GET'])
@is_logged_in
def activity():
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    get_all_recipes = "SELECT v.username, r.title, r.recipe_id FROM recipes r LEFT JOIN verifiedusers v ON v.id = r.user_id ORDER BY date_created DESC;"
    cursor.execute(get_all_recipes)
    recipes = list(map(list, zip(*cursor.fetchall())))
    usernames = recipes[0]
    titles = recipes[1]
    ids = recipes[2]
    connection.commit()
    my_sql_close(connection, cursor)
    return render_template('activity.html', usernames=usernames, titles=titles, ids=ids)

@app.route('/view_recipe', methods = ['GET', 'POST'])
@is_logged_in
def view_recipe():
    recipe_id = request.args.get('recipe')
    sqldb = my_sql_init()
    cursor = sqldb[0]
    connection = sqldb[1]
    get_recipe = "select r.title, r.description, i.name, i.amount, i.unit FROM ingredients i INNER JOIN recipes r WHERE r.recipe_id = %s AND i.recipe_id = %s"
    cursor.execute(get_recipe, [recipe_id, recipe_id])
    recipe_data = list(map(list, zip(*cursor.fetchall())))
    if not recipe_data:
        flash("Could not find recipe", "danger")
        return redirect(url_for('/activity'))
    title = recipe_data[0][0]
    description = recipe_data[1][0]
    ingredients = recipe_data[2]
    amounts = recipe_data[3]
    units = ['kg', 'g', 'lb', 'oz', 'L', 'mL', 'Tblsp', 'tsp', 'cup', 'quart', 'gallon', 'package', 'jar', 'qty']
    actual_units = [units[int(i)] for i in recipe_data[4]]
    connection.commit()
    my_sql_close(connection, cursor)
    return render_template('view_recipe.html', recipe_id=recipe_id, title=title, description=description, ingredients=ingredients, amounts=amounts, units=actual_units)
 
if __name__ == '__main__':
    app.secret_key = secrets.secret_key
    app.run('0.0.0.0', 5001, True)
