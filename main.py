
from flask import Flask, render_template, request

from course_controller import CourseController

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/overview")
def overview():


    return render_template(
        "overview.html",

    )


@app.route("/structure")
def structure():
    return render_template(
        "structure.html",
        category_courses=CourseController().category_courses,
    )


@app.route("/courses")
def courses():
    return render_template(
        "courses.html",
        category_courses=CourseController().category_courses,
    )

@app.route("/submit", methods=["POST"])
def submit():

    course=None
    grade=None
    return render_template(
        "submit_success.html",
        course=course,
        grade=grade,
    )

if __name__ == "__main__":
    app.run(debug=True)
