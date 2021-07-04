# import the required libraries
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
import email
from bs4 import BeautifulSoup
import datetime
import log
import string
import random

import storage

from sql import commit
from sql import fetch
  
from html.parser import HTMLParser
parser = HTMLParser()
  
# Define the SCOPES. If modifying it, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

lookaroundLenTight = 700
lookaroundLenLoose = 1300

linkPositives = ['unsubscribe', 'remove', 'stop receiv', 'opt-out', 'opt out','not to receiv', 'not receiv', 'manage subscript', 'manage my subscript', 'manage your subscript', 'don\'t want to receive update', 'don\'t want to receive email', 'no longer wish to receive']

def newHash():
  lets = string.ascii_letters[:26] + string.digits
  ans = ''
  for i in range(8):
    ans += random.choice(lets)
  return ans


def getAddress(msg):
  fromAddressFull = str(msg['from'])
  start = fromAddressFull.find('<') + 1
  end = fromAddressFull.find('>')
  if end == -1:
    return fromAddressFull
  return fromAddressFull[start:end]
  
def getHttpIndex(lower, keywordIndex, lookaroundLen):
  end = keywordIndex
  start = max(keywordIndex-lookaroundLen,0)
  kindexs = lower.rfind('https:', start, end)
  kindex = lower.rfind('http:', start, end)
  urlindex = kindexs
  if kindexs == -1 and kindex == -1:
    start = keywordIndex
    end = min(keywordIndex + lookaroundLen, len(lower))
    kindexs = lower.find('https:', start, end)
    kindex = lower.find('http:', start, end)
    urlindex = kindexs
    if kindexs == -1 and kindex == -1:
      return None, -1
  if kindexs > 0 and kindex > 0:
    urlindex = min(kindex, kindexs)
  if kindexs == -1:
    urlindex = kindex
  return urlindex, end
  
def getCandidateNearby(lower, body, keyword, start):
  index = lower.find(keyword,start)
  #print(body)
  #quit()
  if index == -1:
    return None, start
  urlindex, end = getHttpIndex(lower, index,lookaroundLenTight)
  if urlindex == None:
    urlindex, end = getHttpIndex(lower, index,lookaroundLenLoose)
    if urlindex == None:
      return None, start
  urlendindex = lower.find('"', urlindex+2, end)
  if urlendindex == -1:
    return None, start
  url = body[urlindex:urlendindex]
  return url, end

def getCandidates(body):
  try:
    #body = parser.unescape(body)
    #print(body)
    lower =  body.lower()
    length = len(lower)
  
    candidates = set()
    lower = lower.replace('unsubscribe.robot','a'*17).replace('unsubscriberobot','a'*16)
    
    for lp in linkPositives:
      start = 6
      while start > 5:
        c, start = getCandidateNearby(lower, body, lp, start)
        if c:
          candidates.add(c)
        start = lower.find(lp, start+1)
    return candidates
  except Exception as e:
    print(3333335)
    print(e)
    log.warn(e)
  return set()
  
def getSender(address):
  if '<' in address:
    index = address.find('<')
    endindex = address.find('>')
    return address[index+1:endindex]
  return address


def getEmails():

    emails = fetch('select email from readmailhash')
    read = set()
    for e in emails:
      read.add(e[0])
    processed = set()
    
    
    
    
    # Variable creds will store the user access token.
    # If no valid token found, we will create one.
    creds = None
  
    # The file token.pickle contains the user access token.
    # Check if it exists
    print(123)
    storage.downloadFile('/auth/token.pickle','unsubscribe/token.pickle')
    if os.path.exists('/auth/token.pickle'):
  
        # Read the token from the file and store it in the variable creds
        with open('/auth/token.pickle', 'rb') as token:
            if token:
                try:
                    creds = pickle.load(token)
                except:
                    print(creds, token)
    print(456)
    # If credentials are not available or are invalid, ask the user to log in.
    if not creds or not creds.valid:
        print( Exception('creds not valiid', creds))
        if creds and creds.expired and creds.refresh_token:
            print('herre')
            print(creds, creds.valid, creds.expired, creds.refresh_token)
            creds.refresh(Request())
            print(creds)
        else:
            flow = InstalledAppFlow.from_client_secrets_file('/auth/unsub_gmail_client_secret_393871751062-l904jal1eamg0l9mhrvekl4f9dj1r3r8.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
            raise  Exception('creds not valiid', creds, creds.valid, creds.expired, creds.refresh_token)
  
        # Save the access token in token.pickle file for the next run
        with open('/auth/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        storage.uploadFile('/auth/token.pickle','unsubscribe/token.pickle')
  
    # Connect to the Gmail API
    service = build('gmail', 'v1', credentials=creds)
    
    now = datetime.datetime.now() - datetime.timedelta(days=4)
    year, month, day = str(now.year), str(now.month), str(now.day)
    # request a list of all the messages
    result = service.users().messages().list(userId='me', q='after:'+year+'/'+month+'/'+day,maxResults=500).execute()
  
    # We can also pass maxResults to get any number of emails. Like this:
    # result = service.users().messages().list(maxResults=200, userId='me').execute()
    messages = result.get('messages')
  
    # messages is a list of dictionaries where each dictionary contains a message id.
    print('11', len(messages))
    # iterate through all the messages
    ii =0
    for msg in messages:
        hashh = newHash()
        if msg['id'] in read:
          continue
        print(msg['id'])
        print(5621)
        processed.add(msg['id'])
        # Get the message from its id
        print('22')
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        # Use try-except to avoid any Errors
        try:
            # Get value of 'payload' from dictionary 'txt'
            #print(txt)
            payload = txt['payload']
            headers = payload['headers']
  
            # Look for Subject and Sender Email in the headers
            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']
            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            if payload.get('parts'):
              parts = payload.get('parts')[0]
            else:
              parts = payload
            print('44')
            data = parts['body']['data']
            print(55)
            #print(data)
            if not data:
              print('no data!, 6666')
              continue
            data = data.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(data)
  
            # Now, the data obtained is in lxml. So, we will parse 
            # it with BeautifulSoup library
            soup = BeautifulSoup(decoded_data , "lxml")
            body = soup.body()
  
            # Printing the subject, sender's email and message
            print("Subject: ", subject)
            print("From: ", sender)
            #print("Message: ", body)
            print('\n')
            print(455)
            fromemail = getSender(sender)
            body = str(list(body))
            candidates = getCandidates(body)

            numcand = 0
            print(1456)
            for c in candidates:
              if numcand > 5:
                break
              numcand += 1 
              log.info('candidate', fromemail, c)
              print(hashh, c, fromemail)
              commit('insert into unsubs (hash, url, email) values (%s, %s, %s)', (hashh, c, fromemail))
        except Exception as e:
            print(556)
            print(e)
            pass
  
    log.info('write read in db')
    print(processed)
    for pro in processed:
      print('pro',pro)
      commit('insert into readmailhash (email) values (%s)', pro)
      
getEmails()
