# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:53:06 2018

@author: ferreira

Simple selenium with chromedriver (tested only with Windows)
Requires: chromedriver.exe and chrome browser installed 
For headless just uncomment the line 45

"""

import sys 
from os import getpid
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import ui
from selenium.webdriver.common.by import By
from time import gmtime, strftime
from datetime import datetime #, timedelta
from selenium  import webdriver
#import unittest

### VARIABLE ###
username='ze@msn.com'
password='cacaca'
strLogFile="logfile.txt"
verbose=1
logging=0
intpid=getpid()   
maxTime=9

def pt(*args):        
    if verbose == 1:       
        print(strftime("%H:%M:%S %d-%m-%Y", gmtime()) + " - " + str(intpid) + " - "+" ".join(map(str,args))+"")
    if logging == 1:      
        f = open(strLogFile,'a')    
        txt=""+" ".join(map(str,args))+"\n"    
        f.write((strftime("%H:%M:%S %d-%m-%Y", gmtime()) + " - " + str(intpid) + " - "+" ".join(map(str,args))+" " + txt))
        f.close()
		
### CHROME DRIVER
options = webdriver.ChromeOptions()
options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
options.add_argument('--disable-gpu')
#options.add_argument('headless')
options.add_argument('--no-sandbox')
options.add_argument("--disable-extensions")
options.add_argument("--incognito")
options.add_argument("disable-infobars")
#options.add_argument("--enable-logging=v=1")  #C:\Program Files (x86)\Google\Chrome\Application\chrome_debug.log
b = webdriver.Chrome(chrome_options=options)

startTime = datetime.now()
b.get('https://finance.yahoo.com/')
b.save_screenshot("step-1.png")
try:    
    ui.WebDriverWait(b, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@title='Cryptocurrencies']")))  
except:
    print("Error - Could not load the page, after 5 secons")
    b.save_screenshot("step-1-ERROR.png")
    b.quit()
    sys.exit(2)
B = b.find_element_by_xpath("//a[@title='Cryptocurrencies']")    
B.click()
#WAIT FOR IT TO LOAD
try:    
    ui.WebDriverWait(b, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@title='Bitcoin USD']")))  
except:
    print("Error - Could not load the page, after 5 secons")
    b.save_screenshot("step-2-ERROR.png")
    b.quit()
    sys.exit(2)
b.save_screenshot("step-1.png")
b.quit()

totalTime = datetime.now() - startTime
intTotalTime = int(str(totalTime)[5:-7])
#print("INTEGER SECONDS TIME:" + str(intTotalTime))
if  intTotalTime > maxTime:
	pt(" - CRITICAL - Site took longer then %d Checked in %s |time=%s" %(maxTime, str(totalTime)[5:-4], str(totalTime)[5:-4]))
	b.quit()
	sys.exit(2)
else:
	pt(" - OK - Site Checked in %s |time=%s" %(str(totalTime)[5:-4], str(totalTime)[5:-4]))
	b.quit()
	sys.exit(0)
    

sys.exit(0)    
