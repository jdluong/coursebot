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

    def login(self):
        if not self.driver:
            self.init_browser(False)
        loggedIn = False
        while not loggedIn:
            try:
                self.login_webauth(self.driver)
                checkLoginSoup = BeautifulSoup(self.driver.page_source,'html.parser')
                # for testing
                # find_n_click_xpath(self.driver, elements.LOGOUT_BUTTON)
                # checkLoginSoup = BeautifulSoup(self.driver.page_source,'html.parser')

                # if enrollment_menu can't be found, then that means login wasn't successful
                find_n_click_xpath(self.driver,elements.ENROLLMENT_MENU)
                loggedIn = True
                print('Successfully logged in!')
            except NoSuchElementException: # if login was unsuccessful...
                self.login_status(checkLoginSoup,self.WebRegExtension,self.loginTimer)
            except:
                print("Something went very wrong")

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

    def enroll(self,coursesDict):
        tries = 0
        while False in self.lecEnrolled or False in self.disEnrolled:
            tries += 1 # for testing
            print("\n---------------------------------------------------------------------------\n")
            print("***************")
            print("*** TRY #",tries,"***")
            print("***************")
            for lectureInd in range(len(self.lectureCodes)):
                if not self.lecEnrolled[lectureInd]:
                    self.enroll_lec(lectureInd)               
                if not self.disEnrolled[lectureInd]:
                    # for each discussion code, in order of priority as inputted...
                    for prio in range(len(self.disCodes[lectureInd])):
                        added = self.enroll_dis(prio,lectureInd,coursesDict)
                        if added: break

            # testing
            print('\n**************')
            print('*** STATUS ***')
            print('**************\n')
            for bothSec in range(len(classNames)):
                if lecEnrolled[bothSec] and disEnrolled[bothSec]:
                    print('[x]',classNames[bothSec],'successfully enrolled')
                elif not lecEnrolled[bothSec] or not disEnrolled[bothSec]:
                    print('[ ]',classNames[bothSec],'NOT enrolled')
                    if not lecEnrolled[bothSec]:
                        print('- need LEC')
                    if not disEnrolled[bothSec]:
                        print('- need DIS')

            # if tries == 3:
            # 	break
            # testing
        # driver.quit()

    def add_course(self,driver,courseCode):
        """
        in webreg, adds the course specified with the classCode

        type lectureCode: string
        """
        find_n_click_xpath(driver,elements.ADD_RADIO)
        find_n_sendkeys(driver,elements.INPUT_COURSECODE,courseCode)
        find_n_click_xpath(driver,elements.SEND_REQUEST)

    def enroll_lec(self,lectureInd):
        """
        enrolls in current lecture in loop

        type lectureInd: int
        """
        self.add_course(self.driver,self.lectureCodes[lectureInd])
        checkLecSoup = BeautifulSoup(self.driver.page_source,'html.parser')
        self.check_lec_status(checkLecSoup,lectureInd)
        print('--')

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
        if checkDisSoup.find_all(string=re.compile("you have added")): # if added after dis
            self.disEnrolled[lectureInd] = True
            print("[x] {className} DIS SUCCESS (prio #{priority}); signed up after lecture".format(className=self.classNames[lectureInd],priority=prio+1))
            return True
        elif checkDisSoup.find_all(string=re.compile("You must successfully enroll in all co-classes")): # if added before dis
            self.disEnrolled[lectureInd] = True
            print("[x] {className} DIS SUCCESS (prio #{priority}); signed up before lecture".format(className=self.classNames[lectureInd],priority=prio+1))
            return True
        elif checkDisSoup.find_all(string=re.compile("This course is full")) == 1: # if unsuccessful
            print("[ ] DIS",prio+1,"IS FULL; will continue down prio")
            return False
        elif checkDisSoup.find("div","WebRegErrorMsg"):
            print('[ ]', self.classNames[lectureInd], 'DIS UNABLE TO ENROLL: "{msg}"'.format(msg=checkDisSoup.find("div","WebRegErrorMsg").string.strip()))
            return False
#----------------------------------- FANCY USER INPUT STUFF WILL DO LATER ------------------------------
    
    def courses_config(self):
        # Class info
        numClasses = int(input("Enter how many classes to sign up for: "))
        for classNum in range(numClasses):
            className = input("Name of course",classNum+1,"(e.g. ICS 31): ")
            lecCode = input("Lecture code for {className}:".format(className=className))
            separated = False
            while not separated:
                disCodesStr = input("Input {className}'s discussion codes, SEPARATED BY COMMAS: ".format(className=className))
                # check if disCodes are right
            # print: is this correct?
