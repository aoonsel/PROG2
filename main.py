# importiere Flask und render_template, request
from flask import Flask, render_template, request

# importiere den ProgramController aus program_controller.py
from program_controller import ProgramController

# importiere den CourseController aus course_controller.py
from course_controller import CourseController

# flask app initialisieren
app = Flask(__name__)

## Hier werden die Routen definiert, die aufgerufen werden können
## Die Routen werden mit der Funktion render_template gerendert
## Die Templates befinden sich im Ordner templates


@app.route("/")
def home():
    # Diese Route zeigt die Startseite an.
    return render_template("index.html")


@app.route("/overview")
def overview():
    # Diese Route zeigt die Übersichtsseite an.

    # hole gewählten Studienplan
    program = ProgramController().get_program()

    # iteriere über alle gewählte Kurse und zähle bestandene ECTS
    sum_credits = 0
    for course_code in program:
        course = CourseController().get_course(course_code)
        if (
            program[course_code]["selected"]
            and "grade" in program[course_code]
            and program[course_code]["grade"] >= 4.0
        ):
            sum_credits += course["credits"]

    # iteriere über Module, überprüfe mind. Wahlcredits und erstelle eine Liste der Warnmeldungen.
    warning_messages = dict()
    # iteriere über alle Kategorien mit Modulen
    for category in CourseController().category_courses:
        min_credits = CourseController().category_courses[category][
            "elective_min_credits"
        ]
        temp_credits = 0
        # iteriere über alle gewählten Kurse in der Kategorie
        for course_code in program:
            course = CourseController().get_course(course_code)
            if (
                course["type"]
                and course["type"] == "elective"
                and program[course_code]["selected"]
                and category == CourseController().get_category(course_code)
            ):
                temp_credits += course["credits"]

        # Überprüfe, ob die mindest Anzahl an Wahlcredits erreicht wurde.
        if temp_credits < min_credits:
            warning_messages.update(
                {
                    category: f"Nicht genügend Credits in Kategorie. Es werden mindestens {str(min_credits)} Wahlcredits benötigt.",
                }
            )
        # Überprüfe, ob die Bachelorarbeit gewählt werden kann.
        if category == "Bachelorarbeit" and sum_credits < CourseController.START_THESIS:
            warning_messages.update(
                {
                    category: f"Nicht genügend Credits für Bachelorarbeit. Es werden mindestens {str(CourseController.START_THESIS)} Credits benötigt."
                }
            )

    category_courses_program = CourseController().category_courses
    # iteriere über alle gewählten Kurse
    for course_code in program:
        # iteriere über alle Kategorien mit Modulen
        for category in CourseController().category_courses:
            # iteriere über alle Kurse in der Kategorie
            for course in category_courses_program[category]["courses"]:
                # wenn Kurscode in der Kategorie gefunden wurde, aktualisiere Kurs
                if course["code"] == course_code:
                    course.update(program[course_code])
                    continue

    # kalkuliere Statistik für Kategorien
    # iteriere über alle Kategorien mit Modulen
    for category in category_courses_program:
        credits_per_category = 0
        elective_credits_per_category = 0
        # iteriere über alle Kurse in der Kategorie
        for course in category_courses_program[category]["courses"]:
            # wenn Kurs gewählt wurde, Note vorhanden ist und bestanden, addiere Credits
            if (
                "selected" in course
                and course["selected"]
                and "grade" in course
                and course["grade"] >= 4.0
            ):
                credits_per_category += course["credits"]
                # wenn Kurs ein Wahlkurs ist, addiere Credits
                if course["type"] == "elective":
                    elective_credits_per_category += course["credits"]
        category_courses_program[category]["category_credits"] = credits_per_category
        # verleihe Major-Titel wenn genügend Credits erreicht wurden (5 Wahlpflichtmodule; 20 ETCS)
        if elective_credits_per_category >= CourseController.MAJOR_CREDITS:
            category_courses_program[category]["major"]=True

    stats = {
        "credits": sum_credits,
        "min_credits": CourseController.NECESSARY_CREDITS,
    }

    return render_template(
        "overview.html",
        program=program,  # gewählter Studienplan
        category_courses=category_courses_program,  # Kategorien mit Modulen und Noten
        stats=stats,  # Statistik
        warning_messages=warning_messages,  # Warnmeldungen
    )


