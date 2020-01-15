from scraper import Scraper
from enroller import Enroller
from course import Course

from scrape import run_scrape
from login_config import run_login_config
from enroll import run_enrollment



def scrape():

    scraper = Scraper('COMPSCI','122A','Dis')

    run_scrape(scraper)

def enroll_config():
    courses = (Course('BME150','13610',['13612','13611','13613']),)
    enroller = Enroller(3,*courses,headless=True)

    run_login_config(enroller)
    return enroller

def enroll_start(enroller,scheduler=None):
    run_enrollment(enroller)
    if scheduler: 
        scheduler.shutdown(wait=False)


def scrape_enroll():
    dept, courseNum = 'BME','150'
    section_type = 'Dis'
    course_codes = '13610,13612,13613'

    scraper = Scraper(dept,courseNum,section_type,course_codes)
    enroller = Enroller(3,headless=True)

    run_login_config(enroller)
    enrolled = False
    while not enrolled:
        course_codes = run_scrape(scraper)
        course = Course(scraper.get_name(), course_codes['Lec'], course_codes[scraper.get_section_type()])
        enrolled = run_enrollment(enroller,course)
        if enrolled:
            enroller.email_notif_enroller("luongjohnd@gmail.com")
    
if __name__ == '__main__':

    mode = 'Scrape Enroll'

    if mode == 'Scrape':
        scraper = Scraper('COMPSCI','122A',section_type)

        run_scrape(scraper)


    if mode == 'Enroll':
        # courses = run_courses_config()
        courses = (Course('BME110B','13550',['13552','13551']),
                    Course('ICS45J','35530'),
                    Course('ICS45C','35520'))
        enroller = Enroller(3,*courses,headless=False)

        run_login_config(enroller)
        run_enrollment(enroller)


    if mode == 'Scrape Enroll':
        dept, courseNum = 'BME','110B'
        section_type = 'Dis'
        course_codes = '13550,13552,13551,13553'

        scraper = Scraper(dept,courseNum,section_type,course_codes)
        enroller = Enroller(3,headless=True)

        run_login_config(enroller)
        enrolled = False
        while not enrolled:
            course_codes = run_scrape(scraper)
            course = Course(scraper.get_name(), course_codes['Lec'], course_codes[scraper.get_section_type()])
            enrolled = run_enrollment(enroller,course)
            if enrolled:
                enroller.email_notif_enroller("luongjohnd@gmail.com")
