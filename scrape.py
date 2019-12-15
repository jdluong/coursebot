from time import sleep, localtime, strftime
from random import random

def print_progress(tries):
	if tries%100==0: 
		currTime = localtime()
		currTime_str = strftime("%H:%M",currTime)
		print("Still working.. [{currTime}]".format(currTime=currTime_str))	

def check_status(scraper, interval=5):
	OPEN, tries = False, 0
	while not OPEN:
		tries += 1
		scraper.reset()
		if scraper.scrape_n_check():
			print(f"{scraper.get_className()} is open! Sending email notification...")
			scraper.email_notif("luongjohnd@gmail.com") # should change to variable later
			return scraper.get_coursesDict()
		# print(scraper.get_coursesDict())
		print_progress(tries)
		sleep(interval*(random()+0.5))

def run_scrape(scraper):
	print("Checking status for {name}... [{currTime}]".format(name=scraper.get_className(),currTime=strftime("%H:%M",localtime())))
	return check_status(scraper)