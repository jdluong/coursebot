from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from scraper import Scraper
from enroller import Enroller
from loginsetup import LoginSetup
import getpass

import requests 
import smtplib
import config

from selenium.common.exceptions import NoSuchElementException # for retry login
import re # regex
import time # for testing

def getCourses():
	print("------------------------------------------------------------------\nWelcome! Follow the prompts to enter your classes.")
	valid = False
	while not valid:
		try:
			numCourses = int(input("Number of courses to enroll in (e.g., one course = lecture w/ disc): "))
			valid = True
		except ValueError:
			print("Please enter a valid number")

	classNames = []
	lectureCodes = []
	disCodes = []
	courseDone = 'no'
	allDone = 'no'
	while allDone == 'no':
		for i in range(numCourses):
			while courseDone == 'no':
				name = (input("Enter the name of course {j} (e.g., I&CS 31): ".format(j=i+1))).strip()
				print('-')
				lec = (input("Enter the LECTURE code for {course}: ".format(course=name))).strip()
				print('-')
				dis = ((input("Enter the DISCUSSION codes, in decreasing priority, for {course}, separated by commas:\n")).strip()).split(',')
				for a in range(len(dis)):
					dis[a] = dis[a].strip()
				print('-')
				print("NAME: {course} | LEC: {lecCode} | DIS: ".format(course=name,lecCode=lec),end='')
				for k in dis:
					print(k,end=' ')
				courseDone = input('\nDoes this look right? If not, you will re-enter the info (yes/no): ')
			classNames.append(name)
			lectureCodes.append(lec)
			disCodes.append(dis)
			courseDone = 'no'
			print("---------")
		
		for x in range(len(lectureCodes)):
			print("\nNAME: {course} | LEC: {lecCode} | DIS: ".format(course=classNames[x],lecCode=lectureCodes[x]),end='')
			for k in disCodes[x]:
				print(k,end=' ')
		allDone = input('\n\nDoes this look right? If not, you will restart from the beginning (yes/no): ')
	
	return classNames,lectureCodes,disCodes

def print_progress(tries):
	if tries%100==0: 
		currTime = time.localtime()
		currTime_str = time.strftime("%H:%M",currTime)
		print("Still working.. [{currTime}]".format(currTime=currTime_str))		

def checkStatus(scraperObj,prioLec,waitTimeScrape,secPreference=False):
	"""
	Creates scraper class to scrape for course statuses and sends email notif if it's open
	
	need prioLec to stop scrape
	
	"""
	OPEN, tries = False, 0
	while not OPEN:
		tries += 1
		coursesDict = scraperObj.run_scrape() 
		if coursesDict['Lec'][prioLec] == 'OPEN':
			if secPreference:
				pass
			else:
				sectionCodes = scraperObj.build_secCode(coursesDict)
				if sectionCodes:
					print(deptName,courseNum,"is open! Sending email notification...")
					OPEN = True
					scraperObj.email_notif("luongjohnd@gmail.com")
					return [sectionCodes]
				else:
					print_progress(tries)
					time.sleep(waitTimeScrape)
		else: # if it's not open yet, wait waitTimeScrape sec, refresh, check again
			print_progress(tries)
			time.sleep(waitTimeScrape)

def checkStatus_new(scraper, interval=6):
	OPEN, tries = False, 0
	while not OPEN:
		tries += 1
		if scraper.scrape_n_check():
			scraper.email_notif("luongjohnd@gmail.com") # should change to variable later
			return scraper.get_coursesDict()
		print_progress(tries)
		time.sleep(interval)
	
def enrollment(SignUpperObj,needToCheck):
	SignUpperObj.login()
	print("Beginning enrollment process...")
	return SignUpperObj.enroll(needToCheck)

if __name__ == "__main__":
	needToCheck = True # scrape or not
	someoneElse = False
	classNames = ['ENGR190W(MW)']
	lectureCodes = ['13306']
	sectionCodes = [['13307']]

	if needToCheck: # CURRENTLY ONLY SUPPORTS ONE CLASS
		loginTimer = 0
		timesToTry = 15
		session = Enroller(lectureCodes,sectionCodes,classNames,loginTimer,headless=True,timesToTry=timesToTry)
		valid_credentials = False
		print("------------------------------------------------------------------")
		while not valid_credentials:
			valid_credentials = session.credentials_setup(isHeadless=True)

		deptName, courseNum = "ENGR", "190W"
		prioLec = "13306"
		section = "Dis"
		waitTimeScrape = 6 # in seconds
		currTime = time.localtime()
		currTime_str = time.strftime("%m/%d, %H:%M",currTime)
		print("Checking status for {dept} {num}... [{currTime}]".format(dept=deptName,num=courseNum,currTime=currTime_str))
		enrolled = False
		secPreference = False
		scraper = Scraper(deptName,courseNum,section) 
		while not enrolled:
			sectionCodes = checkStatus(scraper,prioLec,waitTimeScrape,secPreference)
			print(sectionCodes)
			session.set_sectionCodes(sectionCodes)
			enrolled = enrollment(session,needToCheck)
			if enrolled:
				session.email_notif_enroller("luongjohnd@gmail.com")
			scraper.reset()

	else:
		if someoneElse:
			classNames, lectureCodes, disCodes = getCourses()
		loginTimer = 10

		session = Enroller(lectureCodes,sectionCodes,classNames,loginTimer,headless=False)
		valid_credentials = False
		print("------------------------------------------------------------------")
		while not valid_credentials:
			valid_credentials = session.credentials_setup(isHeadless=False)
		
		enrollment(session,needToCheck)
		session.email_notif_enroller("luongjohnd@gmail.com")