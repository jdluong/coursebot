from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from scraper import Scraper

import requests 
import smtplib
import config

from selenium.common.exceptions import NoSuchElementException # for retry login
import re # regex
import time # for testing

###				  ###
### START PROGRAM ###
###				  ###

###############################################
###############################################
##### CHECK IF CLASS IS OPEN THRU WEBSOC ######
###############################################
###############################################

#########################################################
##### if need to constantly check if class is open ######
#########################################################

deptName = 'I&C SCI'
courseNum = '33'

lectureCodeScrape = '35500'

url = 'https://www.reg.uci.edu/perl/WebSoc'
params = {'Submit':'Display Web',
			'YearTerm':'2019-92',
			'ShowComments':'on',
			'ShowFinals':'on',
			'Breadth':'ANY',
			'Dept':deptName,
			'CourseNum':courseNum,
			'Division':'ANY',
			'ClassType':'ALL',
			'FullCourses':'ANY',
			'FontSize':'100',
			'CancelledCourses':'Exclude'}

needToCheck = True

if needToCheck:

	#######################
	##### THE SCRAPE ######
	#######################

	OPEN = False # keep refreshing and scraping until it's open

	while not OPEN:

		html_page = requests.post(url,data=params).text
	
		soup = BeautifulSoup(html_page,'html.parser') # parse html into stuff bs4 can read

		rows = soup.find_all("tr", valign="top")[1::] # gets the rows containing data
		coursesDict = {} # will populate with lec, dis, and/or lab codes
		tempDict = {} 
		for row in rows:
			tempArray = [] # contains data per course; reinitialized each row
			for children in row.children: # can do same with rows[0] (w/o .children)
				tempArray.append(children.string) # make a list of each column's string, per element
				# should we do things AFTER the list is made, or AS the list is made?

			# SHOULD WE ONLY ADD COURSES THAT ARE OPEN????
			if tempArray[1] not in coursesDict: # for course types that aren't in the dict yet, add it
				tempDict[tempArray[0]] = tempArray[-1]
				coursesDict[tempArray[1]] = tempDict
				tempDict = {}
			else: 
				coursesDict[tempArray[1]][tempArray[0]] = tempArray[-1]

		# after getting statuses of all courses, check if lecture is open
		if coursesDict['Lec'][lectureCodeScrape] == 'OPEN':
			OPEN = True
			try:
				server = smtplib.SMTP('smtp.gmail.com:587')
				server.ehlo()
				server.starttls()
				server.login(config.EMAIL_ADDRESS,config.PASSWORD)
				message = 'Subject: {}\n\n{}'.format('email test',str(coursesDict))
				server.sendmail(config.EMAIL_ADDRESS,config.EMAIL_ADDRESS,message)
				server.quit()
				print("Email sent")
			except:
				print("Email failed to send")

		else: # if it's not open yet, wait 2 sec, refresh, check again
			print("not open yet! trying again in 2 seconds..")
			time.sleep(2)

time.sleep(60)

###################################
###################################
###### SIGNING UP IN WEBREG #######
###################################
###################################

#######################
##### SIGNING IN ######
#######################

lectureCodes = ['13570','13515']
# 160 --- 13570: open
# 60B --- 13515: open
# 180A --- 13580: full
disCodes = [['13573','13572'],['13518','13516']]
# 160 --- 13573: full; 13571: open; 13572: open
# 60B --- 13518: time conflict; 13516: open
# 180A --- 13582: full; 13583: open
classNames = ['BME 160','BME 60B']

username = 'jdluong'
pw = 'jawnlu2v33'

driver = webdriver.Chrome() # open chrome window

driver.get("https://www.reg.uci.edu/registrar/soc/webreg.html") # go to webreg site

# gets the access webreg element, and clicks it
access_webreg = driver.find_element_by_xpath("//a[@href='https://www.reg.uci.edu/cgi-bin/webreg-redirect.sh']")
access_webreg.click()


#######################
#### RETRY LOG IN #####
#######################

loggedIn = False
while not loggedIn:
	# i wanna use a try-except block because the other way would be to read in the entire
	# web page each time to check for the existence of the enrollment_menu window w/ BS, 
	# but i feel like that'd take more time to do than just to keep trying to check for it
	# w/ selenium, which throws an error, and then the error is handled. but it seems like
	# that sounds like bad practice/an anti-pattern
	try:
		# enter ucinetid and pw 
		ucinetid = driver.find_element_by_name("ucinetid")
		ucinetid.send_keys(username)
		password = driver.find_element_by_name("password")
		password.send_keys(pw)
		password.send_keys('\ue007')

		# # for testing
		# logout_button = driver.find_element_by_xpath("//input[@value='Logout'][@type='submit']")
		# logout_button.click()
		# # for testing

		# if enrollment_menu can't be found, then that means login wasn't successful
		# exception is then handled in the except block
		enrollment_menu = driver.find_element_by_xpath("//input[@class='WebRegButton'][@value='Enrollment Menu']")
		enrollment_menu.click()
		loggedIn = True
		print('\nSuccessfully logged in')
	# if login was unsuccessful...
	except NoSuchElementException as exception:
		print("Can't log in. Retrying in one minute...")
		time.sleep(60)
		access_webreg = driver.find_element_by_xpath("//input[@type='submit'][@name='button'][@value='Access WebReg']")
		access_webreg.click()

# ONCE SUCCESSFULLY LOGGED IN...

########################
### MULTIPLE CLASSES ###
########################

# some data structures to indicate that lec and dis are successfull
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

			if len(checkLecSoup.find_all(string=re.compile("You must successfully enroll in all co-classes"))) == 1: # if added before dis
				print("[x] LEC SUCCESS; signed up before discussion")
				lecEnrolled[lectureInd] = True
			elif len(checkLecSoup.find_all(string=re.compile("you have added"))) == 1: # if added after dis
				print("[x] LEC SUCCESS; signed up after discussion")
				lecEnrolled[lectureInd] = True
			elif len(checkLecSoup.find_all(string=re.compile("This course is full"))) == 1: # if unsuccessful
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

###			    ###
### END PROGRAM ###
###		    	###