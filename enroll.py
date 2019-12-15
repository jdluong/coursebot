def enrollment(enroller):
    print("Logging into WebReg...")
    enroller.login()
    print("Beginning enrollment process...")
    return enroller.enroll() # TAKE OUT THE needToCheck PARAM


def run_enrollment(enroller,sections=[]):
    if sections:
        enroller.set_sectionCodes([sections])
    return enrollment(enroller)
    
