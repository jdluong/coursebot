from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException # for retry login
from bs4 import BeautifulSoup

from scraper import Scraper
from loginsetup import LoginSetup
from tools import find_n_click_name, find_n_click_xpath
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
            print("Retrying in",self.loginTimer,"seconds...\n--")
            time.sleep(self.loginTimer)
            find_n_click_xpath(self.driver,elements.ACCESS_WEBREG_webreg)
        else: # some other error we can't catch with class='WebRegErrorMsg'
            print("In webreg, but can't log in for some reason.")
            print("Retrying in",self.loginTimer,"seconds...\n--")
            time.sleep(self.loginTimer)
            find_n_click_xpath(self.driver,elements.ACCESS_WEBREG_webreg)

    def enrollment(self):
        lecEnrolled = [False] * len(lectureCodes)
        disEnrolled = [False] * len(lectureCodes)
        tries = 0
        # maybe a while loop saying while False in lecEnrolled or False in disEnrolled?
        # but how would we get it to try to sign up for lec/dis that is False? 
        # maybe it's not as clean to write another condition for a "retry", or going back
        # so maybe we should have a condition of "if True: skip, if False, do it all again" in the for loop?
        while False in lecEnrolled or False in disEnrolled:

            # testing

            tries += 1
            print("\n---------------------------------------------------------------------------\n")
            print("***************")
            print("*** TRY #",tries,"***")
            print("***************")

            for lectureInd in range(len(lectureCodes)):

                print('\n---------')
                print(classNames[lectureInd],'|')
                print('---------')

                #######################
                ##### ADD LECTURE #####
                #######################

                if lecEnrolled[lectureInd] == False: # if lecture not signed up yet
                    # finds "add" radio button and clicks it
                    add_radio = driver.find_element_by_xpath("//input[@type='radio'][@id='add']")
                    add_radio.click()

                    # finds the input box for the code, input the lecture code, and submits it
                    courseCode_input = driver.find_element_by_name("courseCode")
                    courseCode_input.send_keys(lectureCodes[lectureInd])

                    # find the send request button and press it
                    sendRequest_button = driver.find_element_by_xpath("//input[@type='submit'][@value='Send Request']")
                    sendRequest_button.click()

                    # check if lecture sign up was successful
                    time.sleep(1) # in case the next page takes a whiel to load
                    checkLecSoup = BeautifulSoup(driver.page_source,'html.parser')

                    if checkLecSoup.find_all(string=re.compile("You must successfully enroll in all co-classes")): # if added before dis
                        print("[x] LEC SUCCESS; signed up before discussion")
                        lecEnrolled[lectureInd] = True
                    elif checkLecSoup.find_all(string=re.compile("you have added")): # if added after dis
                        print("[x] LEC SUCCESS; signed up after discussion")
                        lecEnrolled[lectureInd] = True
                    elif checkLecSoup.find_all(string=re.compile("This course is full")): # if unsuccessful
                        print("[ ] LEC IS FULL; will try again later")
                        pass
                
                print('--')

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
