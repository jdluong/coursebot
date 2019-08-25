from bs4 import BeautifulSoup
import requests
import time
import smtplib
import config

class Scraper:

    def __init__(self, deptName, courseNum, waitTime):
        self.deptName = deptName
        self.courseNum = courseNum
        self.BASE_URL = "https://www.reg.uci.edu/perl/WebSoc"
        self.params = {'Submit':'Display Web',
                        'YearTerm':'2019-92',
                        'ShowComments':'on',
                        'ShowFinals':'on',
                        'Breadth':'ANY',
                        'Dept':self.deptName,
                        'CourseNum':self.courseNum,
                        'Division':'ANY',
                        'ClassType':'ALL',
                        'FullCourses':'ANY',
                        'FontSize':'100',
                        'CancelledCourses':'Exclude'}
        self.coursesDict = {}

    def get_coursesDict(self):
        """ 
        get coursesDict member var
        """
        return self.coursesDict
        
    def soupify(self,url,params):
        """
        use url and its params to download html and returns a BeautifulSoup obj
        
        type url: string
        type params: dict

        rtype: BeautifulSoup
        """
        connected = False
        while not connected:
            try:
                html_page = requests.post(url,data=params).text # download html of webpage
                html_page.raise_for_status()
                connected = True
                return BeautifulSoup(html_page,'html.parser')
            except requests.exceptions.HTTPError as httpError:
                print("HTTP Error:",httpError)
                time.sleep(2)
            except requests.exceptions.ConnectTimeout:
                print("Took too long to connect to the server.")
                time.sleep(2)
            except requests.exceptions.ReadTimeout:
                print("Server took too long to send data.")
                time.sleep(2)
            except requests.exceptions.ConnectionError as connError:
                print("Connection Error:", connError)
                time.sleep(2)


    def parse_soup(self,soup):
        """
        parses soup to populate self.coursesDict with course info

        type soup: BeautifulSoup

        rtype: dict
        """
        rows = soup.find_all("tr", valign="top")[1::] # gets the rows containing data
        tempDict = {} 
        for row in rows:
            tempArray = [] # contains data per course; reinitialized each row
            for children in row.children: # can do same with rows[0] (w/o .children)
                tempArray.append(children.string) # make a list of each column's string, per element

            # SHOULD WE ONLY ADD COURSES THAT ARE OPEN????
            if tempArray[1] not in self.coursesDict: # for course types that aren't in the dict yet, add it
                tempDict[tempArray[0]] = tempArray[-1]
                self.coursesDict[tempArray[1]] = tempDict
                tempDict = {}
            else: 
                self.coursesDict[tempArray[1]][tempArray[0]] = tempArray[-1]
        
        return self.get_coursesDict()

    def email_notif(self,receiver):
        """
        sends email to a receiving email from the email in the config.py file

        type receiver: string
        """
        try:
            # setting up server
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            # login to throwaway email
            server.login(config.EMAIL_ADDRESS,config.PASSWORD)
            #send message
            message = 'Subject: {}\n\n{}'.format('email test',str(coursesDict))
            server.sendmail(config.EMAIL_ADDRESS,config.EMAIL_ADDRESS,message)
            server.quit()
            print("Email sent!")
        except :
            print("Email failed to send.")

    def run_scrape(self):
        """
        driver method to return coursesDict after scraping and parsing
        """
        return self.parse_soup(self.soupify(self.BASE_URL,self.params))
