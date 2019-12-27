def config(enroller):
    valid = False
    print("------------------------------------------------------------------")
    while not valid:
        valid = enroller.credentials_setup(isHeadless=True)
        if not valid: 
            print("Please re-enter your credentials:")

def run_login_config(enroller):
    config(enroller)
