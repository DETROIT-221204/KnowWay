from flask import Flask, render_template, request
import smtplib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

# Email credentials
OWN_EMAIL = 'toastedcheese146@gmail.com'
OWN_PASSWORD = 'hqjj moqw pquc pstr'

app = Flask(__name__)


# Database setup
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///subjects.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Database Model
class Subjects(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)


class yt(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)


# Create tables and add initial subjects
with app.app_context():
    db.create_all()  # Ensure tables are created

    # Check if subjects table is empty before adding
    if db.session.query(Subjects).count() == 0:
        subjects_list = [
            Subjects(subject_name='Engineering Mathematics-I'),
            Subjects(subject_name='Engineering Physics-I'),
            Subjects(subject_name='Engineering Chemistry-I'),
            Subjects(subject_name='Engineering Mechanics'),
            Subjects(subject_name='Basic Electrical Engineering')
        ]
        db.session.add_all(subjects_list)
        db.session.commit()


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/resource', methods=['POST'])
def show_resources():
    subjects=Subjects.query.all()
    branch = request.form.get('branch')
    semester = request.form.get('semester')
    if branch == 'Computer Engineering' and semester == '1':
        return render_template('sem1.html',subjects=subjects)
@app.route('/chapters/<string:choice>', methods=['GET'])
def resource(choice):
    chapters = yt.query.all()
    return render_template('chapters.html', chapters=chapters, subject=choice)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]
        send_email(name=name, email=email, message=message)
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)

def send_email(name, email, message):
    email_message = f"Subject: New Message\n\nName: {name}\nEmail: {email}\nMessage: {message}"
    try:
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(OWN_EMAIL, OWN_PASSWORD)
            connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    app.run(debug=True)
