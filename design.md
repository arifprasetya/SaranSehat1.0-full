###**Overview**
<code>Saran Sehat</code> is a web-based application developed with Python, HTML, CSS, and JavaScript. The main modules used to develop <code>Saran Sehat</code> is Flask (https://palletsprojects.com/p/flask) and CS50 Library for Python (https://cs50.readthedocs.io/libraries/cs50/python/), while the database engine used in <code>Saran Sehat</code> is SQLite (https://www.sqlite.org/index.html).
The application is free for use and is available in https://github.com/arifprasetya/SaranSehat1.0-full.git.
Link to the video: [Saran Sehat](https://youtu.be/V1I_ZK46RkU)

###**Structure**
- SARANSEHAT1.0-MAIN
    |-- __pychace__/
    |-- flask_session/
    |-- myenv/
    |-- static/
    |   |-- css/
    |   |-- images/
    |   |-- js/
    |-- templates
    |-- app.py
    |-- helpers.py
    |-- saransehat.db
    |-- DESIGN.md
    |-- README.md    


###**Database Schema**
The database is designed using relational model. Foreign key constraint is used to keep the database integrity.
<code>saransehat.db</code>has four tables to store the application data. 

<code>bio</code> table is to store person's data which his BMI, BMR, and TDEE were calculated. It is related to <code>opo</code> table, referenced by the <code>id</code>.
<code>CREATE TABLE "bio" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT, 
        imt NUMERIC NOT NULL,
        bmr NUMERIC NOT NULL,
        tdee NUMERIC NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
)</code>

<code>foods</code> table is to store foods data.
<code>CREATE TABLE foods (
    "food_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    unit TEXT NOT NULL,
    calories NUMERIC NOT NULL
)</code>

<code>user_intake</code> table is to store foods that were picked by user for getting healthy suggestions. It is related to <code>foods</code> and <code>bio</code>, all referenced by the <code>id</code>
<code>CREATE TABLE "user_intake" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bio_id INTEGER,
    food_id INTEGER,
    food_name TEXT NOT NULL,
    meal_type TEXT,    
    amount NUMERIC NOT NULL, 
    unit TEXT NOT NULL, 
    calories NUMERIC NOT NULL,
    timestamp DATETIME,
    FOREIGN KEY (bio_id) REFERENCES bio(id),
    FOREIGN KEY (food_id) REFERENCES foods(food_id)
)</code>

<code>users</code> table is to store users credentials.
<code>CREATE TABLE "users" (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        name TEXT,
        hash TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT NOT NULL
)</code>
###**Structure**
All the assets and resources used in this application are located inside the <code>static</code> directory. Meanwhile the <code>templates</code>directory keeps all the HTML files which renders results returned by <code>app.py</code>. The backbone of <code>Saran Sehat</code> is in <code>app.py</code>, where records from the database are retrieved and modified, user inputs are processed, and results are rendered to the templates. <code>helpers.py</code> provides several functions to help with multi-level authentication and the adaptation of CS50's apology from <code>finance</code>.
