import datetime
from datetime import timedelta
import os

def hashEmail(a):
  return 'aoeu'

import sql
from sql import fetch
from sql import commit

def countPending():
  results = fetch('select count(*) from unsubs')
  print 'num pending', results
  results = fetch('select * from unsubs')
  print 'pending', results
  
  results = fetch('select count(hash) from unsubs')
  print results
  results = fetch('select count(distinct unsubhash) as b from anonymousanalytics group by emailhash order by b desc')
  #print results
  results = fetch('select count(distinct emailhash ) from anonymousanalytics ')
  print results

def deleteAllUnsubs():
  commit('delete from unsubs where true')

def percentSuccess():
  results = fetch('select success, count(*) from anonymousanalytics group by success')
  print 'success ', results
  dt = datetime.datetime.now() - timedelta(days=20)
  results = fetch('select success, count(*) from anonymousanalytics  where stamp > %s group by success',str(dt)[:11])
  print 'success within 20 days', results
# ("Fetch query:select success, count(*) from anonymousanalytics  where stamp > %s group by success['2018-06-02 ']",)
#   success within 20 days [[0L, 651L], [1L, 787L]]
  
percentSuccess()
countPending()
deleteAllUnsubs()
#import sel

class Uns:
  pass
  
def doUns():
  from selenium import webdriver
  from selenium.webdriver.common.keys import Keys
  print '1'
  driver = webdriver.Firefox()
  print '2'
  driver.get("http://www.python.org")
  print '3'
  assert "Python" in driver.title
  print '4'
  return
  import time
  uns = Uns()
  uns.url='https://click.message.fedex.com/?qs=a2d39ce5274aae028bee17e957371943e3fd281bf03dd1f0a3d9f21d7485636a7c3adb30cca5f54411b2950e842dfe89047581c60e19e136'
  uns.email='william.k.dvorak@gmail.com'
  uns.hashh = 'default'
  browser = sel.getBrowserNoDisplay()
  print 'hre22',browser
  print sel.processPage(uns,browser)
  time.sleep(30)
  browser = sel.getBrowser()
  print 'hre',browser
  print sel.processPage(uns,browser)
  browser = sel.getBrowserNoDisplay()
  print 'hre22',browser
  print sel.processPage(uns,browser)
  print 'done'


def allUnsuccessful():
  results = fetch('select email, url from analytics where success=0')
  ss = dict()
  for r in results:
    ss[str(r[1])] = str(r[0])
  i = 0
  low = 200
  high = low+10
  print len(ss.keys())
  for k,v in ss.iteritems():
    if i > low:
      os.system('open '+k)
      print v
      print k
    i+=1
    if i > high:
      break
    
#allUnsuccessful()

def getProblem():
  hashh = 'lrnbgg19'
  results = fetch('select * from unsubs where hash="lrnbgg19"')
  print results
  results = fetch('select count(*) from unsubs ')
  print results
  
#getProblem()

def anal(email):
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
  
def deleteReadEmail17days():
  results = fetch('select email from readmail')
  print results[-10:]
  
  start = 6000
  for r in results:
    commit('delete from readmail where email=%s',str(start))
    start += 1
  results = fetch('select email from readmail')
  print results[-10:]


  
def deleteLastReads():
  results = fetch('select email from readmail')
  print results[-10:]
  
  total = len(results)
  
  for r in results[total-150:]:
    commit('delete from readmail where email=%s',r[0])
  results = fetch('select email from readmail')
  print results[-10:]
  
#deleteLastReads()
#deleteReadEmail17days()