from flask import Flask, render_template, flash, redirect, url_for, session, request, make_response
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import pbkdf2_sha256
from functools import wraps
import MySQLdb
import pdfkit

app = Flask(__name__)
app.debug = True

pepper = 'XVr7XrQJNnF0brWZLjWy'

#Init MySQL
db1 = MySQLdb.connect(host="localhost", user="root", passwd="Ilovemealplanning1[]")
cursor1 = db1.cursor()
sql0 = '''USE getthegroceries;'''
sql1 = '''CREATE DATABASE IF NOT EXISTS getthegroceries;'''
sql2 = '''CREATE TABLE IF NOT EXISTS users(id INT(11) AUTO_INCREMENT PRIMARY KEY, 
        name VARCHAR(100), email VARCHAR(100), username VARCHAR(30), password VARCHAR(100), salt VARCHAR(100),
        register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'''
sql3 = '''CREATE TABLE IF NOT EXISTS recipes(recipe_id INT(11) AUTO_INCREMENT PRIMARY KEY, 
user_id INT(11), title VARCHAR(255), description TEXT, date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'''
sql4 = '''CREATE TABLE IF NOT EXISTS ingredients(ingr_id INT(11) AUTO_INCREMENT PRIMARY KEY, 
user_id INT(11), recipe_id INT(11), name VARCHAR(255), amount VARCHAR(10), unit VARCHAR(10));'''

#Execute MySQL setup
cursor1.execute(sql0)
cursor1.execute(sql1)
cursor1.execute(sql2)
cursor1.execute(sql3)
cursor1.execute(sql4)
cursor1.close()


#Classes
class Recipe:
    def __init__(self,name,description,ingredients,amounts,units):
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


#Functions
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
    cursor = db1.cursor()
    recipe_query = "SELECT * FROM recipes WHERE user_id = %s"
    ingredient_query = "SELECT * FROM ingredients where recipe_id = %s"
    cursor.execute(recipe_query, [user_id])
    cursor.fetchall()
    recipes = {}
    #iterate through recipes
    for row in cursor:
        #create new cursor object to do ingredient queries
        cursor2 = db1.cursor()
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
        recipes[row[0]] = Recipe(row[2],row[3],ingredient_list,amount_list,unit_list)
    return recipes


def reverse_string(str):
    return str[::-1]


def encrypt(password,username):
    salt = username + reverse_string(username)
    seasonedbeef = salt + password + pepper
    print(seasonedbeef)
    hashy = pbkdf2_sha256.hash(seasonedbeef)
    return hashy


def passwordverify(username, storedhash, password_candidate):
    salt = username + reverse_string(username)
    password_candidate = salt + password_candidate + pepper
    print(password_candidate)
    if pbkdf2_sha256.verify(password_candidate, storedhash):
        return True
    else:
        return False


def delete_recipe(recipe, user_id):
    cursor = db1.cursor()
    getrecipe_id = "SELECT recipe_id from recipes WHERE title=%s AND user_id=%s"
    deletesql1 = "DELETE FROM recipes WHERE recipe_id=%s"
    deletesql2 = "DELETE FROM ingredients WHERE recipe_id=%s"
    cursor.execute(getrecipe_id, [recipe, user_id])
    recipe_id = cursor.fetchone()[0]
    cursor.execute(deletesql1, [recipe_id])
    cursor.execute(deletesql2, [recipe_id])
    db1.commit()
    cursor.close()


