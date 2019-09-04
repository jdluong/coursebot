from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from tools import find_n_click_name, find_n_click_xpath

import getpass
import re

import elements

class LoginSetup:

    def __init__(self):
        self.username = ''
        self._pw = ''
        self.loginDriver = None
        self.success = False

    def credentials_setup(self):
        """
        driver method to set up ucinetid and pw, and test it
        """
        self.set_ucinetid()
        self.set_pw()
        return self.test()
    
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

    def test(self):
        """
        tests username and pw for validity and returns success

        rtype: boolean
        """
        if not self.loginDriver:
            print("Testing credentials....")
            self.init_browser(False)
        else:
            print("Re-testing credentials...")
        self.login_webauth(self.loginDriver)
        # ----TIMEOUT---- add timeout line (check for elements?)
        checkLoginSoup = BeautifulSoup(self.loginDriver.page_source,'html.parser')

        return self.login_status(checkLoginSoup)
    
#------------------------- tools in this class ---------------------------

    def clean_driver(self):
        """
        closes loginDriver window and reinitializes it as None

        type driver: webdriver
        """
        self.loginDriver.quit()
        self.loginDriver = None

    def init_browser(self,headless=True):
        """
        initializes (headless) browser for credentials testing; if headless = False, not headless

        type headless: boolean
        """
        init = False
        while not init:
            try: 
                if headless: # makes headless browser
                    options = webdriver.ChromeOptions()
                    options.headless = True
                    self.loginDriver = webdriver.Chrome(chrome_options=options)
                else:
                    self.loginDriver = webdriver.Chrome()
                # ----TIMEOUT---- replace line below with timeout
                self.loginDriver.get("https://www.reg.uci.edu/registrar/soc/webreg.html")
                find_n_click_xpath(self.loginDriver,elements.ACCESS_WEBREG_registrar)
                init = True
            except:
                print("Something went wrong when using the browser. Retrying...")
                self.clean_driver()

    def login_status(self,checkLoginSoup):
        """
        uses checkLoginSoup to find what state the login is in and returns success or fail

        type checkLoginSoup: BeautifulSoup

        rtype: boolean
        """
        if checkLoginSoup.find_all(string=re.compile("Invalid UCInetID or password")):
        # catches if wrong credentials
            self.success = False
            print("Your UCInetID and password are incorrect. Please re-enter your credentials")
            return self.success
        elif checkLoginSoup.find(id="error-message"): 
        # catches general error messages (hopefully)
            self.success = False
            errMsg = self.build_err_msg(checkLoginSoup)
            print('Unable to log in. "{msg}"'.format(msg=errMsg))
            # ... then what?
            return self.success
        else:
            self.success = True
            print("Your credentials successfully logged in!")
            print("Logging out safely...")
            find_n_click_xpath(self.loginDriver, elements.LOGOUT_BUTTON)
            print("------------------------------------------------------------------")
            self.clean_driver()
            return self.success

    def build_err_msg(self,soup):
        """
        builds error message from webauth login site
        need this because have to iterate, and it's too long/ugly to put in main method

        type soup: BeautifulSoup

        rtype: string
        """
        message = ''
        for line in soup.find(id="error-message").stripped_strings:
            message += line+" "
        return message.strip()

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
    