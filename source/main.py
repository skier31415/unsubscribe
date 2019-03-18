from sql import fetch
from sql import commit
import time
import sel as selenium
import gmail
import schema
import log
import hashlib
import datetime
import string
import random 
from datetime import timedelta

from sel import TimeoutClass, TimeoutException

salt = 'mysalt'
timeout = 90


def newHash():
  lets = string.ascii_letters[:26] + string.digits
  ans = 'tid'
  for i in range(8):
    ans += random.choice(lets)
  return ans
  
def hashEmail(email):
  email = email.lower() + salt
  m = hashlib.sha256()
  m.update(email)
  digest = m.hexdigest()
  return digest

class UnSub:
  def __init__(self, url, email, hashh):
    self.url = url
    self.email = email
    self.hashh = hashh
  def __repr__(self):
    return self.url + "  " + self.email

def getFive():
  # random order in case there's two slaves, don't likely grab the same unsub in high volume
  results = fetch('select url, email, hash from unsubs order by RAND() limit 1')
  s = set()
  for r in results:
    s.add(str(r[2]))
  origSet = set(s)
  if not s:
    return [], origSet
  s = str(list(s)).replace('[','(').replace(']',')')
  results = fetch('select url, email, hash from unsubs where hash in ' + s)
  l = list()
  for r in results:
    l.append(UnSub(r[0], r[1], r[2]))
  return l, origSet
  
def anonymousAnalytics(email, unsubhash, success=False):
  digest = hashEmail(email)
  
  now = str(datetime.datetime.now())
  results = fetch('select unsubhash, success from anonymousanalytics where unsubhash=%s', (unsubhash))
  success = int(success)
  if results:
    if int(results[0][1]) == 0 and success:
      commit('update anonymousanalytics set success=1 where unsubhash=%s', (unsubhash))
    else:
      log.info('unsub hash is still failing, do not update analytics', unsubhash)
  else:
    commit('insert into anonymousanalytics (emailhash, unsubhash, success, stamp) values (%s, %s, %s, %s)', (digest, unsubhash, str(success), now))
  
def fullAnalytics(email, url, success):
  s = int(success)
  commit('insert into analytics (email, url, success) values (%s, %s, %s)', (email, url, s))
    
def addEmailToSqlAnalytics(uns, success=False):
  email = uns.email
  hashh = uns.hashh
  url = uns.url
  anonymousAnalytics(email, hashh, success)
  if url:
    fullAnalytics(email, url, success)

def turnOffInstanceFromDocker():
  import os
  log.info('done sleeping in master')
  os.system('gcloud compute  --project "hosting-2718"  instances stop --zone "us-east1-d" "unsub2"')
  log.info('called stop')

def turnOff():
  import os
  log.info('done sleeping in slave')
  os.system('gcloud -q compute instances delete spot0 --zone=us-east1-d')
  os.system('gcloud -q compute instances delete spot6 --zone=us-east1-d')
  os.system('gcloud -q compute instances delete spot12 --zone=us-east1-d')
  os.system('gcloud -q compute instances delete spot18 --zone=us-east1-d')
  log.info('called stop')

def restart():
  import os
  log.info('restarting')
  os.system('sudo reboot')
  log.info('called restart')

def removeDockerCruft():
  import os
  #os.system('rm -rf /var/lib/docker/aufs')
  #log.info('docker cruft deleted')

def handleDB(it):
  ll, origSet = getFive()
  if not ll:
    if it > 2:
      log.info('empty turning off')
      #time.sleep(120)  # wait for master to finish
      turnOff()
    return
  log.info(str(len(ll))+str(ll))
  res = False
  try:
    i = 0
    uns = ll[0]
    for i in range(2):
      log.info('hashh',uns.hashh)
      with TimeoutClass(timeout):
        res = unsubscribe(uns)
      if res:
        break
  except Exception as e:
    log.warn(e)
  if not res:
    log.info('failed confirmation', uns.hashh)
    addEmailToSqlAnalytics(uns,False)
  else:
    log.info('confirmed unsub')
    commit('insert into usercount (another) values (1)')
    addEmailToSqlAnalytics(uns,True)
  log.info('deleting from unsubs '+str(origSet))
  for ss in origSet:
    commit('delete from unsubs where hash=%s', ss)

def unsubscribe(unsub):
  try:
    ans = False
    browser = selenium.getBrowser()
    ans = selenium.processPage(unsub,browser)
    selenium.closeBrowser(browser)
  except TimeoutException as e:
    raise TimeoutException()
  except Exception as e:
    log.warn('exception processing unsub '+ str(unsub))
    log.warn(e)
    ans = False
  return ans
  
def numUnsubs():
  results = fetch('select hash from unsubs')
  num = len(results)
  return num

def deleteAllUnsubs():
  results = fetch('select hash from unsubs')
  log.info('deleting all unsubs with # unsubs ' + str(len(results)))
  if len(results) < 15:
    for r in results:
      hh = r[0]
      commit('delete from unsubs where hash=%s',hh)
  
def mainMaster(wipe=False):
  log.tid = newHash()
  if wipe:
    schema.wipe()
  mail =  gmail.connect()
  
  it = 0
  while True:
    it += 1
    log.info('reading email')
    try:
      gmail.readEmailFromGmail(mail)
    except Exception as e:
      log.info('exception', e)
      if it % 2 == 1:
        try:
          mail = gmail.connect()
        except Exception as e:
          log.info('exception', e)
    sleeplen = 60
    if it % 1000 == 0:
      mail = gmail.connect()
    #removeDockerCruft()
    turnOffInstanceFromDocker()

def getAnalyticsForEmail(email):
  digest = hashEmail(email)
  results = fetch('select count(*) from anonymousanalytics where emailhash=%s', digest)
  total = results[0][0]
  results = fetch('select count(*) from anonymousanalytics where emailhash=%s and success=1', digest)
  successful = results[0][0]
  if email == 'admin':
    results = fetch('select count(*) from anonymousanalytics')
    total = results[0][0]
    results = fetch('select count(*) from anonymousanalytics where success=1')
    successful = results[0][0]
  if email == 'admin24':
    now = str(datetime.datetime.now()-timedelta(hours=24))
    results = fetch('select count(*) from anonymousanalytics where stamp > %s', now)
    total = results[0][0]
    results = fetch('select count(*) from anonymousanalytics where success=1 and stamp > %s', now)
    successful = results[0][0]
  return [str(int(successful)), str(int(total)-int(successful))]

def printAnalytics():
  log.tid = newHash()
  results = fetch('select * from analytics')
  log.info('all analytics', results)
  results = fetch('select count(*) from unsubs')
  log.info('current unsubs', results)
  log.info('print analytics total, successful, all broken')
  results = fetch('select count(*) from analytics')
  log.info('total', results)
  results = fetch('select count(*) from analytics where success=1')
  log.info('successful', results)
  results = fetch('select email, url from analytics where success=0')
  log.info(results)
  log.info('success / not success for william.k.dvorak')
  log.info(getAnalyticsForEmail('william.k.dvorak@gmail.com'))


def mainSlave():
  log.info('starting slave')
  log.tid = newHash()
  it = 0
  oldNum = 0
  timesSame = 0
  while True:
    it += 1
    try:
      if it > 300:
        restart()
      num = numUnsubs()
      log.info('current num unsubs ' + str(num))
      if num == oldNum:
        timesSame += 1
      else:
        timesSame = 0
      oldNum = num
      if timesSame > 15 and num < 5:
        deleteAllUnsubs()
      handleDB(it)
    except Exception as e:
      log.info('exception', e)



#firstCommand()
