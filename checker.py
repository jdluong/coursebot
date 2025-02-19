from bs4 import BeautifulSoup
import requests
import time
import smtplib
import json
from collections import defaultdict

from tools import email_notif

class Checker:
    def __init__(self, dept, courseNum, section_type=None, courseCodes=''):
        self.dept = dept
        self.courseNum = courseNum
        self.BASE_URL = "https://www.reg.uci.edu/perl/WebSoc"
        self.params = {'Submit':'Display Web',
                        'YearTerm':'2020-03',
                        'ShowComments':'on',
                        'ShowFinals':'on',
                        'Breadth':'ANY',
                        'Dept':dept,
                        'CourseNum':courseNum,
                        'Division':'ANY',
                        'CourseCodes':courseCodes,
                        'ClassType':'ALL',
                        'FullCourses':'ANY',
                        'FontSize':'100',
                        'CancelledCourses':'Exclude'}
        self.headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
        self.coursesDict = defaultdict(list)
        self.section_type = section_type

    def get_coursesDict(self):
        """ 
        return coursesDict member var

        rtype: dict
        """
        return self.coursesDict
    
    def get_name(self):
        """
        *** WINTER BREAK REFACTOR
        """
        return self.dept+self.courseNum
    
    def get_section_type(self):
        return self.section_type
    
    def reset(self):
        """
        initializes coursesDict back to empty dict
        """
        self.coursesDict.clear()
        
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
                html_page = requests.post(url,data=params,headers=self.headers).text
                # html_page.raise_for_status() # for some reason method doesn't work?
                connected = True
                return BeautifulSoup(html_page,'html.parser')
            # except requests.exceptions.HTTPError as httpError:
            #     print("HTTP Error:",httpError)
            #     time.sleep(2)
            except requests.exceptions.ConnectTimeout:
                print("Took too long to connect to the server. Retrying...")
                time.sleep(2)
            except requests.exceptions.ReadTimeout:
                print("Server took too long to send data. Retrying...")
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
    
    def parse_soup_new(self,soup):
        """
        *** WINTER BREAK REFACTOR
        """
        rows = soup.find_all("tr",valign="top")
        for row in rows:
            data = [] # seems that there's no other way to do this
            for children in row.children: # can do same with rows[0] (w/o .children)
                data.append(children.string)

            if data[-1] == 'OPEN':
                self.coursesDict[data[1]].append(data[0])
            else:
                pass
        
        return self.coursesDict
    
    def is_open(self):
        """
        *** WINTER BREAK REFACTOR
        """
        if self.section_type:
            return 'Lec' in self.coursesDict and self.section_type in self.coursesDict
        return 'Lec' in self.coursesDict

    def email_notif(self,receiver):
        """
        sends email to a receiving email from the email in the config.py file

        type receiver: string
        """
        # message = 'Subject: {}\n\n{}'.format('email test',body)
        subject = "Subject: {subject}\n\n".format(subject=self.dept+" "+self.courseNum+" has an opening!")
        body = self.dept+" "+self.courseNum+" has just been updated. Here are the changes:\n\n"
        body += json.dumps(self.coursesDict, indent=2)
        email_notif(receiver,subject,body)

    def run_scrape(self):
        """
        driver method to return coursesDict after scraping and parsing
        """
        return self.parse_soup_new(self.soupify(self.BASE_URL,self.params))
    
    def run_check(self):
        """
        *** WINTER BREAK REFACTOR
        """
        self.run_scrape()
        return self.is_open()

if __name__  == '__main__':
    test = Checker('COMPSCI','122A','Dis')
    # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    # headers = {"User-Agent":user_agent}
    # r = requests.post(test.BASE_URL,data=test.params,headers=headers)
    # print(r.status_code)
    # print(r.text)
    print(test.run_scrape())
    print(test.is_open())
    # print(test.build_secCode(test.get_coursesDict()))