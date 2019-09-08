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

    def enroll(self):
        tries = 0
        while False in self.lecEnrolled or False in self.disEnrolled:
            tries += 1 # for testing
            print("\n---------------------------------------------------------------------------\n")
            print("***************")
            print("*** TRY #",tries,"***")
            print("***************")
            for lectureInd in range(len(self.lectureCodes)):
                # ADDING LECTURE
                if self.lecEnrolled[lectureInd] == False:
                    self.enroll_lec(lectureInd)                
                ####################
                ##### ADD DIS ###### this is obnoxious because look below
                ####################
                if disEnrolled[lectureInd] == False:
                    for prio, disCode in enumerate(disCodes[lectureInd]): # for each discussion code, in order of priority as inputted...
                        if needToCheck:
                            # 1) do we need these following two if-statements if the point of this block
                            # is to go through the priority list in order and sign up for whichever's
                            # open first?
                            # 2) the primary reason i can think of to keep these is to ensure their codes
                            # are right? but would we even need the "OPEN" statement
                            # 3) but to make the code more concise (and without if-statements), it would
                            # make sense to forego these big if-statements for the needToCheck = False case,
                            # because we wouldn't have a coursesDict
                            if disCode in coursesDict['Dis']:
                                if coursesDict['Dis'][disCode] == "OPEN": # if that discussion is open...
                                    # find add radio button and click it
                                    add_radio = driver.find_element_by_xpath("//input[@type='radio'][@id='add']")
                                    add_radio.click()

                                    # find course code input box and enter current discussion code
                                    courseCode_input = driver.find_element_by_name("courseCode")
                                    courseCode_input.send_keys(disCode)

                                    # find send request button and click it
                                    sendRequest_button = driver.find_element_by_xpath("//input[@type='submit'][@value='Send Request']")
                                    sendRequest_button.click()

                                    # have to check if it was successfully added
                                    checkSoup = BeautifulSoup(driver.page_source,'html.parser')
                                    addedCheck = checkSoup.find_all("h2")
                                    if addedCheck[0].string.strip() == "you have added": # if successfully added AFTER lecture...
                                        print('you got your priority #', prio+1, 'for lecture', lectureCodes[lectureInd])
                                        disEnrolled[lectureInd] == True
                                        break # stop trying to add future discussions
                                else: # else, go to next discussion code 
                                    pass
                        else:
                            # find add radio button and click it
                            add_radio = driver.find_element_by_xpath("//input[@type='radio'][@id='add']")
                            add_radio.click()

                            # find course code input box and enter current discussion code
                            courseCode_input = driver.find_element_by_name("courseCode")
                            courseCode_input.send_keys(disCode)

                            # find send request button and click it
                            sendRequest_button = driver.find_element_by_xpath("//input[@type='submit'][@value='Send Request']")
                            sendRequest_button.click()

                            # have to check if it was successfully added
                            # checkSoup = BeautifulSoup(driver.page_source,'html.parser')
                            # addedCheck = checkSoup.find_all("h2")

                            # checking if discussion sign up was successful
                            # time.sleep(1)
                            checkDisSoup = BeautifulSoup(driver.page_source,'html.parser')

                            if len(checkDisSoup.find_all(string=re.compile("you have added"))) == 1: # if added after dis
                                disEnrolled[lectureInd] = True
                                print("[x] DIS",prio+1,"SUCCESS; signed up after lecture")
                                # print('    - you got your priority #', prio+1, 'for', classNames[lectureInd])
                                break
                            elif len(checkDisSoup.find_all(string=re.compile("You must successfully enroll in all co-classes"))) == 1: # if added before dis
                                disEnrolled[lectureInd] = True
                                print("[x] DIS",prio+1,"SUCCESS; signed up before lecture")
                                # print('    - you got your priority #', prio+1, 'for', classNames[lectureInd])
                                break
                            elif len(checkDisSoup.find_all(string=re.compile("This course is full"))) == 1: # if unsuccessful
                                print("[ ] DIS",prio+1,"IS FULL; continue to try")
                            else:
                                print("[ ] DIS",prio+1,"ERROR")

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

    def enroll_lec(self,lectureInd):
        """
        enrolls in current lecture in loop

        type lectureInd: int
        """
        self.add_lecture(self.lectureCodes[lectureInd])
        checkLecSoup = BeautifulSoup(self.driver.page_source,'html.parser')
        self.check_lec_status(checkLecSoup,lectureInd)
        print('--')

    def add_lecture(self,lectureCode):
        """
        in webreg, adds current lecture in loop 

        type lectureCode: string
        """
        find_n_click_xpath(self.driver,elements.ADD_RADIO)
        find_n_sendkeys(self.driver,elements.INPUT_COURSECODE,lectureCode)
        find_n_click_xpath(self.driver,elements.SEND_REQUEST)

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
            print("[ ] LEC IS FULL; will try again later")
            pass
        elif checkLecSoup.find("div","WebRegErrorMsg"):
            print('[ ] UNABLE TO ENROLL: "{msg}"'.format(msg=checkLecSoup.find("div","WebRegErrorMsg").string.strip()))
            pass

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
