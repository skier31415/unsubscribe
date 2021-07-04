from sql import commit

def setup():
  commit('''CREATE TABLE unsubs(id INT NOT NULL AUTO_INCREMENT, \
    hash VARCHAR(8), \
    url VARCHAR(1000), \
    email VARCHAR(150), \
    PRIMARY KEY (id))''')
    
  commit('''CREATE TABLE readmail(id INT NOT NULL AUTO_INCREMENT, \
    email INT, \
    PRIMARY KEY (id))''')
    
  commit('''CREATE TABLE readmailhash(id INT NOT NULL AUTO_INCREMENT, \
    email VARCHAR(16), \
    PRIMARY KEY (id))''')
    
  commit('''CREATE TABLE usercount(id INT NOT NULL AUTO_INCREMENT, \
    another INT, \
    PRIMARY KEY (id))''')
    
  commit('''CREATE TABLE analytics(id INT NOT NULL AUTO_INCREMENT, \
    email VARCHAR(150), \
    url VARCHAR(1000), \
    success INT, \
    PRIMARY KEY (id))''')
    
  commit('''CREATE TABLE anonymousanalytics(id INT NOT NULL AUTO_INCREMENT, \
    emailhash VARCHAR(64), \
    unsubhash VARCHAR(8), \
    success INT, \
    stamp DATETIME, \
    PRIMARY KEY (id))''')

def wipe():
  commit('''drop table unsubs''')
  commit('''drop table readmail''')
  commit('''drop table usercount''')
  commit('''drop table emailhashespositive''')
  commit('''drop table emailhashestotal''')
  commit('''drop table analytics''')
  setup()