import yaml

# this class has the responsibility of managing the courses with their information such as credits, name, etc.
# courses are categorized into categories, such as "social studies" or "computer science"
# this is a singleton class, meaning that there can only be one instance of it


class CourseController:
    _instance = None

    def __new__(cls):
        # creates only a new object if it does not exist yet
        if cls._instance is None:
            cls._instance = super(CourseController, cls).__new__(cls)

            yml = yaml.load(open("data/courses.yaml", "r"), Loader=yaml.FullLoader)
            cls._instance.category_courses = yml
            cls._instance.courses = cls.get_all_courses()

            # check for duplicate course codes
            codes = []
            for course in cls._instance.courses:
                if course["code"] in codes:
                    raise ValueError(
                        "Duplicate course code: " + str(course["code"]) + "!"
                    )
                else:
                    codes.append(course["code"])

        return cls._instance

    @staticmethod
    def get_course(course_id: int):
        for course in CourseController().courses:
            if course["code"] == course_id:
                return course

    @staticmethod
    def get_all_courses():
        categories = CourseController.get_categories()

        courses = []
        for category in categories:
            for course in CourseController().category_courses[category]["courses"]:
                courses.append(course)

        return courses

    @staticmethod
    def get_category(course_code: int):
        for category in CourseController().category_courses:
            for course in CourseController().category_courses[category]["courses"]:
                if course["code"] == course_code:
                    return category
    
    #test
    @staticmethod
    def get_categories():
        categories = []
        for course in CourseController().category_courses:
            categories.append(course)
        return categories