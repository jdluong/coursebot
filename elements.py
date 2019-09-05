#---------------|
# REGISTRAR SITE|
#---------------|

# access webreg button (by xpath) @ registrar site, for initial login
ACCESS_WEBREG_registrar = "//a[@href='https://www.reg.uci.edu/cgi-bin/webreg-redirect.sh']"


#--------------|
# WEBAUTH LOGIN|
#--------------|

# ucinetid field (by name) @ webauth login site
UCINETID = "ucinetid"
# password field (by name) @ webauth login site
PASSWORD = "password"

#--------|
# WEBREG |
#--------|

# access webreg button @ (by xpath) @ webreg, for relogin
ACCESS_WEBREG_webreg = "//input[@type='submit'][@name='button'][@value='Access WebReg']"
# enrollment menu (by xpath) @ webreg
ENROLLMENT_MENU = "//input[@class='WebRegButton'][@value='Enrollment Menu']"
# logout button (by xpath, in webreg)
LOGOUT_BUTTON = "//input[@value='Logout'][@type='submit']"
# LOGIN_BUTTON = 