class AllCourses:
    def __init__(self,*args):
        self.courses = args
        self.names = [course.get_name() for course in args]
        self.lectureCodes = [course.get_lectureCodes() for course in args]
        self.sectionCodes = [course.get_sectionCodes() for course in args]
    
    def __len__(self):
        return len(self.courses)

    