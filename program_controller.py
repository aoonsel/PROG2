import pickle
import os


# this class has the responsibility of managing the individual program of a student
# it is a singleton class, meaning that there can only be one instance of it
# this is because the program is a global variable that is used in multiple places
class ProgramController:
    _instance = None

    FILE_PATH = "data/program.pkl"

    # creates only a new object if it does not exist yet
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProgramController, cls).__new__(cls)

            # check if file exists
            if not os.path.exists(ProgramController.FILE_PATH):
                open(ProgramController.FILE_PATH, "wb").close()
                cls._instance.program = dict()
            else:
                cls._instance.program = cls.load_file()
        return cls._instance

    @staticmethod
    def get_program():
        return ProgramController().program

    @staticmethod
    def load_file():
        with open(ProgramController.FILE_PATH, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def write_file():
        with open(ProgramController.FILE_PATH, "wb") as f:
            pickle.dump(ProgramController().program, f)

    @staticmethod
    def select_course(course_code: int):
        ProgramController().program.update({course_code: {"selected": True}})
        ProgramController.write_file()

    @staticmethod
    def deselect_course(course_code: int):
        ProgramController().program.pop(course_code)
        ProgramController.write_file()

    @staticmethod
    def set_grade(course_code: int, grade: float):
        ProgramController().program.update(
            {course_code: {"grade": grade, "selected": True}}
        )
        ProgramController.write_file()
