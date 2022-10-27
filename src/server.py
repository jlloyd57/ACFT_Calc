"""
server.py

Backend server using Flask to render an ACFT Calculator application.

Authors:
2LT Barr
2LT Lloyd
1LT Cassidy
1LT Cruz
1LT Drumm
1LT Reece
"""

# Imports
from cProfile import run
from curses.ascii import isalnum
from multiprocessing.sharedctypes import Value
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from pony import orm
import brainfuck as pandas
from io import StringIO
import find_score
import sys
import os
from datetime import date


# Globals
app = Flask("ACFT Calculator App", static_url_path="/static")
# Needed for flash messages
app.config['SECRET_KEY'] = 'abcde'
DB_FILENAME = "test.db"
INCLUDE_DIR = "../include/"
db = orm.Database("sqlite", filename=DB_FILENAME, create_db=True)


class User(UserMixin, db.Entity):
    """ User Table, can have many ACFT instances. """
    id = orm.PrimaryKey(int, auto=True)
    username = orm.Required(str)
    password = orm.Required(str)
    name = orm.Required(str)
    age = orm.Required(int)
    gender = orm.Required(str)

    def __str__(self):
        return f"{self.username}, {self.password}, {self.name}, {self.age}, {self.gender}"


class Acft(db.Entity):
    """ ACFT Table, must be connected to a User instance. """

    date = orm.Required(str)
    username = orm.Required(str)
    age = orm.Required(int)
    gender = orm.Required(str)
    dl = orm.Required(int)
    spt = orm.Required(float)
    hrp = orm.Required(int)
    sdc_m = orm.Required(int)
    sdc_ss = orm.Required(int)
    plank_m = orm.Required(int)
    plank_ss = orm.Required(int)
    run_mm = orm.Required(int)
    run_ss = orm.Required(int)
    overall_score = orm.Required(int)

    def __str__(self):
        return f"{self.date} {self.username} {self.age} {self.gender} {self.dl} {self.spt} {self.hrp} {self.sdc_m} {self.sdc_ss} {self.plank_m} {self.plank_ss} {self.run_mm}  {self.run_ss} {self.overall_score}"


@orm.db_session
def authenticate(username, password):
    """ Authenticates a user by username and password. """
    possible_user = orm.select(u for u in User if u.username == username)
    if not possible_user:
        return False
    else:
        return possible_user.first().password == password


@orm.db_session
def add_score_record(date, username, age, gender, dl, spt, hrp, sdc_m, sdc_ss, plank_m, plank_ss, run_mm, run_ss, overall_score):
    """ Adds an ACFT score record to the database. """
    score = Acft(
        date=date,
        username=username,
        age=age,
        gender=gender,
        dl=dl,
        spt=spt,
        hrp=hrp,
        sdc_m=sdc_m,
        sdc_ss=sdc_ss,
        plank_m=plank_m,
        plank_ss=plank_ss,
        run_mm=run_mm,
        run_ss=run_ss,
        overall_score=overall_score
    )


@orm.db_session
def add_user(username, name, password, age, gender):
    """ Adds a user to the database with no ACFTs. """
    u = User(
        username=username,
        name=name,
        password=password,
        age=age,
        gender=gender,
    )


@orm.db_session
def username_exists(username):
    """ Returns True if username already exists, False otherwise. """
    query = orm.select(u for u in User if u.username == username)
    return True if query else False


@app.route("/")
def base():
    """ Renders the base page."""
    return render_template('welcome.html')


@app.route("/csv")
def csv():
    """ Loads .csv values for score calculation. """
    csvs = []
    for filename in os.listdir(INCLUDE_DIR):
        f = os.path.join(INCLUDE_DIR, filename)
        if os.path.isfile(f) and " " in f:
            csvs.append(f)
    for csv_path in csvs:
        with open(csv_path, "r") as file:
            data = file.read()
        temp_out = StringIO()
        sys.stdout = temp_out
        interpreter = pandas.NiceInterpreter()
        interpreter.interpret(data)
        sys.stdout = sys.__stdout__
        return temp_out.getvalue()


