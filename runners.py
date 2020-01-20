from checker import Checker
from enroller import Enroller
from course import Course

from check import run_check
from login_config import run_login_config
from enroll import run_enrollment

# CHECKER

def check():

    checker = Checker('COMPSCI','122A','Dis')

    run_check(check)

# ENROLLER

def enroll_config():
    courses = (Course('BME150','13610',['13612','13611','13613']),)
    enroller = Enroller(3,*courses,headless=True)

    run_login_config(enroller)
    return enroller

def enroll_start(enroller,scheduler=None):
    run_enrollment(enroller)
    if scheduler: 
        scheduler.shutdown(wait=False)

# CHECKER AND ENROLLER

def check_enroll():
    dept, courseNum = 'BME','150'
    section_type = 'Dis'
    course_codes = '13610,13612,13613'

    checker = Checker(dept,courseNum,section_type,course_codes)
    enroller = Enroller(3,headless=True)

    run_login_config(enroller)
    enrolled = False
    while not enrolled:
        course_codes = run_check(checker)
        course = Course(checker.get_name(), course_codes['Lec'], course_codes[checker.get_section_type()])
        enrolled = run_enrollment(enroller,course)
        if enrolled:
            enroller.email_notif_enroller("luongjohnd@gmail.com")
    
if __name__ == '__main__':
    pass
