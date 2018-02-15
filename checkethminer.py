#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
script to control if your etherium miner is working, if its not send an SMS (using AWS)
Created on Tue Jan 16 17:54:41 2018
Get info from api.ethmine.org
@author: ferreira

TODO: Add a max SMS per hour, or send only X amount after a fail, need to keep track of SMS sents
"""

import requests
import time
from time import gmtime, strftime
import os
import boto3

nowd=(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
nowds=(strftime("%H_%d_%m", gmtime()))

pwd=os.getcwd()
agem=0
ch=0
vs=0

##### EDIT HERE ######
wallet="852C8208795994700e9bDef6263337bd473B66aA"
URL0="https://api.ethermine.org/miner/%s/currentStats" %(wallet)
tel="<YOURNUMBER>"
aws_key="<YOURAPI>"
aws_sec="<YOURAPISEC>"
intMaxAge=30   #max time the worker has been seen.
intMinCurrentHashRate=3
intMinValidShares=1  #Last 1 hour
pwd="/var/log/ethminemon"
strLogFile=pwd + "/log_" + str(nowds) + ".log"

intMaxSmsPerHr=1 #TODO

verbose=1
logging=1

def sendsms(msg):
    msg=str(msg)
    client = boto3.client(
        "sns",
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_sec,
        region_name="us-east-1"
    )
    client.publish(
        PhoneNumber=tel,
        Message=msg
    )

def pt(*args):
    global verbose,strLogFile,logging,nowd
    if verbose == 1:
        print(""+" ".join(map(str,args))+"")
    if logging == 1:
        f = open(strLogFile,'a')
        txt=""+" ".join(map(str,args))+"\n"
        f.write(txt)
        f.close()

def getdata(urlp):
    global agem,ch,vs
    pt("Checking wallet: %s" %(wallet))
    params = {'User-Agent': 'Mozilla'}
    response = requests.get(URL0, params=params)
    myjson=response.json()
    lastSeen=myjson['data']['lastSeen']
    lastSeenD=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(lastSeen)))
    nowt=int(time.time())
    agem=nowt - int(lastSeen)
    agem=int(agem / 60)
    pt( 'lastSeen: %s - %d min ago.' %(lastSeenD,agem))
    ch=str(myjson['data']['currentHashrate'])
    ch=int(ch[0:2])
    pt( 'currentHashrate: %s' % ch)
    vs=int(myjson['data']['validShares'])
    pt( 'validShares(last 1hr): ', vs)
    aw=int(myjson['data']['activeWorkers'])
    pt( 'activeWorkers: ', aw)
    pt( 'status: ', myjson['status'])

########################### MAIN #############################

pt("---------------------------------------------------------------------")

pt(nowd)
getdata(URL0)

#ALERTS
if agem > intMaxAge:
    msge="ETH Miner - ERROR - The worker as not beeing updated in the last %i , it was last seen %i minutes ago!" %(intMaxAge,agem)
    pt(msge)
    sendsms(msge)

if ch < intMinCurrentHashRate:
    msge="ETH Miner - ERROR - The current hash rate: %i  is bellow the alert: %d" %(ch,intMinCurrentHashRate)
    pt(msge)
    sendsms(msge)

if vs < intMinValidShares:
    msge="ETH Miner - ERROR - The current valid shares(last 1hr) are: %d  is bellow the alert: %d" %(vs,intMinValidShares)
    pt(msge)
    sendsms(msge)
pt("More details on:\nhttps://ethermine.org/miners/%s" %(wallet))
