# GMAIL ONLY
# ----------

# A few notes: This uses less-secured apps by default for GMail, so I would
# not recommend using this script from an email account you care about.
#
# To enable less-secured apps with GMail, go to the following link:
#   https://myaccount.google.com/lesssecureapps?utm_source=google-account&utm_medium=web
# Please note that it may take a few minutes for these changes to register.
#
# If you would like to use this script with GMail on a secured account,
# please use the GMail API.
#   To install the GMail API, run:
#       pip install --upgrade google-api-python-client
#   Next, substitute the logic below with code adapted from here:
#       https://medium.com/lyfepedia/sending-emails-with-gmail-api-and-python-49474e32c81f
# To use the GMail API you will have to create a workspace admin account for yourself,
# which costs a little something every year.

import smtplib  # import stmplib
from email.message import EmailMessage

from plugin import Platform, alias, plugin, require  # import plugin

EMAIL_HOST = 'smtp.gmail.com'  # 'smtp.gmail.com' for gmail
EMAIL_PORT = 587  # 587 for gmail

# Add more providers if yours isn't here.
PROVIDERS = {
    'att': '@txt.att.net',
    'boost': '@smsmyboostmobile.com',
    'cricket': '@sms.cricketwireless.net',
    'sprint': '@messaging.sprintpcs.com',
    'tmobile': '@tmomail.net',
    'uscellular': '@email.uscc.net',
    'verizon': '@vtext.com',
    'virgin': '@vmobl.com',
}

GMAIL = "gmail"


def format_email(send_to, send_from, subject, body):
    """Format the email body."""

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = send_from
    msg['To'] = send_to

    return msg


def send_message(final_message, email_user, email_pass):
    """Send email to recipient."""

    try:
        smtp = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        smtp.starttls()
    except BaseException:
        print("Could Not connect to Gmail")
        return

    try:
        smtp.login(email_user, email_pass)
        smtp.send_message(final_message)
        print("Sent!")  # confirmation
    except Exception:
        print("Unable to send text right now, please try again later.")
    finally:
        smtp.close()


def send_mail(send_to, send_from, final_message, email_user, email_pass):
    """Send email to recipient."""

    try:
        smtp = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        smtp.starttls()
    except BaseException:
        print("Could Not connect to Gmail")
        return

    try:
        smtp.login(email_user, email_pass)
        smtp.sendmail(send_from, send_to, final_message)
        print("Sent!")  # confirmation
    except Exception as e:
        print("Unable to send text right now, please try again later.")
    finally:
        smtp.close()


@plugin('gmail')  # decorator
def gmail(jarvis, s):
    """
    Sending email from a gmail account using SMTP services.
    To use this plugin :
                1. User should have a gmail id.
                2. Less secure apps should be allowed to access the gmail account.
    """
    jarvis.say("Jarvis uses less-secured apps by default for GMail, \nso I would not "
               "recommend using this script from an \nemail account you care about.\t\t")
    user, pass_word = jarvis.internal_execute("user pass", GMAIL)
    receiver_id = jarvis.input("\nEnter receiver id\n")  # Reciever ID
    msg = jarvis.input("\nEnter message\n")  # message
    send_mail(receiver_id, user, msg, user, pass_word)


@require(network=True, platform=[Platform.MACOS, Platform.LINUX])
@alias("message")
@plugin("text")
def text(jarvis, s):
    """
    Sending texts from a gmail account using SMTP services.
    To use this plugin :
                1. User should have a gmail id.
                2. Less secure apps should be allowed to access the gmail account.
    """
    provider = None
    phone_number = None
    display_name = None

    jarvis.say("Jarvis uses less-secured apps by default for GMail, \nso I would not "
               "recommend using this script from an \nemail account you care about.\t\t")
    your_email, email_pass = jarvis.internal_execute("user pass", GMAIL)

    if s == "":
        phone_number = jarvis.input("Enter Phone Number: ")
        provider = jarvis.input("Enter Provider \n(Available: " + str(PROVIDERS.keys()) + "): ")
        # display_name = jarvis.input("Any preferences on display name? \n"
        #                                  "Enter (if null, your email shows as display name):")

    enter_subject = jarvis.input("Enter Subject: ")
    enter_text = jarvis.input("Enter Text (Enter is send): ")
    if phone_number[:2] == "+1":
        send_to = f'{phone_number}{PROVIDERS[provider]}'
    else:
        send_to = f'+1{phone_number}{PROVIDERS[provider]}'
    send_from = your_email

    final_message = format_email(send_to, send_from, enter_subject, enter_text)
    send_message(final_message, your_email, email_pass)
