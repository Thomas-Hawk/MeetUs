from flask import Flask, render_template, request, redirect, url_for, session, flash
from model import Account, Event, Guest, Whoknowswho, db
import openai

openai.api_key = "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"

app = Flask(__name__)  # Crée un instance de la classe Flask
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///meetus.db"
db.init_app(app)  # associer app à sqlAlchemy


with app.app_context():
    # Créez les tables dans la base de données
    db.create_all()


@app.route("/")
def index():  # Méthode appelée quand on se rend sur la route "/"
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if Account.query.filter_by(username=username).first():
            flash("Username is already taken. Please choose another.")
        else:
            new_user = Account(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully. You can now log in.")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = Account.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id

            flash("Login successful!")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    user = Account.query.get(session["user_id"])
    if user:
        events = Event.query.filter_by(id_account=session["user_id"]).all()
        return render_template("dashboard.html", name=user.username, events=events)
    else:
        flash("You need to log in first.")
        return redirect(url_for("login"))


##################################---EVENT---##################################
@app.route("/event", methods=["POST"])
def creat_event():
    if request.method == "POST":
        nameEvent = request.form["nameEvent"]
        existing_event = Event.query.filter_by(
            id_account=session["user_id"], eventname=nameEvent
        ).first()
        if existing_event:
            flash("event name is already taken. Please choose another.")
            print(existing_event)
        else:
            event = Event(eventname=nameEvent, id_account=session["user_id"])
            db.session.add(event)
            db.session.commit()

    return redirect(url_for("dashboard"))


@app.route("/delete_event/<int:event_id>", methods=["GET"])
def delete_event(event_id):
    event = Event.query.get(event_id)

    if not event:
        flash("Événement introuvable.")
    else:
        db.session.delete(event)
        db.session.commit()

    return redirect(url_for("dashboard"))


@app.route("/event_details/<int:event_id>", methods=["POST", "GET"])
def event_details(event_id):
    event = Event.query.get(event_id)
    guests = Guest.query.filter_by(id_event=event_id).all()
    return render_template("event_details.html", event=event, guests=guests)


##################################---GUEST---##################################
@app.route("/creat_guest/<int:event_id>", methods=["POST", "GET"])
def creat_guest(event_id):
    fname = request.form["fname"]
    lname = request.form["lname"]
    job = request.form["job"]
    age = request.form["age"]
    sex = request.form["sex"]
    hobby_1 = request.form["hobby_1"]
    hobby_2 = request.form["hobby_2"]
    hobby_3 = request.form["hobby_3"]
    guest = Guest(
        fname=fname,
        lname=lname,
        job=job,
        age=age,
        sex=sex,
        hobby_1=hobby_1,
        hobby_2=hobby_2,
        hobby_3=hobby_3,
        id_event=event_id,
    )
    db.session.add(guest)
    db.session.commit()

    return redirect(url_for("event_details", event_id=event_id))


@app.route("/update_guest/<int:event_id><int:guest_id>", methods=["POST", "GET"])
def update_guest(event_id, guest_id):
    event = Guest.query.get(guest_id)

    fname = request.form["fname"]
    lname = request.form["lname"]
    job = request.form["job"]
    age = request.form["age"]
    sex = request.form["sex"]
    hobby_1 = request.form["hobby_1"]
    hobby_2 = request.form["hobby_2"]
    hobby_3 = request.form["hobby_3"]

    event.fname = fname
    event.lname = lname
    event.job = job
    event.age = age
    event.sex = sex
    event.hobby_1 = hobby_1
    event.hobby_2 = hobby_2
    event.hobby_3 = hobby_3

    db.session.commit()

    return redirect(url_for("event_details", event_id=event_id))


@app.route("/guest_friends/<int:event_id><int:guest_id>", methods=["GET"])
def guest_friends(event_id, guest_id):
    guests = Guest.query.filter(Guest.id_event == event_id, Guest.id != guest_id).all()
    guest = Guest.query.get(guest_id)

    knowledges = Whoknowswho.query.filter(Whoknowswho.guest == guest.id).all()
    knowledge_ids = [knowledge.know_him for knowledge in knowledges]
    print(knowledge_ids)

    return render_template(
        "guest_friends.html",
        event_id=event_id,
        guests=guests,
        guest=guest,
        knowledges=knowledge_ids,
    )


@app.route("/delete_guest/<int:event_id><int:guest_id>", methods=["GET"])
def delete_guest(event_id, guest_id):
    guest = Guest.query.get(guest_id)

    if not guest:
        flash("Invité introuvable.")
    else:
        db.session.delete(guest)
        db.session.commit()

    return redirect(url_for("event_details", event_id=event_id))


@app.route("/whoknowwho", methods=["GET", "POST"])
def whoknowwho():
    id_user = request.form.get("userid")
    id_guest = request.form.get("friendid")
    print(id_guest, id_user)
    result = f"Les IDs sont {id_user} et {id_guest}"
    knowledge = Whoknowswho.query.filter(
        Whoknowswho.guest == id_user, Whoknowswho.know_him == id_guest
    ).first()
    if knowledge:
        guest = Whoknowswho.query.get(knowledge.id)
        db.session.delete(guest)
        db.session.commit()
    else:
        whoknowswho = Whoknowswho(guest=id_user, know_him=id_guest)
        db.session.add(whoknowswho)
    db.session.commit()

    return result


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("is_logged_in", None)
    flash("You have been logged out.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