#Flask routes
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/get_list')
@is_logged_in
def getlist():
    cursor = db1.cursor()
    user_id = session.get('userid', None)
    mealplannames = session.get('mealplannames', None)
    sql1 = "SELECT * FROM recipes WHERE user_id=%s AND title=%s"
    sql2 = "SELECT * FROM ingredients WHERE recipe_id=%s"
    descriptions = []
    ingredients = []
    amounts = []
    units = []
    for name in mealplannames:
        print(name)
        cursor.execute(sql1, [user_id, name])
        data = cursor.fetchone()
        print(data)
        recipe_id = data[0]
        descriptions.append(data[3])
        cursor.execute(sql2, [recipe_id])
        for i, row in enumerate(cursor.fetchall()):
            ingredients.append(row[3])
            amounts.append(row[4])
            units.append(row[5])
    for loc, ingredient in enumerate(ingredients):
        for i, check in enumerate(ingredients):
            if (ingredient == check) and (units[loc] == units[i]):
                newamount = amount[i] + amount[loc]
                newingredients.append(ingredient)
                newunits.append(unit[i])
                #TODO: old ingredient/amounts


    rendered = render_template('pdf_template.html', recipes=recipes, ingredients=ingredients, amounts=amounts, units=units)
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=ShoppingList.pdf'
    return response


@app.route('/edit_recipe', methods=['GET', 'POST'])
@is_logged_in
def edit_recipe():
    recipe = request.args.get('recipe')
    user = session['username']

    # declare cursor
    cursor = db1.cursor()

    # sql queries
    getuserid = "SELECT id FROM users WHERE username=%s"
    getrecipe = "SELECT recipe_id, description FROM recipes WHERE title=%s AND user_id=%s"
    getingredients = "SELECT * FROM ingredients WHERE recipe_id=%s"

    # get user_id
    cursor.execute(getuserid, [user])
    user_id = cursor.fetchone()[0]

    # get recipe_id and description
    cursor.execute(getrecipe, [recipe, user_id])
    stuff = cursor.fetchone()

    recipe_id = stuff[0]
    description = stuff[1]

    # form stuff
    form = RecipeForm(request.form)
    form.title.data = recipe
    form.description.data = description
    ingredients = []
    amounts = []
    units = []
    unittype = ['kg', 'g', 'lb', 'oz', 'L', 'mL', 'Tblsp', 'tsp', 'cup', 'quart', 'gallon', 'package', 'jar', 'qty']
    # get ingredients from db
    cursor.execute(getingredients, [recipe_id])
    for row in cursor.fetchall():
        ingredients.append(row[3])
        amounts.append(row[4])
        units.append(row[5])
    if request.method == 'POST' and form.validate():
        # Get all the form data
        newtitle = request.form['title']
        newdescription = request.form['description'] 
        ingredients = request.form.getlist('ingr_name')
        amounts = request.form.getlist('amount')
        units = request.form.getlist('unit')

        # checks for duplicate recipe names
        cursor.execute("SELECT * FROM recipes WHERE user_id=%s AND title=%s", [user_id, newtitle])
        if (newtitle.lower() == recipe.lower()) or (cursor.fetchall() is None):
            # updates recipe data in SQL tables
            recipeupdate = "UPDATE recipes SET title=%s, description=%s WHERE recipe_id=%s;"
            cursor.execute(recipeupdate, [newtitle, newdescription, recipe_id])
            db1.commit()
            dropoldingredients = "DELETE FROM ingredients WHERE recipe_id=%s"
            cursor.execute(dropoldingredients, [recipe_id])
            db1.commit()
            for i, ingredient in enumerate(ingredients):
                ingredientinsert = "INSERT INTO ingredients (user_id, recipe_id, name, amount, unit) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(ingredientinsert, [user_id, recipe_id, ingredient, amounts[i], units[i]])
            # commit to db
            db1.commit()
            flash('Recipe Updated', 'success')
            cursor.close()
            return redirect(url_for('dashboard'))
        else:
            flash('The title "' + newtitle + '" has already been used by you, pick a different title.', 'danger')
            return render_template('edit_recipe.html', form=form, ingredients=ingredients, amounts=amounts, units=units,unittype=unittype)
    else:
        cursor.close()
        return render_template('edit_recipe.html', form=form, ingredients=ingredients, amounts=amounts, units=units, unittype=unittype)




