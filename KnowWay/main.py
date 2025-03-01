from flask import Flask, render_template, request
import smtplib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, text

# Email credentials
OWN_EMAIL = 'toastedcheese146@gmail.com'
OWN_PASSWORD = 'hqjj moqw pquc pstr'

app = Flask(__name__)

# Database setup
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///chapters.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Database Models
class Subjects(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)

class yt(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    subject_name: Mapped[str] = mapped_column(String(250), nullable=True)  # New Column

class Chapters(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    subject_name: Mapped[str] = mapped_column(String(250), nullable=True)

# Create tables inside application context
with app.app_context():
    db.create_all()  # Ensure tables exist

    # ✅ Check if 'subject_name' column exists in `yt` table
    existing_columns = db.session.execute(text("PRAGMA table_info(yt)")).fetchall()
    column_names = [col[1] for col in existing_columns]

    if "subject_name" not in column_names:
        db.session.execute(text("ALTER TABLE yt ADD COLUMN subject_name TEXT"))
        db.session.commit()

    # ✅ Add default data to `yt` table
    yt_records = yt.query.all()
    for record in yt_records:
        record.subject_name = "Engineering Mathematics-I"

    db.session.commit()

    # ✅ Add default subjects if empty
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

    # ✅ Add default chapters if empty
    if db.session.query(Chapters).count() == 0:
        chapter_list = [
            Chapters(id=1, subject_name='Engineering Mathematics-I', chapter_name='Complex Numbers',
                     video_url='https://youtube.com/playlist?list=PLT3bOBUU3L9jA-0qKbD2oHvNFCkwfBw-7&si=OIQz4q753sUmYgvd'),
            Chapters(id=2, subject_name='Engineering Mathematics-I', chapter_name='Hyperbolic function and Logarithm of Complex Numbers',
                     video_url='https://youtube.com/playlist?list=PLjgyGylma3IG5K2j24tEttFX0JAS3Rtp_&si=RJ_aV57ADaFSuz-Z'),
            Chapters(id=3, subject_name='Engineering Mathematics-I', chapter_name='Partial Differentiation',
                     video_url='https://youtube.com/playlist?list=PLT3bOBUU3L9iRoyhs8V1Io-xEsjfq4zI0&si=5F4Q04iBdhk8zjqf'),
            Chapters(id=4, subject_name='Engineering Mathematics-I', chapter_name='Applications of Partial Differentiation and Successive differentiation',
                     video_url='https://youtu.be/nC_e9pKpfK0?si=o4hZaufJaJDFQQ_G'),
            Chapters(id=5, subject_name='Engineering Mathematics-I', chapter_name='Matrices',
                     video_url='https://youtube.com/playlist?list=PLT3bOBUU3L9imMlPeqnVYZqKqycvSK_ms&si=DM6zchTEhrnWLBGN'),
            Chapters(id=6, subject_name='Engineering Mathematics-I', chapter_name='Numerical Solutions of Transcendental Equations and System of Linear Equations and Expansion of Function',
                     video_url='https://youtu.be/nC_e9pKpfK0?si=o4hZaufJaJDFQQ_G')
        ]
        db.session.add_all(chapter_list)
        db.session.commit()

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/resource', methods=['POST'])
def show_resources():
    subjects = Subjects.query.all()
    branch = request.form.get('branch')
    semester = request.form.get('semester')
    if branch == 'Computer Engineering' and semester == '1':
        return render_template('sem1.html', subjects=subjects)

@app.route('/chapters/<string:choice>', methods=['GET'])
def resource(choice):
    chapters = Chapters.query.filter_by(subject_name=choice).all()
    return render_template('chapters.html', chapters=chapters, subject=choice)
@app.route('/demo/<string:choice>',methods=['GET','POST'])
def demo(choice):
    chapter = Chapters.query.filter_by(chapter_name=choice).all()
    return render_template('demoresource.html',res=chapter)


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
