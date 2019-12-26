from scraper import Scraper
from enroller import Enroller

from scrape import run_scrape
from login_config import run_login_config
from enroll import run_enrollment

class_names = ['BME110B']
lectures = ['13550'] 
sections = [['13552','13553','13551']]
section_type = 'Dis'
course_codes = lectures[0]+','+','.join(sections[0])

mode = 'Enroll'

if __name__ == '__main__':
    
    if mode == 'Scrape':
        scraper = Scraper('COMPSCI','122A',section_type)

        run_scrape(scraper)


    if mode == 'Enroll':
        enroller = Enroller(lectures,sections,class_names,3,False)

        run_login_config(enroller)
        run_enrollment(enroller)


    if mode == 'Scrape Enroll':
        # scraper = Scraper('COMPSCI','122A',section_type)
        scraper = Scraper('COMPSCI','122A',section_type, course_codes)
        enroller = Enroller(lectures,sections,class_names,3,True)

        run_login_config(enroller)
        enrolled = False
        while not enrolled:
            sections = run_scrape(scraper)[section_type]
            # print(sections)
            enrolled = run_enrollment(enroller,sections)
            if enrolled:
                enroller.email_notif_enroller("luongjohnd@gmail.com")
