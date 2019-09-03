from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import getpass
import re

import elements

class LoginSetup:

    def __init__(self):
        self.username = ''
        self._pw = ''
        self.loginDriver = None
        self.success = False
    
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
            tempPW = getpass.getpass("Enter your UCInetID password: ")
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
            self.init_browser()
        else:
            print("Re-testing credentials...")

        ucinetid = self.loginDriver.find_element_by_name(elements.UCINETID)
        ucinetid.send_keys(self.username)
        password = self.loginDriver.find_element_by_name(elements.PASSWORD)
        password.send_keys(self._pw)
        password.send_keys('\ue007')
        checkLoginSoup = BeautifulSoup(self.loginDriver.page_source,'html.parser')

        # if checkLoginSoup.find_all(string=re.compile("Invalid UCInetID or password")):
        #     self.success = False
        #     print("Your UCInetID and password failed to login. Please re-enter your credentials")
        #     return self.success
        print(checkLoginSoup.find("div",id="error-message").string)
        if checkLoginSoup.find(id="error-message"):
            # still in login site
            print("Still in login site, can't log in. Err Msg:", checkLoginSoup.find(id="error-message").string[0])
        else:
            self.success = True
            logout_button = self.loginDriver.find_element_by_xpath(elements.LOGOUT_BUTTON)
            logout_button.click()
            print("Your UCInetID and password successfully logged in!")
            print("------------------------------------------------------------------")
            self.loginDriver.quit()
            self.loginDriver = None
            return self.success

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
                
                self.loginDriver.get("https://www.reg.uci.edu/registrar/soc/webreg.html")
                access_webreg = self.loginDriver.find_element_by_xpath(elements.ACCESS_WEBREG_registrar)
                access_webreg.click()
                init = True
            except:
                print("Something went wrong when using the browser. Retrying...")
                self.loginDriver.quit()
                self.loginDriver = None


    
    def credentials_setup(self):
        """
        driver method to set up ucinetid and pw
        """
        self.set_ucinetid()
        self.set_pw()
        return self.test()
