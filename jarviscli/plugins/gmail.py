from plugin import plugin 					# import plugin
import smtplib                                      		# import stmplib


@plugin()						    	# decorator
def gmail(jarvis, s):
    '''
    Sending email from a gmail account using SMTP services.
    To use this plugin :
                1. User should have a gmail id.
                2. Less secure apps should be allowed to access the gmail account.
    '''
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)   		 # establshing server connection
        server.ehlo()
        server.starttls()
        print("SERVER CONNECTED")
    except:
        print("Could Not connect to Gmail")            		 # in case of failure
        exit()
    user = input("Enter User id\n")                     	 # YOUR ID
    Pass_w = input("\nEnter your Password\n")           	 # YOUR Password
    reciever_id = input("\nEnter reciever id\n")        	 # Reciever ID
    msg = input("\nEnter message\n")                    	 # message

    try:
        server.login(user, Pass_w)                      	 # user log in
        print("User Logged in")
    except:
        print('''Allow Less secure apps in GOOGLE ACCOUNT SETTINGS to use SMTP services by following the given steps:
                                                                      \n\t\tStep 1. Log in to email using your browser.
                                                                      \n\t\tStep 2. Go to account settings.
                                                                      \n\t\tStep 3. Find 'allow less secure apps' and mark it as ON.''')
        server.quit()
        exit()
    server.sendmail(user, reciever_id, msg)
    print("MAIL sent")                                  	 # confirmation
    print("Closing Connection")
    server.quit()                                       	 # closing server connection
    print("Server closed")