@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = db1.cursor()
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        usernamequery = '''SELECT * FROM users WHERE username = %s'''
        emailquery = '''SELECT * FROM users WHERE email = %s'''
        cursor.execute(usernamequery, [username])
        usernamedata = cursor.fetchone()
        cursor.execute(emailquery, [email])
        emaildata = cursor.fetchone()
        if emaildata is not None:
            flash("That email is already in use with another account, pick something different.", 'danger')
            return render_template('register.html', form=form)
        if usernamedata is not None:
            flash("That username is already in use, pick something different.", 'danger')
            return render_template('register.html', form=form)
        else:
            password = encrypt(request.form['password'], username)
            cursor.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
            # Commit to DB
            db1.commit()
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
    cursor.close()
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    cursor = db1.cursor()
    if request.method == 'POST':
        # get form fields
        username = request.form['username']
        password_candidate = request.form['password']
        # get user by username
        cursor.execute("SELECT * FROM users WHERE username = %s", [username])
        result = cursor.fetchone()
        if result is not None:
            # get stored hash
            storedhash = result[4]
            # compare passwords
            if passwordverify(username, storedhash, password_candidate):
                # passed login
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Login'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    cursor.close()
    return render_template('login.html')


# logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# dashboard
@app.route('/dashboard', methods = ['GET', 'POST'])
@is_logged_in
def dashboard():
    cursor = db1.cursor()
    user = session['username']
    user_id_query = "SELECT id FROM users WHERE username = %s"
    cursor.execute(user_id_query, [user])
    data = cursor.fetchone()
    user_id = data[0]
    recipes = get_all_recipes(user_id)
    cursor.close()
    names = []
    descriptions = []
    if request.method == 'POST':
        whatdo = request.form['func']
        if whatdo == 'del':
            recipename = request.form['name']
            delete_recipe(recipename, user_id)
            return render_template('dashboard.html', names=names, descriptions=descriptions)
        if whatdo == 'getList':
            recipearray = request.form.getlist('namearray[]')
            session['mealplannames'] = recipearray
            session['userid'] = user_id
            return redirect(url_for('getlist'))
    for i in recipes:
        names.append(recipes[i].name)
        descriptions.append(recipes[i].description)
    return render_template('dashboard.html', names=names, descriptions=descriptions)


@app.route('/add_recipe', methods=['GET', 'POST'])
@is_logged_in
def add_recipe():
    cursor = db1.cursor()
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
        usernamequery = "SELECT id FROM users WHERE username = %s"
        cursor.execute(usernamequery, [user])
        user_id = cursor.fetchone()
        # checks for duplicate recipe names
        cursor.execute("SELECT * FROM recipes WHERE user_id=%s AND title=%s", [user_id, title])
        if cursor.fetchall():
            flash('Recipe title has already been used by you, pick a different title.', 'danger')
            return redirect(url_for('add_recipe'))
        else:
            # insert recipe data into SQL tables
            recipeinsert = "INSERT INTO recipes(user_id, title, description) VALUES(%s, %s, %s)"
            cursor.execute(recipeinsert, [user_id[0], title, description])
            db1.commit()
            recipequery = "SELECT recipe_id FROM recipes WHERE title = %s"
            cursor.execute(recipequery, [title])
            recipe_id = cursor.fetchone()
            for i, ingredient in enumerate(ingredients):
                ingredientinsert = "INSERT INTO ingredients(user_id, recipe_id, name, amount, unit) VALUES(%s, %s, %s, %s, %s)"
                cursor.execute(ingredientinsert, [user_id[0], recipe_id[0], ingredient, amounts[i], units[i]])
            # commit to db
            db1.commit()
            flash('Recipe Created', 'success')
            cursor.close()
            return redirect(url_for('dashboard'))
    else:
        cursor.close()
        return render_template('add_recipe.html', form=form, units=units)


if __name__ == '__main__':
    app.secret_key='bingbongdingdong123'
    app.run()
