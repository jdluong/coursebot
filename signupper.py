from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException # for retry login
from bs4 import BeautifulSoup

from scraper import Scraper
from loginsetup import LoginSetup
from tools import find_n_click_name, find_n_click_xpath, find_n_sendkeys
import elements

import getpass
import re # regex
import time # for testing

class SignUpper(LoginSetup):

    def __init__(self,lectureCodes,disCodes,classNames):
        super().__init__()
        self.classNames = classNames
        self.lectureCodes = lectureCodes
        self.disCodes = disCodes
        self.loginTimer = 60
        self.lecEnrolled = [False] * len(self.lectureCodes)
        self.disEnrolled = [False] * len(self.lectureCodes)

    def login(self,headless):
        """
        logging in while handling exceptions and checking status
        """
        if not self.driver:
            self.init_browser(headless)
        loggedIn = False
        while not loggedIn:
            try:
                self.login_webauth(self.driver)
                checkLoginSoup = BeautifulSoup(self.driver.page_source,'html.parser')
                # find_n_click_xpath(self.driver, elements.LOGOUT_BUTTON)
                # checkLoginSoup = BeautifulSoup(self.driver.page_source,'html.parser')
                find_n_click_xpath(self.driver,elements.ENROLLMENT_MENU) # exception here if can't log in
                loggedIn = True
                print('Successfully logged into WebReg!')
            except NoSuchElementException: # if login was unsuccessful...
                self.login_status(checkLoginSoup,self.WebRegExtension,self.loginTimer)
            except:
                print("Something went very wrong during the login process.")
                self.save_page(self.driver)

    def enroll(self,coursesDict):
        """
        method for enrollment process logic for lecture and discussion

        type coursesDict: dict
        """
        tries = 0
        disTries = 0 # for testing
        while False in self.lecEnrolled or False in self.disEnrolled:
            try:
                tries += 1 # for testing
                print("\n///\n*** ATTEMPT #{tryNum} ***\n///".format(tryNum=tries))
                for lectureInd in range(len(self.lectureCodes)):
                    if not self.lecEnrolled[lectureInd]:
                        self.enroll_lec(lectureInd) # tries enroll_lec, and returns success         
                    if not self.disEnrolled[lectureInd]:
                        # for each discussion code, in order of priority as inputted...
                        for prio in range(len(self.disCodes[lectureInd])):
                            disTries+=1
                            # START TEST CODE
                            if disTries == 2:
                                find_n_click_xpath(self.driver, elements.LOGOUT_BUTTON)
                            # END TEST CODE
                            added = self.enroll_dis(prio,lectureInd,coursesDict)
                            if added: break
                        print('------------')
                self.print_courses_status(tries)

                print("Logging out safely...")
                find_n_click_xpath(self.driver, elements.LOGOUT_BUTTON)
                print("------------------------------------------------------------------")
            except NoSuchElementException: # if ever get logged out for some reason...
                # THIS IS ASSUMING WE'RE STILL IN WEBREG WHEN WE GET KICKED OFF!!
                self.fix_logic() # fixes lecEnrolled and disEnrolled when we get kicked off
                print("ERR: Logged out of WebReg, for some reason:")
                checkSoup = BeautifulSoup(self.driver.page_source,'html.parser')
                # self.save_page(self.driver)
                self.WebRegExtension(checkSoup) # assuming we're in webreg; we can do self.login_status(checkSoup,self.WebRegExtension,self.loginTimer)
                self.login(headless=True) # logs in , handles exception, AND gets us back to add/drop page
                print("Resuming enrollment process...")


# ---------------------- for webregextension in self.login() ----------------------

    def WebRegExtension(self,checkLoginSoup):
        """
        extends login_status to handle WebReg statuses

        type checkLoginSoup: BeautifulSoup
        """
        if checkLoginSoup.find("div","WebRegErrorMsg"):
            print('In WebReg, but can\'t log in. "{msg}"'.format(msg=checkLoginSoup.find("div","WebRegErrorMsg").string.strip()))
            self.WebRegWait(self.loginTimer)
            find_n_click_xpath(self.driver,elements.ACCESS_WEBREG_webreg)
        else: # some other error we can't catch with class='WebRegErrorMsg'
            print("In WebReg, but can't log in for some reason.")
            self.save_page(self.driver)
            self.WebRegWait(self.loginTimer)
            find_n_click_xpath(self.driver,elements.ACCESS_WEBREG_webreg)

