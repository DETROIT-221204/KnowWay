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

    # New columns
    notes_link: Mapped[str] = mapped_column(String(500), nullable=True)
    previous_year_q: Mapped[str] = mapped_column(String(500), nullable=True)
    book_recommendation: Mapped[str] = mapped_column(String(500), nullable=True)
    book_link: Mapped[str] = mapped_column(String(500), nullable=True)
    recommended_courses: Mapped[str] = mapped_column(String(500), nullable=True)
    recommended_courses_link: Mapped[str] = mapped_column(String(500), nullable=True)

# Create tables inside application context
with app.app_context():
    db.create_all()  # Ensure tables exist

    # ✅ Check if new columns exist in `Chapters`, and add them if missing
    existing_columns = db.session.execute(text("PRAGMA table_info(chapters)")).fetchall()
    column_names = [col[1] for col in existing_columns]

    new_columns = {
        "notes_link": "TEXT",
        "previous_year_q": "TEXT",
        "book_recommendation": "TEXT",
        "book_link": "TEXT",
        "recommended_courses": "TEXT",
        "recommended_courses_link": "TEXT"
    }

    for column, col_type in new_columns.items():
        if column not in column_names:
            db.session.execute(text(f"ALTER TABLE chapters ADD COLUMN {column} {col_type}"))

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
            Chapters(
                subject_name='Engineering Mathematics-I', chapter_name='Complex Numbers',
                video_url='https://youtube.com/playlist?list=PLT3bOBUU3L9jA-0qKbD2oHvNFCkwfBw-7&si=OIQz4q753sUmYgvd',
                notes_link="https://example.com/complex_numbers_notes.pdf",
                previous_year_q="https://example.com/complex_numbers_pyqs.pdf",
                book_recommendation="Advanced Engineering Mathematics by Erwin Kreyszig",
                book_link="https://example.com/buy_advanced_math",
                recommended_courses="Coursera - Engineering Mathematics",
                recommended_courses_link="https://coursera.org/eng_math"
            ),
            Chapters(
                subject_name='Engineering Mathematics-I',
                chapter_name='Hyperbolic Function and Logarithm of Complex Numbers',
                video_url='https://youtube.com/playlist?list=PLjgyGylma3IG5K2j24tEttFX0JAS3Rtp_&si=RJ_aV57ADaFSuz-Z',
                notes_link="https://example.com/hyperbolic_functions_notes.pdf",
                previous_year_q="https://example.com/hyperbolic_functions_pyqs.pdf",
                book_recommendation="Higher Engineering Mathematics by B.S. Grewal",
                book_link="https://example.com/buy_higher_math",
                recommended_courses="Udemy - Complex Numbers Masterclass",
                recommended_courses_link="https://udemy.com/complex_numbers"
            )
        ]
        db.session.add_all(chapter_list)
        db.session.commit()

    # ✅ Update a specific record (fixing typo)
    record_update = db.session.execute(db.select(Chapters).where(Chapters.id == 6)).scalar()
    if record_update:
        record_update.notes_link='https://drive.google.com/drive/u/0/folders/1Wf1WQUNDIuji1T1jvSeemvWYXrVaMnNk?sort=13&direction=a'
        record_update.previous_year_q='https://muquestionpapers.com/be/first-year-engineering/semester-1'
        record_update.book_recommendation = 'GV Kumbhojkar'
        record_update.book_link='https://drive.google.com/drive/u/0/folders/1Wf1WQUNDIuji1T1jvSeemvWYXrVaMnNk?sort=13&direction=a'
        record_update.recommended_courses='None'
        record_update.recommended_courses_link='None'
        db.session.commit()

# Routes
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

@app.route('/demo/<string:choice>', methods=['GET', 'POST'])
def demo(choice):
    chapter = Chapters.query.filter_by(chapter_name=choice).all()
    return render_template('demoresource.html', res=chapter)

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

# Email Function
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
