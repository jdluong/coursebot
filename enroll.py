def enrollment(enroller):
    print("Logging into WebReg...")
    enroller.login()
    print("Beginning enrollment process...")
    return enroller.enroll()

def run_enrollment(enroller,*courses):
    if courses:
        enroller.add_courses(courses)
    return enrollment(enroller)
    
