from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from tools import find_n_click_name, find_n_click_xpath, find_n_sendkeys
import elements

import getpass
import re
import time

class LoginSetup:

    def __init__(self):
        self.username = ''
        self._pw = ''
        self.driver = None
        self.ERROR_PAGES_PATH = "error_pages/" # change this FOR WINDOWS?
        self.screenshotNum = 0
        self.testing = True

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
        self.username = input("-> Enter your UCInetID: ").strip()
    
    def set_pw(self):
        """
        sets password; doesn't ask for old password to validate a "reset"
        """
        # MAKE THIS MORE SECURE SOMEHOW
        same = False
        while not same:
            tempPW = getpass.getpass("-> Enter your password: ")
            pwCheck = getpass.getpass("-> Confirm your password: ")
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
        checkLoginSoup = BeautifulSoup(self.driver.page_source,'html.parser')
        return self.login_status(checkLoginSoup)
    
#------------------------- for self.test(isHeadless) ---------------------------

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
                self.redir_login(self.driver) 
                init = True
            except Exception as e:
                print("Something went wrong when using the browser:")
                print(f"{type(e)}: {e}")
                print("Retrying...")
                self.clean_driver()

    def login_status(self,checkLoginSoup,loginTimer=0):
        """
        uses checkLoginSoup to find what state the login is in and returns success or fail
        can extend to check webreg status with last two arguments

        type checkLoginSoup: BeautifulSoup
        type WebRegExtend: boolean
        type loginTimer: int

        rtype: boolean
        """
        if checkLoginSoup.find_all(string=re.compile("Invalid UCInetID or password")):
            print("Your UCInetID and password are incorrect. ")
            return False
        elif checkLoginSoup.find(id="status"): # too many failed logins, and maybe others?
            print('Unable to log in. "{msg}"'.format(msg=self.build_err_msg(checkLoginSoup,"status")))
            return False
        elif checkLoginSoup.find(class_="webauth-alert"): # general error messages (hopefully)
            print('Unable to log in. "{msg}"'.format(msg=self.build_err_msg(checkLoginSoup,"error-message")))
            return False
        elif checkLoginSoup.find_all(string=re.compile("UCInetID Secure Web Login")):
            print('Unable to log in for some reason.')
            self.save_page(self.driver)
            return False
        else: # means we're in webreg
            if self.testing:
                print("Your credentials successfully logged in!\nLogging out safely...")
                self.testing = False
                try:
                    find_n_click_xpath(self.driver, elements.TEST_LOGOUT)
                except Exception as e:
                    print("Couldn't log out safely:")
                    print(f"{type(e)}: {e}")
                    print("Continuing anyway...")
                    pass
                print("------------------------------------------------------------------")
                self.clean_driver()
            return True
            
                
    
    def redir_login(self,driver):
        """
        had to implement because after webreg goes down, "access webreg" doesn't lead to webauth
        login anymore; so have to find another link to validate; self.testing, will
        redirect to diff places

        type driver: webdriver
        """
        try:
            if self.testing:
                self.driver.get("https://www.reg.uci.edu/access/student/welcome/")
                find_n_click_xpath(self.driver,elements.TEST_LOGIN)
            else:
                self.driver.get("https://www.reg.uci.edu/registrar/soc/webreg.html")
                find_n_click_xpath(self.driver,elements.ACCESS_WEBREG_registrar)
        except Exception as e:
            print("Something went wrong with redirecting to login:")
            print(f"{type(e)}: {e}")


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
        """
        combines the print statement with the sleep statement
        
        type loginTimer: int
        """
        print("Trying again in",loginTimer,"seconds...\n--")
        time.sleep(loginTimer)

#----------------------- more general tools ------------------------

    def login_webauth(self,driver):
        """
        takes in driver and logs in, assuming it's in webauth site

        type driver: webdriver
        """
        find_n_sendkeys(driver,elements.UCINETID,self.username)
        find_n_sendkeys(driver,elements.PASSWORD,self._pw)
        find_n_sendkeys(driver,elements.PASSWORD,'\ue007')
    
    def save_page(self,driver):
        """
        saves screenshot and html of web page in driver; used primarily for saving
        error pages that we haven't accounted for 

        type driver: WebDriver
        """
        try:
            driver.save_screenshot(self.ERROR_PAGES_PATH+str(self.screenshotNum)+'.png')
            with open(self.ERROR_PAGES_PATH+str(self.screenshotNum)+'.html', 'w') as f:
                f.write(self.driver.page_source)
            self.screenshotNum+=1
        except:
            print("Something went wrong with saving the page. Continuing anyway...")
            pass
    
if __name__ == '__main__':
    test = LoginSetup()
    test.credentials_setup(False)