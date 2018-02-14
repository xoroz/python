#
# Script to check if a process is runnig for X hours, if so kill them 
# by Felipe Ferreira 02/2018 

import time, os, psutil, sys

ts = int(time.time())

intcount=0
intcountkill=0
if len(sys.argv) == 3:
	strproc=sys.argv[1]
	intmaxhr=sys.argv[2]
else:
	strproc="chrome.exe"
	intmaxhr=1

for p in psutil.process_iter(attrs=['pid', 'name','status']):
	if strproc in  p.info['name']:
		n = p.info['name']
		pi = p.info['pid']
		pd = p.create_time()		
		d= int(ts) - int(pd)
		intdiffhrs=int(d / 3600)
		intcount+=1
		if intdiffhrs > intmaxhr:		
			print( "KILLING STALE PROCESS - Name: %s PID: %d Created: %d hours ago" %(str(n),int(pi), intdiffhrs))
			proc = psutil.Process(pi)
			proc.terminate() 
			intcountkill+=1

if intcount	== 0:
	print("OK - Found %d process %s running|proc=%s" %(intcount,strproc,intcount))
	sys.exit(0)
else:
	print("WARNING - Found %d process %s running,and killed %d|proc=%s" %(intcount,strproc,intcountkill,intcount))
	sys.exit(2)
	
