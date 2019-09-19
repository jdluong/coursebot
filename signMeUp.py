from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from scraper import Scraper
from signupper import SignUpper
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

		
def checkStatus(deptName,courseNum,prioLec,waitTimeScrape):
	"""
	Creates scraper class to scrape for course statuses and sends email notif if it's open

	type deptName, courseNum, prioLec: string
	
	NEED TO REDUCE NUMBER OF PARAMETERS
	need deptName and courseNum
	need prioLec to stop scrape
	need waitTimeScrape to specify how long to wait per scrape

	could make it checkStatus(scraperObj,prioLec,waitTimeScrape) instead
	"""
	scraper = Scraper(deptName,courseNum)
	OPEN = False 
	while not OPEN:
		coursesDict = scraper.run_scrape()
		if coursesDict['Lec'][prioLec] == 'OPEN':
			print(deptName,courseNum,"is open! Sending email notification...")
			OPEN = True
			scraper.email_notif_scrape("luongjohnd@gmail.com")
		else: # if it's not open yet, wait waitTimeScrape sec, refresh, check again
			# print(deptName, courseNum, "is not open yet! trying again in", waitTimeScrape, "seconds...")
			time.sleep(waitTimeScrape)
			# print("--")
		# print("------------------------------------------------------------------")
	
	return coursesDict

def enrollment(SignUpperObj,coursesDict,receiver):
	SignUpperObj.login()
	print("Beginning enrollment process...")
	return SignUpperObj.enroll(coursesDict)

# def driver()

if __name__ == "__main__":
	needToCheck = True # scrape or not
	someoneElse = False
	if someoneElse:
		classNames, lectureCodes, disCodes = getCourses()
	else:
		classNames = ['I&CS 33']
		lectureCodes = ['35500']
		disCodes = [['35508','35505','35507','35503','35501','35502','35504''35506']]
	loginTimer = 10
	timesToTry = 15

	# init obj
	session = SignUpper(lectureCodes,disCodes,classNames,loginTimer,headless=False,timesToTry=timestoTry)
	# ask for login info and confirm it's valid
	valid_credentials = False
	print("------------------------------------------------------------------")
	while not valid_credentials:
		valid_credentials = session.credentials_setup(isHeadless=False)
	# scrape, if configured
	if needToCheck:
		deptName, courseNum = "I&C SCI", "33"
		prioLec = "35500"
		waitTimeScrape = 10 # in seconds
		print("Checking status for {dept} {num}...".format(dept=deptName,num=courseNum))
		enrolled =  False
		while not enrolled:
			coursesDict = checkStatus(deptName,courseNum,prioLec,waitTimeScrape)
			enrolled = enrollment(session,coursesDict,needToCheck)
			session.email_notif_signupper("luongjohnd@gmail.com")
	else: 
		coursesDict = None
	# start enrollment process
	enrollment(session,coursesDict,"luongjohnd@gmail.com")