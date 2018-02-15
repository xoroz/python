#
# Script to check if a process is runnig for X hours, if so kill them 
# by Felipe Ferreira 02/2018 

import time, os, psutil, sys
from time import gmtime, strftime

#POSSIBILE BUG: if log dosent exit ERROR permission 

ts = int(time.time())
logging=1
verbose=0
intcount=0
strLogFile="check_proc_stale.log"

intpid=os.getpid() 
me=os.getlogin()
intcountkill=0

if len(sys.argv) == 3:
	strproc=sys.argv[1]
	intmaxhr=sys.argv[2]
	
else:
	strproc="chrome.exe"
	intmaxhr=1

def pt(*args):        
    if verbose == 1:       
        print(strftime("%H:%M:%S %d-%m-%Y", gmtime()) + " - " + str(intpid) + " - "+" ".join(map(str,args))+"")
    if logging == 1:      
        f = open(strLogFile,'a')    
        txt=""+" ".join(map(str,args))+"\n"    
        f.write((strftime("%H:%M:%S %d-%m-%Y", gmtime()) + " - " + str(intpid) + " - "+" ".join(map(str,args))+" " + txt))
        f.close()
	
for p in psutil.process_iter(attrs=['pid', 'name','username']):
	if strproc in  p.info['name']:
		n = p.info['name']
		pi = p.info['pid']
		u = p.info['username']
		if me in u:
			pd = p.create_time()		
			d= int(ts) - int(pd)
			intdiffhrs=int(d / 3600)
			intcount+=1
			#pt( "DEBUG PROCESS - Name: %s PID: %d Created: %d hours ago User: %s" %(str(n),int(pi), intdiffhrs, u))
			if intdiffhrs > intmaxhr:			
				pt( "KILLING STALE PROCESS - Name: %s PID: %d Created: %d hours ago User: %s" %(str(n),int(pi), intdiffhrs, u))
				proc = psutil.Process(pi)
				try:
					proc.terminate() 
					intcountkill+=1
				except:			
					pt("ERROR - Could not kill the service, Name: %s PID: %d Created: %d hours ago, ERROR %s" %(str(n),int(pi), intdiffhrs, sys.exc_info()[0]))
					print("ERROR - Could not kill the service, Name: %s PID: %d Created: %d hours ago, ERROR %s" %(str(n),int(pi), intdiffhrs, sys.exc_info()[0]))
if intcount	== 0:
	print("OK - Found %d process %s running|proc=%s" %(intcount,strproc,intcount))
	sys.exit(0)
else:
	print("WARNING - Found %d process %s running,and killed %d|proc=%s" %(intcount,strproc,intcountkill,intcount))
	sys.exit(2)
