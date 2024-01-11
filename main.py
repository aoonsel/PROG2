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
                course["type"]
                and course["type"] == "elective"
                and program[course_code]["selected"]
                and category == CourseController().get_category(course_code)
            ):
                temp_credits += course["credits"]

        if temp_credits < min_credits:
            warning_messages.update(
                {
                    category: f"Nicht genügend Credits in Kategorie. Es werden mindestens {str(min_credits)} Wahlcredits benötigt.",
                }
            )
        if category == "Bachelorarbeit" and sum_credits < CourseController.START_THESIS:
            warning_messages.update(
                {
                    category: f"Nicht genügend Credits für Bachelorarbeit. Es werden mindestens {str(CourseController.START_THESIS)} Credits benötigt."
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

    # überprüfen ob Note hinterlegt wurde
    grade = None
    if "grade" in form_data and form_data["grade"] != "":
        grade = float(form_data["grade"])
    else:
        grade = None

    # Note kann nicht hinterlegt werden, wenn Kurs nicht gewählt ist
    course_type = course["type"]
    if grade is not None and "selected" not in form_data and course_type == "elective":
        return render_template(
            "submit_error.html",
            error="Es kann keine Note für einen Kurs hinterlegen, der nicht gewählt ist.",
        )

    # wenn Kurs verpflichtend ist, muss Note hinterlegt sein
    if grade is None and course_type == "obligatory":
        return render_template(
            "submit_error.html",
            error="Es kann kein verpflichtenden Kurs ohne Note hinterlegen.",
        )

    sum_credits = 0
    program = ProgramController().get_program()
    for course_code_temp in program:
        course_temp = CourseController().get_course(course_code_temp)
        if (
            program[course_code_temp]["selected"]
            and "grade" in program[course_code_temp]
            and program[course_code_temp]["grade"] >= 4.0
        ):
            sum_credits += course_temp["credits"]

    # Thesis can only be selected when sum of credits is at least 140
    if course["name"] == "Thesis" and sum_credits < CourseController.START_THESIS:
        return render_template(
            "submit_error.html",
            error=f"Bachelorarbeit erst gewählt werden, wenn mindestens {CourseController.START_THESIS} Credits erreicht sind.",
        )

    # find grade of Praxistransfer in program
    grade_praxis = None
    for course_code_temp in program:
        course_temp = CourseController().get_course(course_code_temp)
        if course_temp["name"] == "Fachpraktikum":
            grade_praxis = program[course_code_temp]["grade"]
            break

    # Unternehmensprojekt can only be selected when Praxistransfer is passed
    if course["name"] == "Unternehmensprojekt" and (
        not grade_praxis or (grade_praxis and grade_praxis < 4.0)
    ):
        return render_template(
            "submit_error.html",
            error="Unternehmensprojekt kann erst gewählt werden, wenn Praxistransfer (Fachpraktikum) bestanden ist.",
        )

    # when course type elective, not selected and no grade, do delete course from program
    if grade is None and "selected" not in form_data and course_type == "elective":
        ProgramController().select_course(course_code)
        return "Modul ist nicht mehr gewählt!"

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
