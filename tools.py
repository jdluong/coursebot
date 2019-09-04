from selenium import webdriver

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