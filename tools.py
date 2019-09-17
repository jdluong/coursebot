from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import smtplib
import time
import config

def find_n_click_xpath(driver,element_xpath):
    """
    finds element by xpath in driver and clicks it

    type driver: webdriver
    type element_xpath: string
    """
    element = driver.find_element_by_xpath(element_xpath)
    element.click()

def find_n_click_name(driver,element_name):
    """
    finds element by name in driver and clicks it

    type driver: webdriver
    type element_name: string
    """
    element = driver.find_element_by_name(element_name)
    element.click()

def find_n_sendkeys(driver,element_name,keys):
    """
    finds element by name in driver and sends keys to it

    type driver: webdriver
    type element_name: string
    type keys: string
    """
    element = driver.find_element_by_name(element_name)
    element.send_keys(keys)

def email_notif(receiver,subject,body):
    """
    emails to receiver the specified subject and body

    type receiver: string
    type subject: string
    type body: string
    """
    try:
        start = time.time()
        # setting up server
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        print("Server config finished at:",time.time()-start,"seconds")
        # login to throwaway email
        server.login(config.EMAIL_ADDRESS,config.PASSWORD)
        print("Login finished at:",time.time()-start,"seconds")
        # create and send email
        message = subject+body
        server.sendmail(config.EMAIL_ADDRESS,receiver,message)
        print("Email sent at at:",time.time()-start,"seconds")
        server.quit()
        print("Email sent!")
        print("Whole email process took",time.time()-start,"seconds")
    except smtplib.SMTPException as err:
        print("Email failed to send:",str(err),"\nContinuing anyway...")