@app.route("/structure")
def structure():
    # Diese Route zeigt die Seite zum strukturieren des Studienplans an.
    return render_template(
        "structure.html",
        category_courses=CourseController().category_courses,
        program=ProgramController().get_program(),
    )


@app.route("/courses")
def courses():
    # Diese Route zeigt die Seite mit allen Modulen an.
    return render_template(
        "courses.html",
        category_courses=CourseController().category_courses,
    )


@app.route("/submit", methods=["POST"])
def submit():
    # Diese Route wird aufgerufen, wenn ein Modul gewählt oder bearbeitet wird.

    form_data = request.form
    # Daten aus dem Abgesendeten Formular auslesen, text zu int konvertieren
    course_code = int(form_data["course.code"])
    course = CourseController().get_course(course_code)

    # Überprüfen ob Note im Formular hinterlegt wurde
    grade = None
    if "grade" in form_data and form_data["grade"] != "":
        # Note aus Formular (Text) auslesen und zu float konvertieren
        grade = float(form_data["grade"])

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

    # zähle bestandene ECTS zusammen
    sum_credits = 0
    program = ProgramController().get_program()
    # iteriere über alle gewählten Kurse
    for course_code_temp in program:
        course_temp = CourseController().get_course(course_code_temp)
        # wenn Kurs gewählt wurde, Note vorhanden ist und bestanden, addiere Credits
        if (
            program[course_code_temp]["selected"]
            and "grade" in program[course_code_temp]
            and program[course_code_temp]["grade"] >= 4.0
        ):
            sum_credits += course_temp["credits"]

    # Thesis kann erst gewählt werden, wenn mindestens 140 Credits erreicht sind
    if course["name"] == "Thesis" and sum_credits < CourseController.START_THESIS:
        return render_template(
            "submit_error.html",
            error=f"Bachelorarbeit kann erst gewählt werden, wenn mindestens {CourseController.START_THESIS} Credits erreicht sind.",
        )

    # Note vom Praxistransfer muss vorhanden sein, um Unternehmensprojekt zu wählen
    # - > Note wird gesucht und in grade_praxis gespeichert
    grade_praxis = None
    # iteriere über alle gewählten Kurse
    for course_code_temp in program:
        course_temp = CourseController().get_course(course_code_temp)
        # wenn Kurs Fachpraktikum ist, speichere Note
        if course_temp["name"] == "Fachpraktikum":
            grade_praxis = program[course_code_temp]["grade"]
            break

    # Überprüfe ob Praxistransfer bestanden ist, wenn nicht-> Fehlermeldung
    if course["name"] == "Unternehmensprojekt" and (
        not grade_praxis or (grade_praxis and grade_praxis < 4.0)
    ):
        return render_template(
            "submit_error.html",
            error="Unternehmensprojekt kann erst gewählt werden, wenn Praxistransfer (Fachpraktikum) bestanden ist.",
        )

    # wenn Kurs nicht gewählt ist und keine Note hinterlegt ist, wird der Kurs aus dem Studienplan entfernt
    if grade is None and "selected" not in form_data and course_type == "elective":
        ProgramController().select_course(course_code)
        return "Modul ist nicht mehr gewählt!"

    # Modul wurde gewählt, schreibe neuen Studienplan in .pkl Datei
    ProgramController().select_course(course_code)

    # Modul wurde benotet, schreibe Note in .pkl Datei
    if grade is not None:
        ProgramController().set_grade(course_code, grade)

    # Rückgabe an Jinja Template
    return render_template(
        "submit_success.html",  # html template
        course=course,  # editierte Modul
        grade=grade,  # Note
    )


if __name__ == "__main__":
    # startet die Flask Applikation
    app.run(host="0.0.0.0", debug=True)
