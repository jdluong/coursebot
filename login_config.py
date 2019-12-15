def config(enroller):
    valid = False
    print("------------------------------------------------------------------")
    while not valid:
        valid = enroller.credentials_setup(isHeadless=True)

def run_login_config(enroller):
    config(enroller)