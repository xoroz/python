#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 16:23:15 2018

this may not be reused, or maybe only parts of it.
it basicly monitor a folder and moves files from the GW to PRD and ARCH repositories and send an email
it creates a list of files found and process it by an external java 
it does call two bash script, one is to check if there are any open/writing files at the moment

bash checklock.sh (on my othe repo)

Last Update: 19/02/18
@author: Felipe Ferreira 
"""

import shlex                                 # CMD SPLIT PROCESSING
import subprocess                            # CALLING EXTERNAL CMDS
import os                                    # GENERIC OS OPERATIONS
import shutil                                # COPY 
from pyshorteners import Shortener           # GOOGLE SHORT URL API
import sys 
from os.path import splitext
from time import strftime, localtime
from datetime import datetime, timedelta
import smtplib
from random import randint

intrnd=randint(1000, 9999)  # RANDOM NUMBER
intpid=os.getpid()          # MY PROC PID 
blnfound=0
blnforce=0                  # USED TO FORCE LIST PROCESSING IF OUTDATED
intcount=0                  # COUNTER FOR ALL FILES PROCCESSED

listRunning = list()
##################EDIT HERE

stremail=['mymail@bobao.com']
me="newfilemon-dev@vaicatacoquinho.com"
rootdir = "/opt/REPO-GW-DEV"
prddir = "/opt/REPO-PRD-DEV"
archdir = "/opt/REPO-ARCH-DEV"
strLogFile="/opt/logs-dev/" + os.path.basename(__file__)[:-3] + "_" + strftime("%d_%m", localtime()) + ".log"
strLogFileList="/opt/logs-dev/" + os.path.basename(__file__)[:-3] + "_LIST.log"
strUrlBase="https://<USER>:<PASS>@<OWNCLOUD_SERVER_URL>/remote.php/webdav/"                                 

debug=0
logging=1
verbose=1
num_lines_max=10            # MAX ITENS ON THE LIST TO PROCESS LIST
intmaxtime=1                # MAX MINUTES TO PROCESS LIST
GOOGLE_API_KEY="BIBOASDBBOBAOBNE"
##################DONE EDIT

################ FUNCTIONS 
def scan(pathX):
#recursive go thru all files on pathX    
    global intcount
    for dp, dn, filenames in os.walk(pathX):
        for f in filenames:                                 
            try:
                process(dp + "/" + f)
                intcount+=1
            except:
                pt("ERROR processing file %s" %f)
def process(fileX): 
#process each file    
    archstamp=(strftime("%H%M%S", localtime()))
    path, filename = os.path.split(fileX)
    file_name,extension = splitext_(filename)        
# check if file is not being copied    
    checkopen()
    if filename in listRunning:
        pt("( %d )Skipping File %s is being copied" %(listRunning.len(), filename))
        return
    if extension == ".zip":
# check if zip file is not corrupted
        if checkzip(fileX) != "OK":
            pt("WARNING - Zip is corrupt, maybe file %s is in use, skipping." % file_name)
            return   
    pathArch=path.replace(rootdir,archdir)
    fileDistArch=pathArch + "/" + file_name + "_" + archstamp + str(extension)
    
    pathPrd=path.replace(rootdir,prddir)
    #fileDistPrd=pathPrd + "/" + file_name + "_" + str(intrnd) + str(extension)
    fileDistPrd=pathPrd + "/" + filename
    
    strUrlFilePrd=strUrlBase + str(pathPrd.replace("/opt/","")) + "/" + filename  
    strShortUrlFilePrd=shorturl(strUrlFilePrd)  #GOOGLE SHORT URL SERVICE
    if not os.path.exists(pathArch):
            os.makedirs(pathArch)             
    if not os.path.exists(pathPrd):
            os.makedirs(pathPrd)                         
    #existcheckprd(fileDistPrd)               #if any other versions of this files are found will delete it            
    
    try:
        shutil.copy2(fileX, fileDistArch)
        shutil.copy2(fileX, fileDistPrd)    
        os.remove(fileX)
    except BaseException as e:
        pt("ERRROR - : " + str(e))        
    pt(".............................................")        
    pt("Added File: " + str(filename) + " URL: " + strShortUrlFilePrd)
    pt("PRD  File at: " + str(fileDistPrd))
    ptd("ARCH File at: " + str(fileDistArch))
#SET OS PERMISSION    
    strCmd="/bin/chown root.apache " + str(fileDistPrd)
    exitcode, out, err = runj(strCmd)
    strCmd="/bin/chmod 755 " + str(fileDistPrd)
    exitcode, out, err = runj(strCmd)
    if exitcode != 0:
        pt("WARNING - could not set %s file permissions, error: %s " %(fileDistPrd, err) )    
    listwrite(fileDistPrd,strShortUrlFilePrd) 


def listwrite(fileP,urlP): 
#should first open and check if entry does not exist, avoid duplicates, if dosent add to the list and do listcheck()
    global blnfound
    blnfound=0          
    if not os.path.exists(strLogFileList):
        open(strLogFileList, 'a').close()    
    with open(strLogFileList, "r+") as f:
        for line in f:  
            if fileP in line:  
                 pt("File Already in the list")
                 blnfound=1       
        if blnfound != 1:            
            f.write(str(fileP) + " ; " + urlP + "\n")            
            f.close()
            ptd("Added %s file to the list" % str(fileP))            
            blnfound=1
            listcheck()
        f.close()
    
def listcount():
#get number of itens in the list and each line    
    num_lines=0
    lines=""       
    if os.path.exists(strLogFileList):        
        with open(strLogFileList, "r") as f:
            for line in f:                
                lines=lines + str(line) + "<br>" 
                num_lines+=1
            f.close                
            return num_lines,lines
    else:
        if not os.path.exists(strLogFileList):
            open(strLogFileList, 'a').close()
            return 

def listcheck():
#check if list has reached the max number, then we send the e-mail requesting approval
#group files and avoid e-mail out for each single file
    num_lines,lines = listcount()        
    if num_lines >= 1:
        pt("(%d/%d) itens in the LIST " %(num_lines,num_lines_max)) 
        if num_lines >= num_lines_max or blnforce == 1:
            msge="Waiting for approval of the following new files: <br> %s" %(lines)
            strCmd='/bin/runjava.sh'        
            exitcode, out, err = runj(strCmd)            
            if exitcode != 0:
                pt("ERROR - The %s returned an error" % strCmd)            
                pt(out,err)
            else:
                pt("The %s ran succesfully" % strCmd)                            
                pt(out)        
            sendmailm("Found " + str(num_lines) + " new files waiting for approval",stremail,msge)
            pt("Found " + str(num_lines) + " new files sent to repo PRD" )
            strLogFileListRen= strLogFileList + "_" + strftime("%H_%M_%S_%d-%m-%Y", localtime()) + ".sent"
            os.rename(strLogFileList,strLogFileListRen)    
            pt(strLogFileList + " - reanmed")
    else:
        return                    
 
def listlastmod():
    global blnforce    
    max_delay = timedelta(minutes=intmaxtime)
    if os.path.exists(strLogFileList):
        file_mod_time = datetime.fromtimestamp(os.stat(strLogFileList).st_mtime)  # This is a datetime.datetime object!            
    else:                
        open(strLogFileList, 'a').close()            
        file_mod_time = datetime.fromtimestamp(os.stat(strLogFileList).st_mtime)  # This is a datetime.datetime object!            
    intdelta = datetime.today() - file_mod_time   
    if intdelta > max_delay:
        ptd("LIST is outdated: {} last modified on {}. Threshold set to {} minutes.".format(strLogFileList, file_mod_time, max_delay.seconds/60))
        blnforce = 1
        listcheck()
        blnforce = 0
        
def existcheckprd(strFilePrd):
    path, filename = os.path.split(strFilePrd)    
    strFilePart = shortfilename(strFilePrd)
    ptd("Search for: %s in %s" % (strFilePart,path))
    for f in os.listdir(path):       
        if strFilePart in f:
            strFileDel=str(path) + "/" + str(f)           
            os.remove(strFileDel)
            pt("Deleting File: %s " % strFileDel)

def checkzip(fileZ):
#make sure that the zip file is complete and works
    strCmd="/bin/unzip -t %s" % fileZ
    exitcode, out, err = runj(strCmd)                       
    if exitcode != 0:
        #pt("ERROR - The %s returned an error, maybe the file is in use!" % strCmd)            
        #pt(err)
        return "ERROR"
    else:
        return "OK"

def splitext_(path):
    if len(path.split('.')) > 2:
        return path.split('.')[0],'.'.join(path.split('.')[-2:])
    return splitext(path)

def checkopen():
     global listRunning
#Check if any samba/vsftpd copying is running, if so just exit
     strCmd="/fsNAS/bin/checklock-dev.sh"
     ptd("Checking for samba/vsftpd locks: " + str(strCmd))     
     exitcode, out, err = runj(strCmd)                                 
     if out != "":
        out=str(out)
        pt("WARNING - File is being copied, skipping: %s " % out)
        fileru = out.split("/")
        strfileru=fileru[-1]
        if not strfileru in listRunning:
            listRunning.append(strfileru)
        # DEBUG 
        for item in listRunning:
            pt("RUNNING LIST HAS %s" %str(item))
        #sys.exit(0)        
     else:
        return 

def runj(cmd):
#Execute the external command and get its exitcode, stdout and stderr.
    args = shlex.split(cmd)    
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode    
    return exitcode, out, err   
            
def sendmailm(subj,to,text):    
    pt("Sending email to: %s" % to)
    from email.mime.multipart import MIMEMultipart
#    from email.mime.text import MIMEText
    msg = MIMEMultipart('alternative')    
    msg.add_header('Content-Type','text/html')
    msg['Subject'] = subj
    msg['From'] = me 
    msg['To'] = ", ".join(to)
    html = "\
    <html> \
      <head></head> \
      <body> \
        <p>%s<br>           \
           <a href=https://<YOUR_URL>>link to repo</a> \
        </p> \
      </body> \
    </html> "  %( text ) 
    msg.set_payload(html)           
    s = smtplib.SMTP('localhost')    
    #s.sendmail(msg['From'], [msg['To']], msg.as_string())    
    s.sendmail(me, to, msg.as_string())        
    #s.send_message(text)
    s.quit()

def shorturl(urlX):
#COULD HAVE A RETRY ?    
    proxy = 'http://<IP:PORT>'
    os.environ['http_proxy'] = proxy 
    os.environ['HTTP_PROXY'] = proxy
    os.environ['https_proxy'] = proxy
    os.environ['HTTPS_PROXY'] = proxy    
    shortener = Shortener('Google', api_key=GOOGLE_API_KEY)
    try:        
        urlX=format(shortener.short(urlX))
    except BaseException as e:
        pt("ERRROR - Could not shorten the URL : " + str(e))        
        sys.exit(2)
        return 
    ptd("Short url is: " + urlX)
    return urlX

def ptl(*args):    
    f = open(strLogFile,'a')    
    txt=""+" ".join(map(str,args))+"\n"    
    f.write(txt)
    f.close()
     
def pt(*args):        
    if verbose == 1:       
        print(strftime("%H:%M:%S %d-%m-%Y", localtime()) + " - " + str(intpid) + " - "+" ".join(map(str,args))+"")
    if logging == 1:      
        ptl(strftime("%H:%M:%S %d-%m-%Y", localtime()) + " - " + str(intpid) + " - "+" ".join(map(str,args))+"")

def ptd(*args):        
    if debug == 1:
        print(strftime("%H:%M:%S %d-%m-%Y", localtime()) + " DEBUG " + str(intpid) + " - "+" ".join(map(str,args))+"")        
        
#############################  MAIN         
# CHECK OS 
if os.name != 'posix':    
    print("Sorry - This script has only being tested in linux and you are running: %s" %(os.name))
    sys.exit(2)
    
startTime = datetime.now()
listlastmod()
scan(rootdir)
if intcount > 0:
    totalTime = datetime.now() - startTime
    if len(listRunning) != 0:
        pt("Processed %d files and %d were busy,  in %s " % (intcount,len(listRunning),str(totalTime)[2:-4]))
    else:
        pt("Processed %d files in %s " % (intcount,str(totalTime)[2:-4]))
    pt("-------------------------------------------------------------------------------------------------------------------")
sys.exit(0)