# ---------------------- for lecture enrollment in self.enroll(coursesDict) ----------------------

    def enroll_lec(self,lectureInd):
        """
        enrolls in current lecture in loop

        type lectureInd: int
        """
        self.add_course(self.driver,self.lectureCodes[lectureInd])
        checkLecSoup = BeautifulSoup(self.driver.page_source,'html.parser')
        self.check_lec_status(checkLecSoup,lectureInd)
        print('-')


    def check_lec_status(self,checkLecSoup,lectureInd):
        """
        checks the status of lecture after trying to add

        type checkLecSoup: BeautifulSoup
        type lectureInd: string
        """
        if checkLecSoup.find_all(string=re.compile("You must successfully enroll in all co-classes")): # if added before dis
            print("[x]", self.classNames[lectureInd], "LEC SUCCESS; signed up before discussion")
            self.lecEnrolled[lectureInd] = True
        elif checkLecSoup.find_all(string=re.compile("you have added")): # if added after dis
            print("[x]", self.classNames[lectureInd], "LEC SUCCESS; signed up after discussion")
            self.lecEnrolled[lectureInd] = True
        elif checkLecSoup.find_all(string=re.compile("This course is full")): # if unsuccessful
            print("[ ]", self.classNames[lectureInd], "LEC IS FULL; will try again later")
        elif checkLecSoup.find("div","WebRegErrorMsg"):
            print('[ ]', self.classNames[lectureInd], 'LEC UNABLE TO ENROLL: "{msg}"'.format(msg=checkLecSoup.find("div","WebRegErrorMsg").string.strip()))
        else:
            print('[ ]', self.classNames[lectureInd], 'LEC UNABLE TO ENROLL FOR SOME REASON')
            self.save_page(self.driver)
    
    # ---------------------- for discussion enrollment in self.enroll(coursesDict) ----------------------

    def enroll_dis(self,prio,lectureInd,coursesDict):
        """
        enrolls in current lecture's discussion (singular); returns if that dis was added

        type prio: int
        type lectureInd: int
        type needToCheck: bool

        rtype: bool
        """
        disCode = self.disCodes[lectureInd][prio]
        if coursesDict:
            if disCode in coursesDict['Dis']:
                if coursesDict['Dis'][disCode] == "OPEN": # if that discussion is open...
                    self.add_course(self.driver,disCode)
                    checkDisSoup = BeautifulSoup(self.driver.page_source,'html.parser')
                    return self.check_dis_status(checkDisSoup,prio,lectureInd)
                else: # else, go to next discussion code 
                    print("[ ] {className} DIS #{priority} IS FULL; will continue down prio".format(className=self.classNames[lectureInd],priority=prio+1))
                    return False
        else:
            self.add_course(self.driver,disCode)
            checkDisSoup = BeautifulSoup(self.driver.page_source,'html.parser')
            return self.check_dis_status(checkDisSoup,prio,lectureInd)

    def check_dis_status(self,checkDisSoup,prio,lectureInd):
        """
        checks the status of the current discussion after attempting to enroll in it

        type checkDisSoup: BeautifulSoup
        type prio: int
        type lectureInd: int
        """
        if checkDisSoup.find_all(string=re.compile("you have added")): # if added after dis
            self.disEnrolled[lectureInd] = True
            print("[x] {className} DIS #{priority} SUCCESS; signed up after lecture".format(className=self.classNames[lectureInd],priority=prio+1))
            return True
        elif checkDisSoup.find_all(string=re.compile("You must successfully enroll in all co-classes")): # if added before dis
            self.disEnrolled[lectureInd] = True
            print("[x] {className} DIS #{priority} SUCCESS; signed up before lecture".format(className=self.classNames[lectureInd],priority=prio+1))
            return True
        elif checkDisSoup.find_all(string=re.compile("This course is full")) == 1: # if unsuccessful
            print("[ ] {className} DIS #{priority} IS FULL; will continue down prio".format(className=self.classNames[lectureInd],priority=prio+1))
            return False
        elif checkDisSoup.find("div","WebRegErrorMsg"):
            print('[ ] {className} DIS #{priority} UNABLE TO ENROLL: "{msg}"'.format(className=self.classNames[lectureInd],priority=prio+1,msg=checkDisSoup.find("div","WebRegErrorMsg").string.strip()))
            return False
        else:
            print('[ ] {className} DIS #{priority} UNABLE TO ENROLL FOR SOME REASON.')
            self.save_page(self.driver)
            return False

# ---------------------- for fixing logic when kicked off WebReg ----------------------

    def fix_logic(self):
        """
        fixes logic in the case that we get kicked out of webreg, because when we get kicked out,
        the single dis or lec gets dropped and we have to start over. without this, the program
        thinks we are actually enrolled in it when it logs back in and resumes
        """
        for lecInd in range(len(self.lecEnrolled)):
            if not (self.lecEnrolled[lecInd] and self.disEnrolled[lecInd]):
                self.lecEnrolled[lecInd] = False
                self.disEnrolled[lecInd] = False

# ---------------------- for printing status in self.enroll(coursesDict) ----------------------

    def print_courses_status(self,tries):
        """
        prints course status after each try

        type tries: int
        """
        # print('\n* STATUS #{tryNum} *'.format(tryNum=tries))
        for bothSec in range(len(self.classNames)):
            if self.lecEnrolled[bothSec] and self.disEnrolled[bothSec]:
                print('[x] {name} successfully enrolled!'.format(name=self.classNames[bothSec]))
            elif not self.lecEnrolled[bothSec] or not self.disEnrolled[bothSec]:
                print('[ ] {name} NOT enrolled (need'.format(name=self.classNames[bothSec]),end='')
                if not self.lecEnrolled[bothSec]:
                    print(' LEC',end='')
                if not self.disEnrolled[bothSec]:
                    print(' DIS',end='')
                print(')')

    # ---------------------- all-purpose method for adding courses  ----------------------

    def add_course(self,driver,courseCode):
        """
        in webreg, adds the course specified with the classCode

        type lectureCode: string
        """
        find_n_click_xpath(driver,elements.ADD_RADIO)
        find_n_sendkeys(driver,elements.INPUT_COURSECODE,courseCode)
        find_n_click_xpath(driver,elements.SEND_REQUEST)
