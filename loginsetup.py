from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from tools import find_n_click_name, find_n_click_xpath
import elements

import getpass
import re
import time

class LoginSetup:

    def __init__(self):
        self.username = ''
        self._pw = ''
        self.driver = None

    def credentials_setup(self,isHeadless):
        """
        driver method to set up ucinetid and pw, and test it; headless or not

        type isHeadless: boolean
        """
        self.set_ucinetid()
        self.set_pw()
        return self.test(isHeadless)
    
    def set_ucinetid(self):
        """
        sets ucinetid; doesn't require revalidation
        """
        self.username = input("Enter your UCInetID: ")
    
    def set_pw(self):
        """
        sets password; doesn't ask for old password to validate a "reset"
        """
    # MAKE THIS MORE SECURE SOMEHOW
    # if not self._pw:
        same = False
        while not same:
            tempPW = getpass.getpass("Enter your password: ")
            pwCheck = getpass.getpass("Confirm your password: ")
            if tempPW == pwCheck:
                same = True
                self._pw = tempPW
            else:
                print("Passwords didn't match! Please try again.")

    def test(self,isHeadless):
        """
        tests username and pw for validity and returns success

        type isHeadless: boolean

        rtype: boolean
        """
        if not self.driver:
            print("Testing credentials....")
            self.init_browser(isHeadless)
        else:
            print("Re-testing credentials...")
        self.login_webauth(self.driver)
        # ----TIMEOUT---- add timeout line (check for elements?)
        checkLoginSoup = BeautifulSoup(self.driver.page_source,'html.parser')

        return self.login_status(checkLoginSoup)
    
#------------------------- tools in this class ---------------------------

    def clean_driver(self):
        """
        closes driver window and reinitializes it as None

        type driver: webdriver
        """
        self.driver.quit()
        self.driver = None

    def init_browser(self,isHeadless):
        """
        initializes (isHeadless) browser for credentials testing; if headless = False, not headless

        type isHeadless: boolean
        """
        init = False
        while not init:
            try: 
                if isHeadless: # makes headless browser
                    options = webdriver.ChromeOptions()
                    options.headless = True
                    self.driver = webdriver.Chrome(chrome_options=options)
                else:
                    self.driver = webdriver.Chrome()
                # ----TIMEOUT---- replace line below with timeout
                self.driver.get("https://www.reg.uci.edu/registrar/soc/webreg.html")
                find_n_click_xpath(self.driver,elements.ACCESS_WEBREG_registrar)
                init = True
            except:
                print("Something went wrong when using the browser. Retrying...")
                self.clean_driver()

    def login_status(self,checkLoginSoup,WebRegExtension=None,loginTimer=0):
        """
        uses checkLoginSoup to find what state the login is in and returns success or fail
        can extend to check webreg with last argument

        type checkLoginSoup: BeautifulSoup
        type WebRegExtend: boolean
        type loginTimer: int

        rtype: boolean
        """
        if checkLoginSoup.find_all(string=re.compile("Invalid UCInetID or password")):
            print("Your UCInetID and password are incorrect. Please re-enter your credentials")
            if WebRegExtension:
                self.set_ucinetid()
                self.set_pw()
            return False
        elif checkLoginSoup.find(id="status"): # too many logins, and maybe others?
            print('Unable to log in. "{msg}"'.format(msg=self.build_err_msg(checkLoginSoup,"status")))
            if WebRegExtension: self.WebRegWait(loginTimer)
            return False
        elif checkLoginSoup.find(id="error-message"): # general error messages (hopefully)
            print('Unable to log in. "{msg}"'.format(msg=self.build_err_msg(checkLoginSoup,"error-message")))
            if WebRegExtension: self.WebRegWait(loginTimer)
            return False
        elif checkLoginSoup.find_all(string=re.compile("UCInetID Secure Web Login")):
            print('Unable to log in for some reason.')
            if WebRegExtension: self.WebRegWait(loginTimer)
        else: # means we're in webreg
            if WebRegExtension:
                WebRegExtension(checkLoginSoup)
            else:
                print("Your credentials successfully logged in!\nLogging out safely...")
                try:
                    find_n_click_xpath(self.driver, elements.LOGOUT_BUTTON)
                except:
                    pass
                print("------------------------------------------------------------------")
                self.clean_driver()
                return True

    def build_err_msg(self,soup,ID):
        """
        builds error message from webauth login site
        need this because have to iterate, and it's too long/ugly to put in main method

        type soup: BeautifulSoup
        type ID: string

        rtype: string 
        """
        message = ''
        for line in soup.find(id=ID).stripped_strings:
            message += line+" "
        return message.strip()

    def WebRegWait(self,loginTimer):
        print("Trying again in",loginTimer,"seconds...")
        print("--")
        time.sleep(loginTimer)

#----------------------- more general tools ------------------------

    def login_webauth(self,driver):
        """
        takes in driver and logs in, assuming it's in webauth site

        type driver: webdriver
        """
        ucinetid = driver.find_element_by_name(elements.UCINETID)
        ucinetid.send_keys(self.username)
        password = driver.find_element_by_name(elements.PASSWORD)
        password.send_keys(self._pw)
        password.send_keys('\ue007')
    