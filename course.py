class Course:
    def __init__(self, name, lecture, section_type=None, sections=[]):
        self.name = name
        self.lecture = lecture
        self.section_type = section_type
        self.sections = sections

        self.lec_enr = False
        self.section_enr = False if section_type else True
    
    def get_name(self):
        return self.name
    
    def get_lecture(self):
        return self.lecture
    
    def get_section_type(self):
        return self.section_type
    
    def get_sections(self):
        return self.sections
    
    def set_sections(self,sections):
        self.sections = sections
    
    def is_lec_enr(self):
        return self.lec_enr

    def set_lec_enr(self,enr):
        self.lec_enr = enr
    
    def is_section_enr(self):
        return self.section_enr
    
    def set_section_enr(self,enr):
        self.section_enr = enr
    
    
    def is_enr(self):
        return (self.lec_enr and self.section_enr))
    
    def fix_status(self):
        if not (self.lec_enr and self.section_enr):
            self.lec_enr = False
            if section_type:
                self.section_enr = False