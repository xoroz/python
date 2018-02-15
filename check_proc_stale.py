#
# Script to check if a process is runnig for X hours, if so kill them 
# by Felipe Ferreira 02/2018 
#
# IMPORTANT: is the process is running under SYSTEM account it must likely will fail with access denied!
# in my case I had to run the nsclient all under a specific local account, and it worked
#
import time, os, psutil, sys
from time import gmtime, strftime


ts = int(time.time())
logging=1
verbose=1
intcount=0
#strLogFile="C:\Program Files\NSClient++\scripts\check_proc_stale.log"
strLogFile="check_proc_stale.log"
intpid=os.getpid() 
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
	
for p in psutil.process_iter(attrs=['pid', 'name','status']):
	if strproc in  p.info['name']:
		n = p.info['name']
		pi = p.info['pid']
		pd = p.create_time()		
		d= int(ts) - int(pd)
		intdiffhrs=int(d / 3600)
		intcount+=1
		if intdiffhrs > intmaxhr:		
			pt( "KILLING STALE PROCESS - Name: %s PID: %d Created: %d hours ago" %(str(n),int(pi), intdiffhrs))
			proc = psutil.Process(pi)
			try:
				proc.terminate() 
				intcountkill+=1
			except:
			
				pt("ERROR - Could not kill the service, Name: %s PID: %d Created: %d hours ago, ERROR %s" %(str(n),int(pi), intdiffhrs, sys.exc_info()[0]))
			

if intcount	== 0:
	pt("OK - Found %d process %s running|proc=%s" %(intcount,strproc,intcount))
	sys.exit(0)
else:
	pt("WARNING - Found %d process %s running,and killed %d|proc=%s" %(intcount,strproc,intcountkill,intcount))
	sys.exit(2)
	
