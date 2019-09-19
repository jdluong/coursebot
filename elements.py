#---------------|
# REGISTRAR SITE|
#---------------|

# access webreg button (by xpath); for initial login
ACCESS_WEBREG_registrar = "//a[@href='https://www.reg.uci.edu/cgi-bin/webreg-redirect.sh']"
# "click here to log in" (by xpath); to test login
TEST_LOGIN = "//a[@href='https://login.uci.edu/ucinetid/webauth']"
# logout (by xpath); logout of test login in student access
TEST_LOGOUT = "//a[@href='../logout/']"

#--------------|
# WEBAUTH LOGIN|
#--------------|

# ucinetid field (by name)
UCINETID = "ucinetid"
# password field (by name)
PASSWORD = "password"

#--------|
# WEBREG |
#--------|

# access webreg button @ (by xpath); for relogin
ACCESS_WEBREG_webreg = "//input[@type='submit'][@name='button'][@value='Access WebReg']"
# enrollment menu (by xpath)
ENROLLMENT_MENU = "//input[@class='WebRegButton'][@value='Enrollment Menu']"
# study list (by xpath)
STUDY_LIST = "//input[@class='WebRegButton'][@value='Show Study List']"
# add radio button (by xpath)
ADD_RADIO = "//input[@type='radio'][@id='add']"
# input box for course code (by name)
INPUT_COURSECODE = "courseCode"
# send request button (by xpath)
SEND_REQUEST = "//input[@type='submit'][@value='Send Request']"
# logout button (by xpath, in webreg)
LOGOUT_BUTTON = "//input[@value='Logout'][@type='submit']"