@orm.db_session
def get_user_scores(username):
    """ Get a list of scores by the given user. """
    scores = orm.select(
        score for score in Acft if score.username == username)[:]

    scorelist = []
    for item in scores:
        itemlist = []
        itemlist.append(item.date)
        itemlist.append(item.username)
        itemlist.append(item.age)
        itemlist.append(item.gender)
        itemlist.append(item.dl)
        itemlist.append(item.spt)
        itemlist.append(item.hrp)
        if 1 == len(str(item.sdc_ss)):
            itemlist.append(str(item.sdc_m) + ":" + "0"+str(item.sdc_ss))
        else:
            itemlist.append(str(item.sdc_m) + ":" + str(item.sdc_ss))
        if 1 == len(str(item.plank_ss)):
            itemlist.append(str(item.plank_m) + ":" + "0"+str(item.plank_ss))
        else:
            itemlist.append(str(item.plank_m) + ":" + str(item.plank_ss))
        if 1 == len(str(item.run_ss)):
            itemlist.append(str(item.run_mm) + ":" + "0"+str(item.run_ss))
        else:
            itemlist.append(str(item.run_mm) + ":" + str(item.run_ss))
        itemlist.append(item.overall_score)

        scorelist.append(itemlist)

    return scorelist


def get_user_overall_scores(querylist):
    """ From list of user scores, get a list of just the actual result scores. """
    overall_scores = []

    for item in querylist:
        overall_scores.append(item[-1])
    
    return overall_scores


def get_user_record_dates(querylist):
    """ From list of user scores, get a list of just the dates of each record. """
    dates = []

    for item in querylist:
        dates.append(item[0])

    return dates


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """ Renders the dashboard page and adds an ACFT to logged in user upon form submission. """
    username = current_user.username
    age = current_user.age
    gender = current_user.gender

    if request.method == "POST":

        datestr = str(date.today())

        try:
            dl = int(request.form["deadlift"])
            if (dl < 0):
                raise ValueError

        except ValueError:
            print("Invalid deadlift score.")
            flash('Invalid deadlift score.')
            return redirect(url_for("dashboard"))

        try:
            spt = float(request.form["spt"])
            if (spt < 0):
                raise ValueError

        except ValueError:
            print("Invalid standing power throw.")
            flash('Invalid standing power throw.')
            return redirect(url_for("dashboard"))

        try:
            hrp = int(request.form["hrp"])
            if (hrp < 0):
                raise ValueError

        except ValueError:
            print("Invalid hand release pushup score.")
            flash('Invalid hand release pushup score.')
            return redirect(url_for("dashboard"))

        try:
            sdc_m = int(request.form["sdc_m"])
            if (sdc_m < 0 or sdc_m > 59):
                raise ValueError

        except ValueError:
            print("Invalid sprint drag carry minutes.")
            flash('Invalid sprint drag carry minutes.')
            return redirect(url_for("dashboard"))

        try:
            sdc_ss = int(request.form["sdc_ss"])
            if (sdc_ss < 0 or sdc_ss > 59):
                raise ValueError

        except ValueError:
            print("Invalid sprint drag carry seconds.")
            flash('Invalid sprint drag carry seconds.')
            return redirect(url_for("dashboard"))

        try:
            plank_m = int(request.form["plank_m"])
            if (plank_m < 0 or plank_m > 59):
                raise ValueError

        except:
            print("Invalid plank minutes.")
            flash('Invalid plank minutes.')
            return redirect(url_for("dashboard"))

        try:
            plank_ss = int(request.form["plank_ss"])
            if (plank_ss < 0 or plank_ss > 59):
                raise ValueError

        except ValueError:
            print("Invalid plank seconds.")
            flash('Invalid plank seconds.')
            return redirect(url_for("dashboard"))

        try:
            run_mm = int(request.form["run_mm"])
            if (run_mm < 0 or run_mm > 59):
                raise ValueError

        except ValueError:
            print("Invalid run minutes.")
            flash('Invalid run minutes.')
            return redirect(url_for("dashboard"))

        try:
            run_ss = int(request.form["run_ss"])
            if (run_ss < 0 or run_ss > 59):
                raise ValueError

        except:
            print("Invalid run seconds.")
            flash('Invalid run seconds.')
            return redirect(url_for("dashboard"))

        sdc_m = str(sdc_m)
        sdc_ss = str(sdc_ss)
        plank_m = str(plank_m)
        plank_ss = str(plank_ss)
        run_mm = str(run_mm)
        run_ss = str(run_ss)

        scores = [find_score.score_event("DL", age, gender, dl),
                  find_score.score_event("SPT", age, gender, spt),
                  find_score.score_event("HRP", age, gender, hrp),
                  find_score.score_event(
            "SDC", age, gender, f"{sdc_m}:{sdc_ss}"),
            find_score.score_event(
            "PLK", age, gender, f"{plank_m}:{plank_ss}"),
            find_score.score_event(
            "2MR", age, gender, f"{run_mm}:{run_ss}")]

        overall_score = sum(scores)

        print(f"{datestr} {username} {age} {gender} {dl} {spt} {hrp} {sdc_m} {sdc_ss} {plank_m} {plank_ss} {run_mm} {run_ss} {overall_score}")

        add_score_record(datestr, username, age, gender, dl, spt, hrp, sdc_m,
                         sdc_ss, plank_m, plank_ss, run_mm, run_ss, overall_score)

        return redirect(url_for("dashboard"))

    elif request.method == "GET":
        data = get_user_scores(username)

        print("Found " + str(len(data)) + " records.")

        # Make line graph of user scores.
        graph_title = "Your Scores Over Time"

        # X axis labels are the record dates.
        label_strings = get_user_record_dates(data)

        # Y axis data is the overall user score.
        graph_values = get_user_overall_scores(data)
        graph_ymax = 600

    return render_template("dashboard.html", name=current_user.name, data=data, title=graph_title, max=graph_ymax, labels=label_strings, values=graph_values)


