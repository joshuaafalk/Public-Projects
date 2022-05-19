from imaplib import IMAP4_SSL
import email
import datetime

def fetch_new_email():
    date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y") #get mail from last day
    mail = IMAP4_SSL('imap.gmail.com')                  #connecting to mail service
    mail.login('USERNAME', 'PASSWORD')  #logging in and setting up email access
    mail.select("inbox")                                #selecting inbox

    result, data = mail.uid('search', None, '(SENTSINCE {date}) HEADER Subject "P.Budget"'.format(date=date)) #searching for emails with set subject
    ids = data[0]
    id_list = ids.split()                               #creates list of uids for all emails matching search criteria
    return id_list, mail

    
def get_new_emails():    
    mail_list, mail = fetch_new_email()
    message_list = []

    i = 0
    while i < len(message_list):
        latest_email_id = mail_list[i]                       #uid of most recent email with correct subject
        result, data = mail.uid('fetch', latest_email_id,'(RFC822)') #fetching text of email using uid
        raw = data[0][1]                                    #raw message data
        body = ""                                           #body will hold string of decoded email body
        message = email.message_from_bytes(raw)             #new email object from raw data

        if message.is_multipart():                          #ensures attachments/html are not read incorrectly
            for section in message.walk():                  #parses each section in message
                ctype = section.get_content_type()          #gets content type of section
                cdispo = str(section.get('Content-Disposition')) #gets content arrangement
                if ctype == 'text/plain' and 'attachment' not in cdispo: #if the type of content is plain text and not an attachment it is decoded
                    body = section.get_payload(decode=True)              #decodes section that is plain text, this is the text body so breaks loop
                    break
        else: #if the message is not multipart it can simply decode the whole thing
            body = message.get_payload(decode=True)

        message_list.append(body.decode('utf-8').strip('\r\n'))  #add cleaned up message the message list
        i+=1
    
    return message_list

