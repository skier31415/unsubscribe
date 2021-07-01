#https://support.google.com/accounts/answer/185833
import imaplib
from sql import commit
from sql import fetch
import log
import time
import imaplib
import email
import datetime
from datetime import timedelta
import string
import random

lookaroundLenTight = 700
lookaroundLenLoose = 1300

linkPositives = ['unsubscribe', 'remove', 'stop receiv', 'opt-out', 'opt out','not to receiv', 'not receiv', 'manage subscript', 'manage my subscript', 'manage your subscript', 'don\'t want to receive update', 'don\'t want to receive email', 'no longer wish to receive']
  
from html.parser import HTMLParser
parser = HTMLParser()

def newHash():
  lets = string.ascii_letters[:26] + string.digits
  ans = ''
  for i in range(8):
    ans += random.choice(lets)
  return ans

class UnSub:
  def __init__(self, url, email, hashh):
    self.url = url
    self.email = email
    self.hashh = hashh
  def __repr__(self):
    return self.url + "  " + self.email

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
    body = parser.unescape(body)
    lower =  body.lower()
    length = len(lower)
  
    candidates = set()
    lower = lower.replace('unsubscribe.robot','a'*17).replace('unsubscriberobot','a'*16)
    startOrig = lower.rfind('content-type: text/html')
    if startOrig == -1:
      startOrig = lower.rfind('content-type: text/plain')
      if startOrig == -1:
        return set()
    
    for lp in linkPositives:
      start = startOrig
      while start > 5:
        c, start = getCandidateNearby(lower, body, lp, start)
        if c:
          candidates.add(c)
        start = lower.find(lp, start+1)
    return candidates
  except Exception as e:
    log.warn(e)
  return set()
    
  
def processOne(mail, i, actuallyCommit=False):
  log.info('email number '+str(i))
  try:
    unused, data = mail.fetch(str(i), '(RFC822)' )
  except Exception as e:
    log.info(e)
  hashh = newHash()
  for response_part in data:
    if not isinstance(response_part, tuple):
      continue
      
    msg = email.message_from_string(str(response_part[1]))
    fromAddress = getAddress(msg)
    
    body = msg.as_string()
    body = body.replace('=\r\n','')
    body = body.replace('=3D','=')
    
    candidates = getCandidates(body)
    i = 0
    for c in candidates:
      if i > 5:
        break
      i += 1 
      log.info('candidate', fromAddress, c)
      if actuallyCommit:
        commit('insert into unsubs (hash, url, email) values (%s, %s, %s)', (hashh, c, fromAddress))

def connect():
  mail = None
  try:
    f = open('/auth/gmail.txt')
    both = f.read().split('\n')
    f.close()
    address = both[0]
    password = both[1]
    imap = "imap.gmail.com"
  
    mail = imaplib.IMAP4_SSL(imap)
    mail.login(address,password)
  except Exception as e:
    log.info('exception connecting to gmail', e)
  return mail

def readEmailFromGmail(mail):
  data = None
  log.info('login and get emails')

  mail.select('inbox')
  now = (datetime.datetime.now()-timedelta(days=7)).strftime('%d-%b-%Y') 
  if now[0] == '0':
    now = now[1:]
  log.info('(SINCE %s)' % now)
  unused, data = mail.search(None, '(SINCE %s)' % now)
  
  if not data:
    log.info('no new emails %s', str(mail))
    return
  mail_ids = data[0]
  
  if not mail_ids:
    return
  id_list = mail_ids.split()
  first_email_id = int(id_list[0])
  latest_email_id = int(id_list[-1])
  
  log.info('track read in db')
  emails = fetch('select email from readmail')
  read = set()
  for e in emails:
    read.add(int(e[0]))
  processed = set()
  
  log.info('process')
  for i in range(first_email_id, latest_email_id+1):
    actuallyCommit = True
    if int(i) in read:
      actuallyCommit=False
      continue
    processOne(mail, i, actuallyCommit)
    processed.add(i)
  
  log.info('write read in db')
  for i in processed:
    commit('insert into readmail (email) values (%s)', i)
    