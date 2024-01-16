# importiert yaml, um die yaml Datei zu laden
import yaml

# Diese Klasse hat die Verantwortung, das individuelle Programm eines Studenten zu verwalten
# Es handelt sich um eine Singleton-Klasse, was bedeutet, dass es nur eine Instanz davon geben kann
# Dies liegt daran, dass das Programm eine globale Variable ist, die an mehreren Stellen verwendet wird
# und es nicht sinnvoll ist, sie jedes Mal neu zu laden


class CourseController:
    _instance = None

    # 180 ECTS Punkte sind notwendig, um das Studium abzuschliessen
    NECESSARY_CREDITS = 180
    START_THESIS = 140  # Ab 140 ECTS Punkten kann die Bachelorarbeit begonnen werden
    MAJOR_CREDITS = 20  # 20 ECTS Punkte müssen in einem Fachgebiet erworben werden

    def __new__(cls):
        # erstellt nur ein Objekt dieser Klasse, wenn noch keines existiert
        if cls._instance is None:
            # Erstelle ein Objekt dieser Klasse
            cls._instance = super(CourseController, cls).__new__(cls)

            # lade YAML Datei mit Kursinformationen
            yml = yaml.load(
                open("data/courses.yaml", "r", encoding="utf-8"), Loader=yaml.FullLoader
            )

            # speichere Kursinformationen in Instanzvariablen
            cls._instance.category_courses = yml
            cls._instance.courses = cls.get_all_courses()

            # überprüfe, ob Kurse Codes doppelt vorhanden sind
            codes = []
            # iteriere über alle Kurse
            for course in cls._instance.courses:
                # wenn Kurscode bereits vorhanden ist, wirf Fehler
                if course["code"] in codes:
                    raise ValueError("Doppelter Kurscode: " + str(course["code"]) + "!")
                else:
                    codes.append(course["code"])

            # wandle Zeilenumbrüche der Beschreibung in </br> um
            for course in cls._instance.courses:
                course["description"] = course["description"].replace("\n", "</br>")

        return cls._instance

    # statische Methode, gibt Kurs anhand Kurscode zurück
    @staticmethod
    def get_course(course_id: int):
        for course in CourseController().courses:
            if course["code"] == course_id:
                return course

    # statische Methode, gibt alle Kurse zurück, nicht nach Kategorien sortiert
    @staticmethod
    def get_all_courses():
        categories = CourseController.get_categories()

        courses = []
        for category in categories:
            for course in CourseController().category_courses[category]["courses"]:
                courses.append(course)

        return courses

    # statische Methode, gibt alle Kategorien zurück, ohne Kurse zurück
    @staticmethod
    def get_categories():
        categories = []
        for course in CourseController().category_courses:
            categories.append(course)
        return categories

    # statische Methode, gibt Kategorie anhand Kurscode zurück
    @staticmethod
    def get_category(course_code: int):
        for category in CourseController().category_courses:
            for course in CourseController().category_courses[category]["courses"]:
                if course["code"] == course_code:
                    return category

    # statische Methode, gibt alle Kategorien Namen zurück
    @staticmethod
    def get_categories_name():
        categories = []

        for cat in CourseController().category_courses:
            categories.append(CourseController().category_courses[cat]["name"])

        return categories
