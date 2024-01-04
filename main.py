from course_controller import CourseController
from flask import Flask, render_template, request

from program_controller import ProgramController

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/overview")
def overview():
    program = ProgramController().get_program()

    # count credits and selected courses
    sum_credits = 0
    for course_code in program:
        course = CourseController().get_course(course_code)
        if (
            program[course_code]["selected"]
            and "grade" in program[course_code]
            and program[course_code]["grade"] >= 4.0
        ):
            sum_credits += course["credits"]

    # iterate over program and check min elective credits
    warning_messages = dict()
    for category in CourseController().category_courses:
        min_credits = CourseController().category_courses[category][
            "elective_min_credits"
        ]
        temp_credits = 0
        for course_code in program:
            course = CourseController().get_course(course_code)
            if (
                course["type"] and
                course["type"] == "elective"
                and program[course_code]["selected"]
                and category == CourseController().get_category(course_code)
            ):
                temp_credits += course["credits"]

        if temp_credits < min_credits:
            warning_messages.update(
                {
                    category: f"Not enough credits in category. Need at least {str(min_credits)} elective credits."
                }
            )
        if category == "Bachelorarbeit" and sum_credits < CourseController.START_THESIS:
            warning_messages.update(
                {
                    category: f"Not enough credits to start thesis. Need at least {str(CourseController.START_THESIS)} credits in sum."
                }
            )


    category_courses_program = CourseController().category_courses
    # bring program information into course data
    for course_code in program:
        for category in CourseController().category_courses:
            for course in category_courses_program[category]["courses"]:
                if course["code"] == course_code:
                    course.update(program[course_code])
                    continue

    # calculate stats
    for category in category_courses_program:
        credits_per_category = 0
        for course in category_courses_program[category]["courses"]:
            if (
                "selected" in course
                and course["selected"]
                and "grade" in course
                and course["grade"] >= 4.0
            ):
                credits_per_category += course["credits"]
        category_courses_program[category]["category_credits"] = credits_per_category
        if credits_per_category >= CourseController.MAJOR_CREDITS:
            category_courses_program[category]["major"] = True

    stats = {
        "credits": sum_credits,
        "min_credits": CourseController.NECESSARY_CREDITS,
    }

    return render_template(
        "overview.html",
        program=program,
        category_courses=category_courses_program,
        stats=stats,
        warning_messages=warning_messages,
    )


@app.route("/structure")
def structure():
    return render_template(
        "structure.html",
        category_courses=CourseController().category_courses,
        program=ProgramController().get_program(),
    )


@app.route("/courses")
def courses():
    return render_template(
        "courses.html",
        category_courses=CourseController().category_courses,
    )


@app.route("/submit", methods=["POST"])
def submit():
    form_data = request.form

    course_code = int(form_data["course.code"])
    course = CourseController().get_course(course_code)

    # check if data attribute is present
    grade = None
    if "grade" in form_data and form_data["grade"] != "":
        grade = float(form_data["grade"])
    else:
        grade = None

    # cannot submit grade without being selected, when course is elective
    course_type = course["type"]
    if grade is not None and "selected" not in form_data and course_type == "elective":
        return render_template(
            "submit_error.html",
            error="Cannot submit grade for course without being selected.",
        )

    # when course type obligatory, grade must be submitted
    if grade is None and course_type == "obligatory":
        return render_template(
            "submit_error.html", error="Cannot submit obligatory course without grade."
        )
    
    sum_credits = 0
    program = ProgramController().get_program()
    for course_code in program:
        course = CourseController().get_course(course_code)
        if (
            program[course_code]["selected"]
            and "grade" in program[course_code]
            and program[course_code]["grade"] >= 4.0
        ):
            sum_credits += course["credits"]

    # Thesis can only be selected when sum of credits is at least 140
    if course["name"] == "Thesis" and sum_credits < CourseController.START_THESIS:
        return render_template(
            "submit_error.html", error=f"Not enough credits to start thesis. Need at least {CourseController.START_THESIS} credits in sum."
        )

    
    # find grade of Praxistransfer in program
    grade_praxis = None
    for course_code in program:
        course = CourseController().get_course(course_code)
        if course["name"] == "Praxistransfer":
            grade_praxis = program[course_code]["grade"]
            break

    # Unternehmensprojekt can only be selected when Praxistransfer is passed
    if not grade_praxis or (grade_praxis < 4.0 and course["name"] == "Unternehmensprojekt"):
        return render_template(
            "submit_error.html", error=f"Unternehmensprojekt kann erst gewählt werden, wenn Praxistransfer bestanden ist."
        )

    # when course type elective, not selected and no grade, do delete course from program
    if grade is None and "selected" not in form_data and course_type == "elective":
        ProgramController().select_course(course_code)
        return "Course is not selected anymore!"

    # write new program to file
    ProgramController().select_course(course_code)

    if grade is not None:
        ProgramController().set_grade(course_code, grade)

    return render_template(
        "submit_success.html",
        course=course,
        grade=grade,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
