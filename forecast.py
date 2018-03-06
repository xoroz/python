#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 11:28:11 2018

@author: ferreira

Learning Python BeautifulSoup
Get forecast for the next 3 days
allows Liguria CIty as a paremeter, creates a html file (table) using precreated css file
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys

if len(sys.argv) > 1 :
    key=str(sys.argv[1])
else:
    key="rapallo"

strurl="http://liguriameteo.genovapost.com/previsioni/meteo/%s" % key
filename = "forecast-%s.html" % key

try:
    page = requests.get(strurl)
except:
    print("ERROR - could not load the URL %s" % strurl)
    sys.exit(2)

if page.status_code != 200:
    print("ERROR could not load URL %s" % strurl)
    sys.exit(2)

soup = BeautifulSoup(page.content , 'html.parser')
three_day = soup.find_all("div", class_="col-sm-12")[2]

days = list()
# had to be done, because days are not inside the data table
for da in three_day.select("h4"):
    da = da.get_text()
    i=1
    while i <= 3:
     days.append(da)
     i = i + 1

period = [p.get_text() for p in three_day.select("th")]
cond = [d["title"].replace("Condizioni del cielo: ","") for d in three_day.select(".cmeteo img")]

weather = pd.DataFrame({
        "Periodo": period,
        "Giorno": days,
        "Condizione": cond
        })
weather = weather[['Giorno','Periodo','Condizione']]
weather = weather.to_html(border=1).encode('utf-8')


# WRITE HTML FILE
f = open(filename,'w')
f.write("<html>\n")
f.write('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n')
f.write("<link rel=stylesheet type=text/css href=styletable.css>\n")
f.write(weather)
f.write("\n</html>")
f.close()
print("File %s updated" % filename)
sys.exit(0)
