# Importiere das Modul yaml, das zum Lesen und Schreiben von YAML-Dateien verwendet wird.
import pickle

# importiere os Modul, das zum Erstellen und Verwalten von Dateien verwendet wird
import os


# Diese Klasse hat die Verantwortung, das individuelle Programm eines Studenten zu verwalten
# Es handelt sich um eine Singleton-Klasse, was bedeutet, dass es nur eine Instanz davon geben kann
# Dies liegt daran, dass das Programm eine globale Variable ist, die an mehreren Stellen verwendet wird
# und es nicht sinnvoll ist, sie jedes Mal neu zu laden
class ProgramController:
    _instance = None

    FILE_PATH = "data/program.pkl"  # Dateipfad der .pkl Datei

    # erstellt nur ein Objekt dieser Klasse, wenn noch keines existiert
    def __new__(cls):
        # Überprüfe, ob bereits ein Objekt dieser Klasse existiert
        if cls._instance is None:
            # Erstelle ein Objekt dieser Klasse
            cls._instance = super(ProgramController, cls).__new__(cls)

            # überprüfen ob .pkl Datei existiert
            if not os.path.exists(ProgramController.FILE_PATH):
                # wenn nicht, erstelle leere .pkl Datei
                open(ProgramController.FILE_PATH, "wb").close()
                cls._instance.program = dict()
            else:
                # wenn ja, lade .pkl Datei
                cls._instance.program = cls.load_file()
        return cls._instance

    # statische Methode, gibt gewählte Studienprogramm zurück
    @staticmethod
    def get_program():
        return ProgramController().program

    # statische Methode, lädt .pkl Datei vom Dateipfad
    @staticmethod
    def load_file():
        with open(ProgramController.FILE_PATH, "rb") as f:
            return pickle.load(f)

    # statische Methode, schreibt .pkl Datei zum Dateipfad
    @staticmethod
    def write_file():
        with open(ProgramController.FILE_PATH, "wb") as f:
            pickle.dump(ProgramController().program, f)

    # statische Methode, wählte einen Kurs im Studienprogramm aus
    @staticmethod
    def select_course(course_code: int):
        ProgramController().program.update({course_code: {"selected": True}})
        ProgramController.write_file()

    # statische Methode, wählt einen Kurs im Studienprogramm ab
    @staticmethod
    def deselect_course(course_code: int):
        ProgramController().program.pop(course_code)
        ProgramController.write_file()

    # statische Methode, setzt Note für einen Kurs im Studienprogramm
    @staticmethod
    def set_grade(course_code: int, grade: float):
        ProgramController().program.update(
            {course_code: {"grade": grade, "selected": True}}
        )
        ProgramController.write_file()
