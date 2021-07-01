# does not work for emojis
import time

con = None
import pymysql
import time

f = open('/auth/sql.txt')
lines = f.readlines()
f.close()
user = lines[0][:-1]
password = lines[1][:-1]
ip = lines[2][:-1]

def closeDB():
  con.close()
  
def resetCon():
  global con
  time.sleep(.5)
  con = pymysql.connect(host=ip, user=user, password=password, db='unsubscribe', charset='utf8mb4')


def fetch(query, ps=None, tryNum=0):
  if tryNum == 3:
    return []
  rows = []
  try:
    with con:
      cur = con.cursor()
      cur.execute(query, ps)
      rows = cur.fetchall()
      cur.close() 
  except Exception as e:
    resetCon()
    return fetch(query, ps, tryNum+1)
  return rows
  
def commit(query, ps=None, tryNum=0):
  if tryNum == 3:
    return False
  try:
    with con:
      cur = con.cursor()
      cur.execute(query, ps)
      con.commit()
      cur.close() 
      return True
  except Exception as e:
    resetCon()
    return commit(query, ps, tryNum+1)
  return False
  
resetCon()
