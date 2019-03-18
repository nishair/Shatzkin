
from urllib.request import urlopen, Request
import requests
import re
import json
import os
import warnings

from ps_audit_logger import PSAuditLogger

BASE_DIR = '/opt/tools'
FIND_EVENTS_SCRIPT_TYPE = 'notifications'

try:
    # For Python 3.0 and later
    logger = PSAuditLogger(script_type=FIND_EVENTS_SCRIPT_TYPE, filename=os.path.join(BASE_DIR, f'logs/{FIND_EVENTS_SCRIPT_TYPE}_1'))
except:
    print("Python 2 error")

def sendDirect(postbody):
    passwd = 'T3mpPasswd!'
    sess = requests.Session()
    #### Authenticate ####
    try:
    	authbody = f'''{{
    "UserIdOrEmail": "notifications@direct.org",
    "Password": "{passwd}"
    }}'''
     except : authbody = '{
        "UserIdOrEmail": "notifications@direct.org",
        "Password": "{passwd}"
    }' % passwd
    resp = sess.post("https://ssl.dmhisp.com/SecureMessagingApi/Account/Logon", data=authbody, headers={"Content-Type":"application/json"}, verify=False)
    rsjson = json.loads(resp.content)
    sessKey = rsjson['SessionKey']
    resp = sess.post("https://ssl.dmhisp.com/SecureMessagingApi/Message/", data=postbody, headers={"Content-Type":"application/json","X-Session-Key":sessKey}, verify=False)
    rsjson = json.loads(resp.content)
    msgId = rsjson['MessageId']
    return resp.content

addresses = json.dumps({"Facility1":["address1@facility1.net","address2@facility1.net"]})
addresses_json = json.dumps(addresses)

mpid = 123

qstr = 'q=()s.mpid:("%s")&store=1101&fields=patient.fmrn.active,patient.name.family,patient.name.given,patient.birthdate,patient.gender,patient.ssn,patient.address.line,patient.address.city,patient.address.state,patient_zip,patient.ethnicity,patient.race,patient.communication.language,patient.phone,patient.email' % (mpid)

personaRecord = urllib2.urlopen(urllib2.Request('http://127.0.0.1:30000/query', qstr)).read()

qstr_bytes = str.encode(qstr)
type(qstr_bytes)

personaRecord = urlopen(urllib.request.Request('http://127.0.0.1:30000/query', qstr_bytes)).read()

import urllib.request
u = urllib.request.urlopen("xxxx")#The url you want to open

lName = re.findall(r"<patient.name.family>(.+?)</patient.name.family>",personaRecord)[0]
fAndMidName = re.findall(r"<patient.name.given>(.+?)</patient.name.given>",personaRecord)[0]
dob = re.findall(r"<patient.birthdate>(.+?)</patient.birthdate>",personaRecord)[0]
#Assuming dob is integer
from datetime import datetime
date = datetime.strptime(a, '%Y-%m-%d').strftime('%m/%d/%y')

subject = "Bronx RHIO Alert for MPID:%s"%(mpid)
body = "Patient Name: %s %s"%(fAndMidName, lName)
body.append("Patient DOB: %s"%dob)

postbody = """{
    "To":%s,
    "From":"notifications_test@bronxrhiodirect.org",
    "Subject":"%s",
    "CreateTime":"11:51 AM",
    "TextBody":"%s"
}"""%(addresses_json["Facility1"],subject,"\\n".join(body))

rsjson = json.loads(resp)
msgId = rsjson['MessageId']

logger.info("<Notification><Patient_MPID>%s</Patient_MPID><Patient_LastName>%s</Patient_LastName><Recipient>%s</Recipient><DirectMessageId>%s</DirectMessageId></Notification>"%(mpid, lName, ', '.join(addresses_json[alertToSendFac]), msgId))

