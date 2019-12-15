from scraper import Scraper
from signupper import SignUpper

from scrape import run_scrape
from login_config import run_login_config
from enroll import run_enrollment

class_names = ['CS122A']
lectures = ['34150']
sections = []
section_type = 'Dis'
course_codes = ''

mode = 'Scrape'

if __name__ == '__main__':
    if mode == 'Scrape':
        # scraper = Scraper('COMPSCI','122A',section_type)
        scraper = Scraper('BME','50A',section_type)
        
        run_scrape(scraper)


    if mode == 'Enroll':
        section = [['34155','34156','34154']]
        enroller = SignUpper(lectures,sections,class_names,3,True)

        run_login_config(enroller)
        run_enrollment(enroller)


    if mode == 'Scrape Enroll':
        scraper = Scraper('COMPSCI','122A',section_type)
        enroller = SignUpper(lectures,sections,class_names,3,True)

        run_login_config(enroller)
        enrolled = False
        while not enrolled:
            sections = run_scrape(scraper)
            enrolled = run_enrollment(enroller,sections)
            if enrolled:
                enroller.email_notif_signupper("luongjohnd@gmail.com")