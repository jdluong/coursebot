from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time # for testing

deptName = 'BME'
courseNum = '160' 
lectureCode = '13570'
disCodes = ['13571','13572']

username = 'jdluong'
pw = 'jawnlu2v33'

needToCheck = True

###############################################
###############################################
##### CHECK IF CLASS IS OPEN THRU WEBSOC ######
###############################################
###############################################

###############################
##### OPENING THE BROWSER #####
###############################

driver = webdriver.Chrome() # open chrome window

driver.get("https://www.reg.uci.edu/perl/WebSoc") # go to WebSOC site

# finds course number box and enter desired course number
courseNum_box = driver.find_element_by_name('CourseNum')
courseNum_box.click()
courseNum_box.send_keys(courseNum)

# finds department dropdown element, select desired dept, and press enter
dept_dropdown = driver.find_element_by_name('Dept')
dept_dropdown.send_keys(deptName) 
dept_dropdown.send_keys('\ue007') 

#######################
##### THE SCRAPE ######
#######################

OPEN = False # keep refreshing and scraping until it's open


while not OPEN:

	if needToCheck:
		html_page = driver.page_source # get html of the webpage
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
		if lectureCode in coursesDict['Lec']:
			if coursesDict['Lec'][lectureCode] == 'OPEN':
				OPEN = True

	else:
		OPEN = True


	###################################
	###################################
	###### SIGNING UP IN WEBREG #######
	###################################
	###################################

	# IF LEC IS OPEN, start signing up process
	if OPEN:

		#######################
		##### SIGNING IN ######
		#######################

		driver.get("https://www.reg.uci.edu/registrar/soc/webreg.html") # go to webreg site

		# gets the access webreg element, and clicks it
		access_webreg = driver.find_element_by_xpath("//a[@href='https://www.reg.uci.edu/cgi-bin/webreg-redirect.sh']")
		access_webreg.click()

		# enter ucinetid and pw 
		ucinetid = driver.find_element_by_name("ucinetid")
		ucinetid.send_keys(username)
		password = driver.find_element_by_name("password")
		password.send_keys(pw)
		password.send_keys('\ue007')

		#######################
		##### ADD LECTURE #####
		#######################

		# finds enrollment menu button and clicks it
		enrollment_menu = driver.find_element_by_xpath("//input[@class='WebRegButton'][@value='Enrollment Menu']")
		enrollment_menu.click()

		# finds "add" radio button and clicks it
		add_radio = driver.find_element_by_xpath("//input[@type='radio'][@id='add']")
		add_radio.click()

		# finds the input box for the code, input the lecture code, and submits it
		courseCode_input = driver.find_element_by_name("courseCode")
		courseCode_input.send_keys(lectureCode)

		# find the send request button and press it
		sendRequest_button = driver.find_element_by_xpath("//input[@type='submit'][@value='Send Request']")
		sendRequest_button.click()

		# should check if signing up for lecture is successful; if not, repeat

		####################
		##### ADD DIS ###### this is obnoxious because look below
		####################

		for disCode in disCodes: # for each discussion code, in order of priority as inputted...
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
						if addedCheck[0].string.strip() == "you have added": # if successfully added...
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
					checkSoup = BeautifulSoup(driver.page_source,'html.parser')
					addedCheck = checkSoup.find_all("h2")
					if addedCheck[0].string.strip() == "you have added": # if successfully added...
						break # stop trying to add future discussions
				else: # else, go to next discussion code 
					pass
		# should add if a discussion was signed up for; if not keep trying

	else: # IF CLASS ISN'T OPEN YET, wait 2 sec, refresh, check again
		print("not open yet! trying again in 2 seconds..")
		time.sleep(2)
		driver.refresh()

#### CHECK MULTIPLE LECTURES/CLASSES
#### MAKE IT RELOG EVERY MINUTE IF IT'S NOT IN ENROLLMENT MENU

# driver.quit()