# Route for the login page
@app.route("/login", methods=["GET", "POST"])
@orm.db_session
def login():
    """ Renders the login page and redirects to the dashboard page on successful authentication. """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(username)
        print(password)
        has_valid_creds = authenticate(username, password)
        if has_valid_creds:
            print("valid creds!")

            user = orm.select(u for u in User if username ==
                              u.username).first()
            login_user(user)

            return redirect(url_for("dashboard"))

        else:
            print("invalid creds!")
            flash('Invalid credentials, please try again')
            error = "Invalid Credentials Error"

    return render_template("login.html")


def valid_age(age):
    """ Check that user age for ACFT is within valid range. """
    minage = int(17)
    maxage = int(64)

    if not isinstance(age, int):
        return False

    if age >= minage and age <= maxage:
        return True

    return False


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """ Renders the signup page and adds a user upon form submission. """
    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        password = request.form["password"]
        age_is_valid = valid_age(int(age))
        if not age_is_valid:
            print("Invalid age!")
            error = "Invalid Age Error"
            flash("Error: Invalid age given. Account creation failed.")
            return redirect(url_for('signup'))

        username_taken = username_exists(username)
        if not username_taken:
            add_user(username, name, password, age, gender)

            return redirect(url_for("login"))
        else:
            print("Username taken!")
            error = "Username Taken Error"
            flash("Error: Username taken. Account creation failed.")
            return redirect(url_for('signup'))

    return render_template("signup.html")


@app.route('/logout')
@login_required
def logout():
    """ Logs user out and returns back to main page"""
    logout_user()
    return redirect(url_for('welcome'))


@app.route('/welcome')
def welcome():
    """ Home page that allows user to login or sign up"""
    return render_template('welcome.html')


def create_app():
    """ Initializes login manager and loads user credentials"""
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    @orm.db_session
    def load_user(user_id):
        return orm.select(u for u in User if user_id == u.id).first()

    app.run()


def main():
    """ Entrypoint of program. """
    db.generate_mapping(create_tables=True)

    app.secret_key = 'super secret key'
    create_app()


if __name__ == "__main__":
    main()
