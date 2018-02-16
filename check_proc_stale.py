# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 09:58:28 2018
#
# Script to check if a process is runnig for X hours, if so kill them 
# by Felipe Ferreira 02/2018 

#MAYBE A BUG:
1. if log dosent exit ERROR 
2. if process is not owned by the user it will fail with access denied!

@author: ferreira
"""


import time, os, psutil, sys
from time import gmtime, strftime
import shlex     # CMD SPLIT PROCESSING
import subprocess       # CALLING EXTERNAL CMDS



ts = int(time.time())
logging=1
verbose=1
intcount=0
strLogFile="check_proc_stale.log"

intpid=os.getpid() 
me=os.getlogin()
intcountkill=0

if len(sys.argv) == 3:
 strproc=sys.argv[1]
 intmaxhr=int(sys.argv[2])
else:
 strproc="chrome.exe"
 intmaxhr=1

def pt(*args): 
 if verbose == 1:       
  print(strftime("%H:%M:%S %d-%m-%Y",gmtime()) + " - " + str(intpid) + " - "+" ".join(map(str,args))+"")
 if logging == 1:      
  f = open(strLogFile,'a')    
  txt=""+" ".join(map(str,args))+"\n"    
  f.write((strftime("%H:%M:%S %d-%m-%Y", gmtime()) + " - " + str(intpid) + " - "+" ".join(map(str,args))+" " + txt))
  f.close()
def runj(cmd):
#Execute the external command and get its exitcode, stdout and stderr.
 args = shlex.split(cmd)    
 proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
 out, err = proc.communicate()
 exitcode = proc.returncode    
 return exitcode, out, err   

#################################################### MAIN ############################
for p in psutil.process_iter(attrs=['pid', 'name','username']):
 if strproc in p.info['name']:
  n = p.info['name']
  pi = int(p.info['pid'])
  u = p.info['username']
#if me in u:  #MAYBE ONLY TRY TO KILL IF IT IS MINE!? avoid access denied errors!
  pd = p.create_time() 
  d= int(ts) - int(pd)
  intdiffhrs=int(d / 3600)
  intcount+=1
  pt( "DEBUG PROCESS - Name: %s PID: %d Created: %d hours ago User: %s" %(str(n),int(pi), intdiffhrs, u))
  if intdiffhrs >= intmaxhr:
   pt( "KILLING STALE PROCESS - Name: %s PID: %d Created: %d hours ago User: %s" %(str(n),int(pi), intdiffhrs, u))
   strCmd="taskkill /F /PID %d" % pi
   exitcode, out, err = runj(strCmd)
   if exitcode != 0:
    print("CRITICAL - Could not kill a process ERROR: %s" %(str(err)))
    sys.exit(2)
   else:
    pt("OK - process %s killed" % n)
    intcountkill+=1
if intcount == 0:
 print("OK - Found %d process %s running|proc=%s" %(intcount,strproc,intcount))
 sys.exit(0)
else:
 print("WARNING - Found %d process %s running,and killed %d|proc=%s" %(intcount,strproc,intcountkill,intcount))
 sys.exit(2)
