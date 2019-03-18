try:
    import urllib2
except: 
    from urllib.request import urlopen, Request
    import urllib
import requests
import re
import json
from datetime import datetime

from ps_audit_logger import PSAuditLogger

BASE_DIR = '/opt/tools'
FIND_EVENTS_SCRIPT_TYPE = 'notifications'

try:
    logger = PSAuditLogger(script_type=FIND_EVENTS_SCRIPT_TYPE, filename=os.path.join(BASE_DIR, f'logs/{FIND_EVENTS_SCRIPT_TYPE}_1'))
except: logger = PSAuditLogger(script_type=FIND_EVENTS_SCRIPT_TYPE, filename=os.path.join(BASE_DIR, 'logs/{0}_1'.format(FIND_EVENTS_SCRIPT_TYPE)))

def sendDirect(postbody):
    passwd = 'T3mpPasswd!'
    sess = requests.Session()
    #### Authenticate ####
    try: 
        authbody = f'''{{
    "UserIdOrEmail": "notifications@direct.org",
    "Password": "{passwd}"
    }}'''
    except: authbody = """{
        "UserIdOrEmail": "notifications@direct.org",
        "Password": "%s"
    }""" % passwd
    resp = sess.post("https://ssl.dmhisp.com/SecureMessagingApi/Account/Logon", data=authbody, headers={"Content-Type":"application/json"}, verify=False)
    rsjson = json.loads(resp.content)
    sessKey = rsjson['SessionKey']
    resp = sess.post("https://ssl.dmhisp.com/SecureMessagingApi/Message/", data=postbody, headers={"Content-Type":"application/json","X-Session-Key":sessKey}, verify=False)
    rsjson = json.loads(resp.content)
    msgId = rsjson['MessageId']
    return resp.content

addresses = json.dumps({"Facility1":["address1@facility1.net","address2@facility1.net"]})
mpid = 123

try:
    qstr = f'''qstr = 'q=()s.mpid:({mpid})&store=1101&fields=patient.fmrn.active,patient.name.family,patient.name.given,patient.birthdate,patient.gender,patient.ssn,patient.address.line,patient.address.city,patient.address.state,patient_zip,patient.ethnicity,patient.race,patient.communication.language,patient.phone,patient.email' '''
except: qstr = 'q=()s.mpid:("%s")&store=1101&fields=patient.fmrn.active,patient.name.family,patient.name.given,patient.birthdate,patient.gender,patient.ssn,patient.address.line,patient.address.city,patient.address.state,patient_zip,patient.ethnicity,patient.race,patient.communication.language,patient.phone,patient.email' % (mpid)

try:
    qstr_bytes = str.encode(qstr)
    type(qstr_bytes)
    personaRecord = urlopen(urllib.request.Request('http://127.0.0.1:30000/query', qstr_bytes)).read()
except: personaRecord = urllib2.urlopen(urllib2.Request('http://127.0.0.1:30000/query', qstr)).read()

lName = re.findall(r"<patient.name.family>(.+?)</patient.name.family>",personaRecord)[0]
fAndMidName = re.findall(r"<patient.name.given>(.+?)</patient.name.given>",personaRecord)[0]
dob = re.findall(r"<patient.birthdate>(.+?)</patient.birthdate>",personaRecord)[0]

dob_yy = datetime.strptime(dob, '%Y-%m-%d').strftime('%m/%d/%y')

try:
    subject = f'Bronx RHIO Alert for MPID:{mpid}'
except: subject = "Bronx RHIO Alert for MPID:%s"%(mpid)
try:
    body = f'Patient Name: {fAndMidName} {lName}'
except: body = "Patient Name: %s %s"%(fAndMidName, lName)

try:
    body.append(f'Patient DOB: {dob_yy}')
except: body.append("Patient DOB: %s"%dob_yy)


postbody = """{
    "To":%s,
    "From":"notifications_test@bronxrhiodirect.org",
    "Subject":"%s",
    "CreateTime":"11:51 AM",
    "TextBody":"%s"
}"""%(addresses["Facility1"],subject,"\\n".join(body))

rsjson = json.loads(resp)
msgId = rsjson['MessageId']

logger.info("<Notification><Patient_MPID>%s</Patient_MPID><Patient_LastName>%s</Patient_LastName><Recipient>%s</Recipient><DirectMessageId>%s</DirectMessageId></Notification>"%(mpid, lName, ', '.join(addresses[alertToSendFac]), msgId))

