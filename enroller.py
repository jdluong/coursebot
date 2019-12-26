from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException # for retry login
from bs4 import BeautifulSoup
from collections import deque

from scraper import Scraper
from loginsetup import LoginSetup
from tools import find_n_click_name, find_n_click_xpath, find_n_sendkeys, email_notif
import elements

import getpass
import re # regex
import time # for testing

class Enroller(LoginSetup):

    def __init__(self,loginTimer,*args,headless=True):
        super().__init__()
        self.loginTimer = loginTimer
        self.ref_courses = args
        self.courses = deque(args)
        self.headless = headless
        self.try_count = 100

    def login(self):
        """
        logging in while handling exceptions and checking status

        type headless: bool
        """
        if not self.driver:
            self.init_browser(self.headless)

        loggedIn = False
        while not loggedIn:
            try:
                self.login_webauth(self.driver)
                find_n_click_xpath(self.driver,elements.ENROLLMENT_MENU) # exception here if can't log in
                loggedIn = True
                print('Successfully logged into WebReg!')
            except NoSuchElementException: # if login was unsuccessful...
                checkLoginSoup = BeautifulSoup(self.driver.page_source,'html.parser')
                self.webreg_login_status(checkLoginSoup,self.loginTimer)
            except Exception as e:
                print("Something went wrong during the login process:")
                print(f"{type(e)}: {e}")
                self.save_page(self.driver)

    def enroll(self):
        """
        method for enrollment process logic for lecture and discussion, returns success/fail

        rtype: bool
        """
        tries = 0
        while self.courses:
            tries += 1
            if tries == self.try_count: break
            print("\n///\n*** ATTEMPT #{tryNum} ***\n///".format(tryNum=tries))
            course = self.courses.popleft()
            try:
                if not course.is_lec_enr():
                    if self.enroll_lec(course):
                        course.set_lec_enr(True)
                    print('-')
                if not course.is_section_enr():
                    if self.enroll_dis(course):
                        course.set_section_enr(True)
                    print('------------')
                if not course.is_enr():
                    self.courses.append(course)

            except (NoSuchElementException, StaleElementReferenceException): # if ever get logged out for some reason... ASSUMING STILL IN WEBREG
                for course in self.courses: course.fix_status() 
                print("ERR: Logged out of WebReg, for some reason:")
                checkSoup = BeautifulSoup(self.driver.page_source,'html.parser')
                self.webreg_login_status(checkSoup,0)
                self.login() # logs in, handles exception, AND gets us back to add/drop page
                print("Resuming enrollment process...")

        print("Logging out safely...")
        self.logout_webreg(self.driver)
        print("------------------------------------------------------------------")
        for course in self.courses: course.fix_status() # for when half of course is enrolled
        return len(self.courses) == 0


# ---------------------- for webregextension in self.login() ----------------------

    def webreg_login_status(self,checkLoginSoup,loginTimer=0):
        """
        extends login_status to handle WebReg statuses

        type checkLoginSoup: BeautifulSoup
        """
        if LoginSetup.login_status(self,checkLoginSoup,loginTimer): # if in webreg
            if checkLoginSoup.find_all(string=re.compile('WebReg is experiencing high traffic at this time.')):
                print('In WebReg, but can\'t log in because of high traffic.')
                self.WebRegWait(loginTimer)
                self.driver.refresh()
            elif checkLoginSoup.find("div","WebRegErrorMsg"):
                print('In WebReg, but can\'t log in: {msg}"'.format(msg=checkLoginSoup.find("div","WebRegErrorMsg").string.strip()))
                self.WebRegWait(loginTimer)
                find_n_click_xpath(self.driver,elements.ACCESS_WEBREG_webreg)
            else: # some other error we can't catch with class='WebRegErrorMsg'
                print("In WebReg, but can't log in for some reason.")
                self.save_page(self.driver)
                self.WebRegWait(loginTimer)
                try:
                    find_n_click_xpath(self.driver,elements.ACCESS_WEBREG_webreg)
                except:
                    self.redir_login(self.driver)

