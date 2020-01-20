from time import sleep, localtime, strftime
from random import random

def print_progress(tries):
	if tries%100==0: 
		currTime = localtime()
		currTime_str = strftime("%H:%M",currTime)
		print("Still working.. [{currTime}]".format(currTime=currTime_str))	

def check_status(checker, interval=5):
	OPEN, tries = False, 0
	while not OPEN:
		tries += 1
		checker.reset()
		OPEN = checker.run_check()
		if OPEN:
			print(f"{checker.get_name()} is open! Sending email notification...")
			checker.email_notif("luongjohnd@gmail.com")
			return checker.get_coursesDict()
		# print(checker.get_coursesDict())
		print_progress(tries)
		sleep(interval*(random()+0.5))

def run_check(checker):
	print("Checking status for {name}... [{currTime}]".format(name=checker.get_name(),currTime=strftime("%H:%M",localtime())))
	return check_status(checker)