# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:53:06 2018
@author: ferreira
# before starting make sure there are no stale chromedriver.exe presents(older then x hours)
"""

#import re
import sys 
import os 
from datetime import datetime
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import ui
from selenium.webdriver.common.by import By
from time import strftime, time 
from selenium  import webdriver
#import unittest

### EDIT HERE ###
username='USER'
password='PASSWORD'
verbose=0
logging=1
maxTime=20
intMaxLoadTime=15 #per singola pagina
### DONE EDIT ###
intpid=os.getpid()   

cwd = str(os.getcwd())
logd="%s\selenium-logs" % cwd
today=int(datetime.today().weekday())
strLogFile="%s\logfile-%d.txt" %(logd,today)

if not os.path.exists(logd):
    os.makedirs(logd)    

def pt(*args):        
    txt=""+" ".join(map(str,args))+"\n"    
    stamp=datetime.now().strftime("%H:%M:%S %d-%m-%Y")    
    if "CRITICAL" in txt or "OK" in txt:        
        print(txt)
    if verbose == 1:       
           print(stamp + " - " + str(intpid) + " - "+ txt)
    if logging == 1:      
        f = open(strLogFile,'a')            
        f.write((stamp + " - " + str(intpid) + " - "+ txt))
        f.close()		
        
def check_stale_procs():
    import psutil
    intcount=0
    intmaxhr=1             # PROCESS STALE TIME
    intcountkill=0
    ts = int(time())
    strproc1="chromedriver.exe"
    strproc2="chrome.exe"
    
    for p in psutil.process_iter(attrs=['pid', 'name','username']):
     if strproc1 in p.info['name'] or strproc2 in p.info['name']:
      n = p.info['name']
      pi = int(p.info['pid'])
      u = p.info['username']
    #if me in u:  #MAYBE ONLY TRY TO KILL IF IT IS MINE!? avoid access denied errors!
      pd = p.create_time() 
      d= int(ts) - int(pd)
      intdiffhrs=int(d / 3600)
      intcount+=1
      pt( "FOUND STALE PROCESS - Name: %s PID: %d Created: %d hours ago User: %s" %(str(n),int(pi), intdiffhrs, u))
      if intdiffhrs >= intmaxhr:
  #     pt( "KILLING STALE PROCESS - Name: %s PID: %d Created: %d hours ago User: %s" %(str(n),int(pi), intdiffhrs, u))
       proc = psutil.Process(pi)   
       try:
        proc.terminate() 
        intcountkill+=1
       except:
        pt("ERROR - Could not kill the service, Name: %s PID: %d Created: %d hours ago, ERROR %s" %(str(n),int(pi), intdiffhrs, sys.exc_info()[0]))        
      intcountkill+=1
      pt("Proccess %s killed" % n)    
    #if intcount != 0:
    # print("WARNING - Found %d process %s running,and killed %d|proc=%s" %(intcount,strproc,intcountkill,intcount))

#######################   MAIN    #######################
check_stale_procs()

    
### CHROME DRIVER
options = webdriver.ChromeOptions()
options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
options.add_argument('--disable-gpu')
options.add_argument('headless')
options.add_argument('--no-sandbox')
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--incognito")
options.add_argument("disable-infobars")
#options.add_argument("--enable-logging=v=1")  #C:\Program Files (x86)\Google\Chrome\Application\chrome_debug.log
b = webdriver.Chrome(chrome_options=options)

# 1 LOGIN PAGE
###############################################################
startTime = datetime.now()
strurl="<YOUR_URL>"
step="1-login"
b.get(strurl)
b.save_screenshot("%s\gpnx-step-%s.png" %(logd,step))
try:
    ui.WebDriverWait(b, intMaxLoadTime).until(EC.element_to_be_clickable((By.ID, 'submitButton')))
except:
    pt("CRITICAL - Error - %s could not load the page, after %d secons" % (step,intMaxLoadTime))
    b.save_screenshot("%s\gpnx-error-%s.png" %(logd,step))
    b.quit()
    sys.exit(2)
    
U = b.find_element_by_id("username")
P = b.find_element_by_id("password")
B = b.find_element_by_id('submitButton')

U.send_keys(username)
P.send_keys(password)
B.click()

#2 WAIT THE LANDING PAGE TO LOAD AND CLICK ON DM TIME
step="2-click-dmtime"
try:    
    ui.WebDriverWait(b, intMaxLoadTime).until(EC.presence_of_element_located((By.XPATH,"//label[@class='<SOMETHINGHERE>']")))    
    ui.WebDriverWait(b, intMaxLoadTime).until(EC.presence_of_element_located((By.XPATH,"//div[@class='<SOMETHINGHERE>")))
    ui.WebDriverWait(b, intMaxLoadTime).until(EC.presence_of_element_located((By.XPATH,"//span[@id='<SOMETHINGHERE>']")))    
except:
    pt("CRITICAL - Error - %s could not load the page, after %d secons" % (step,intMaxLoadTime))    
    b.save_screenshot("%s\error-%s.png" %(logd,step))
    b.quit()
    sys.exit(2)
b.save_screenshot("%s\step-%s.png" %(logd,step))
B1 = b.find_element_by_xpath("//img[@src='/<SOMETHINGHERE>']")
B2 = b.find_element_by_xpath("//a[@href='<SOMETHINGHERE>']")
ActionChains(b).move_to_element(B1).click(B2).perform()


totalTime = datetime.now() - startTime
intTotalTime = int(str(totalTime)[5:-7])
#print("INTEGER SECONDS TIME:" + str(intTotalTime))
if  intTotalTime > maxTime:
	pt("CRITICAL - Site took longer then %d Checked in %s |time=%s" %(maxTime, str(totalTime)[5:-4], str(totalTime)[5:-4]))
	b.quit()
	sys.exit(2)
else:
	pt("OK - Site Checked in %s |time=%s" %(str(totalTime)[5:-4], str(totalTime)[5:-4]))
	b.quit()
	sys.exit(0)
