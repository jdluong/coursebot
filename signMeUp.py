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


def checkStatus(deptName,courseNum,prioLec,waitTimeScrape):
	"""
	Creates scraper class to scrape for course statuses and sends email notif if it's open

	type deptName, courseNum, prioLec: string
	
	need deptName and courseNum
	need prioLec to stop scrape
	need waitTimeScrape to specify how long to wait per scrape

	could make it checkStatus(scraperObj,waitTimeScrape) instead
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
			print(deptName, courseNum, "is not open yet! trying again in", waitTimeScrape, "seconds...")
			time.sleep(waitTimeScrape)
			print("--")
		print("------------------------------------------------------------------")
	
	return coursesDict

def enrollment(lectureCodes,disCodes,classNames):
	pass

if __name__ == "__main__":
	needToCheck = False
	
	lectureCodes = ['13570']
	# lectureCodes = ['35500','35800','36780']
	# 160 --- 13570: open
	# 180A --- 13580: full
	# 60B --- 13515: open

	disCodes = [['13573','13574','13572','13571']]
	# disCodes = [['35508','35507',''],['35803','35802','35801'],['36782','36781']]
	# 160 --- 13573: full; 13571: open; 13572: open
	# 180A --- 13582: full; 13583: open
	# 60B --- 13519: full; 13518: open
	
	classNames = ['BME 160']
	#classNames = ['BME 160','BME 180A','BME 60B']

	loginTimer = 10

	# ask for login info and confirm it's valid
	session = SignUpper(lectureCodes,disCodes,classNames,loginTimer,headless=False)
	valid_credentials = False
	print("------------------------------------------------------------------")
	while not valid_credentials:
		valid_credentials = session.credentials_setup(isHeadless=False)

	if needToCheck:
		# deptName, courseNum = "I&C SCI", "33"
		deptName, courseNum = "BME", "160"
		prioLec = "13570"
		waitTimeScrape = 10 # in seconds
		# NEED TO REDUCE AMOUNT OF PARAMETERS for checkStatus
		# Could initialize Scraper obj here, and have checkStatus parameters
		# be checkStatus(scraper:Scraper, waitTimeScrape:int), but don't know
		# yet how we're going to do the multiple checkStatuses
		#
		# SO FOR NOW, we'll have 4 parameters...
		print("Checking status for {dept} {num}...".format(dept=deptName,num=courseNum))
		coursesDict = checkStatus(deptName,courseNum,prioLec,waitTimeScrape)
	else: 
		coursesDict = None

	session.login()
	print("Beginning enrollment process...")
	session.enroll(coursesDict)
	session.email_notif_signupper("luongjohnd@gmail.com")