# ---------------------- for lecture enrollment in self.enroll(needToCheck) ----------------------

    def enroll_lec(self,course):
        """
        enrolls in current lecture in loop

        type lectureInd: int
        """
        self.add_course(self.driver,course.get_lecture())
        checkLecSoup = BeautifulSoup(self.driver.page_source,'html.parser')
        return self.check_lec_status(checkLecSoup,course.get_name())


    def check_lec_status(self,checkLecSoup,name):
        """
        checks the status of lecture after trying to add

        type checkLecSoup: BeautifulSoup
        type lectureInd: string
        """
        if checkLecSoup.find_all(string=re.compile("You must successfully enroll in all co-classes")): # if added before dis
            print(f"[x] {name} LEC SUCCESS; signed up before discussion")
            return True
        elif checkLecSoup.find_all(string=re.compile("you have added")): # if added after dis
            print(f"[x] {name} LEC SUCCESS; signed up after discussion")
            return True
        elif checkLecSoup.find_all(string=re.compile("This course is full")): # if unsuccessful
            print(f"[ ] {name}LEC IS FULL; will try again later")
            return False
        elif checkLecSoup.find("div","WebRegErrorMsg"):
            print('[ ] {name} LEC UNABLE TO ENROLL: "{msg}"'.format(name=name,msg=checkLecSoup.find("div","WebRegErrorMsg").string.strip()))
            return False
        else:
            print(f'[ ] {name} LEC UNABLE TO ENROLL FOR SOME REASON')
            self.save_page(self.driver)
            return False
    
    # ---------------------- for discussion enrollment in self.enroll(needToCheck) ----------------------

    def enroll_dis(self,course):
        """
        enrolls in current lecture's discussion (singular); returns if that dis was added

        type prio: int
        type lectureInd: int
        type needToCheck: bool

        rtype: bool
        """
        for prio,section in enumerate(course.get_sections(),1):
            self.add_course(self.driver,section)
            checkDisSoup = BeautifulSoup(self.driver.page_source,'html.parser')
            if self.check_dis_status(checkDisSoup,prio,course.get_name())
                return True
        return False

    def check_dis_status(self,checkDisSoup,prio,name):
        """
        checks the status of the current discussion after attempting to enroll in it

        type checkDisSoup: BeautifulSoup
        type prio: int
        type lectureInd: int
        """
        if checkDisSoup.find_all(string=re.compile("you have added")): # if added after dis
            print(f"[x] {name} DIS #{prio} SUCCESS; signed up after lecture")
            return True
        elif checkDisSoup.find_all(string=re.compile("You must successfully enroll in all co-classes")): # if added before dis
            print(f"[x] {name} DIS #{prio} SUCCESS; signed up before lecture")
            return True
        elif checkDisSoup.find_all(string=re.compile("This course is full")): # if unsuccessful
            print(f"[ ] {name} DIS #{prio} IS FULL; will continue down prio")
            return False
        elif checkDisSoup.find("div","WebRegErrorMsg"):
            print('[ ] {name} DIS #{priority} UNABLE TO ENROLL: "{msg}"'.format(name=name,prio=prio,msg=checkDisSoup.find("div","WebRegErrorMsg").string.strip()))
            return False
        else:
            print(f'[ ] {name} DIS #{priority} UNABLE TO ENROLL FOR SOME REASON.')
            self.save_page(self.driver)
            return False
    
    # ---------------------- for logging out of webreg  ----------------------

    def logout_webreg(self,driver):
        """
        method to log out of webreg safely; don't rly need to handle exceptions?

        type driver: webdriver
        """
        try:
            find_n_click_xpath(self.driver, elements.LOGOUT_BUTTON)
        except:
            print("Couldn't log out safely, for some reason.")

    # ---------------------- for sending email notification  ----------------------
    
    def email_notif_enroller(self,receiver):
        """
        builds body and sends email to a receiving email from the email in the config.py file

        type receiver: string
        """
        # message = 'Subject: {}\n\n{}'.format('email test',body)
        if self.courses:
            subj = "Could not enroll in all classes"
            body = "Could not enroll in: "
            for course in self.courses:
                body += course.get_name()+" "
        else:
            subj = "Sucessfully enrolled in all classes!"
            body = "Successfully enrolled in "+str(self.classNames)
        subject = "Subject: {subject}\n\n".format(subject=subj)
        email_notif(receiver,subject,body)

    # ---------------------- all-purpose method for adding courses  ----------------------
        # maybe this belongs in tools? idk
    def add_course(self,driver,courseCode):
        """
        in webreg, adds the course specified with the classCode

        type lectureCode: string
        """
        find_n_click_xpath(driver,elements.ADD_RADIO)
        find_n_sendkeys(driver,elements.INPUT_COURSECODE,courseCode)
        find_n_click_xpath(driver,elements.SEND_REQUEST)

if __name__ == '__main__':
    soup = BeautifulSoup(open('traffic_page.htm','r'),'html.parser')
    print(soup.find('div','DivLogoutMsg'))
