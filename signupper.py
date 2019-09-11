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
                print('Successfully logged into WebReg!\nBeginning enrollment process...')
            except NoSuchElementException: # if login was unsuccessful...
                self.login_status(checkLoginSoup,self.WebRegExtension,self.loginTimer)
            except:
                print("Something went very wrong")

    def enroll(self,coursesDict):
        """
        method for enrollment process logic for lecture and discussion

        type coursesDict: dict
        """
        tries = 0
        while False in self.lecEnrolled or False in self.disEnrolled:
            tries += 1 # for testing
            print("\n///\n*** ATTEMPT #{tryNum} ***\n///".format(tryNum=tries))
            for lectureInd in range(len(self.lectureCodes)):
                if not self.lecEnrolled[lectureInd]:
                    self.enroll_lec(lectureInd)               
                if not self.disEnrolled[lectureInd]:
                    # for each discussion code, in order of priority as inputted...
                    for prio in range(len(self.disCodes[lectureInd])):
                        added = self.enroll_dis(prio,lectureInd,coursesDict)
                        if added: break
                    print('------------')
            self.print_courses_status(tries)
        # start test code
            if tries == 3: break
        find_n_click_xpath(self.driver, elements.LOGOUT_BUTTON)
        # end test code
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
            pass
        elif checkLecSoup.find("div","WebRegErrorMsg"):
            print('[ ]', self.classNames[lectureInd], 'LEC UNABLE TO ENROLL: "{msg}"'.format(msg=checkLecSoup.find("div","WebRegErrorMsg").string.strip()))
            pass

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
