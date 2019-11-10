class Course:
    def __init__(self,deptName,courseNum,lectureCodes,sectionCodes,section):
        self.deptName = deptName
        self.courseNum = courseNum
        self.name = deptName+courseNum
        self.lectureCodes = lectureCodes
        self.sectionCodes = sectionCodes
        self.section = section
    
    def get_deptName(self):
        return self.deptName

    def get_courseNum(self):
        return self.courseNum
    
    def get_name(self):
        return self.name

    def get_lectureCodes(self):
        return self.lectureCodes
    
    def get_sectionCodes(self):
        return self.sectionCodes
    
    def get_sectionType(self):
        return self.section