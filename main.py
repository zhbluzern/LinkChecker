#!/usr/bin/env python
# coding: utf-8

# # Alma-Link-Checker
# 
# Das ist ein Python-Skript um Ressourcen-Links in Alma zu überprüfen

import requests
import lxml.etree as ET
from lxml import etree
import urllib.parse
import urllib.request
import re
import waybackpy
from dotenv import load_dotenv
import os
import pandas as pd


# API-Key und Collection-ID wird aus .env File gelesen
def configure():
    load_dotenv()

# Kommentar hier kommt Wayback-Machine

def getWaybackUrl(url):
    user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
    wayback = waybackpy.Url(url, user_agent)
    try:
        archive = wayback.newest()
        return archive.archive_url
    except:
        try:
            archive = wayback.save()
            return archive.archive_url
        except:
            return None

        
def saveWaybackUrl(url):
    user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
    wayback = waybackpy.Url(url, user_agent)
    try:
        archive = wayback.save()
        return archive.archive_url
    except:
        return None 

def getWaybackUrl(url):
    user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
    wayback = waybackpy.Url(url, user_agent)
    try:
        archive = wayback.newest()
        return archive.archive_url
    except:
        return None
    

#Define Costum Variables like API-Keys, Collection-IDs etc
# ---------------------
configure()
# ---------------------

#headers = {'User-Agent': 'LinkChecker of ZHB-Luzern mailto:informatik@zhbluzern.ch'}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.360', 'referer':'https://f601722f1b888e75f8efe02bd2f39850.safeframe.googlesyndication.com/'}

#data = requests.get(portfolioUrl)

# Funktion um jeweils 100 Portofolios über die API zu harvesten
def getPortfolios(offset,os):
    portfolioUrl = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/electronic/e-collections/{os.getenv('collectionID')}/e-services/62238282890005505/portfolios?limit=100&offset={str(offset)}&apikey={os.getenv('apiKey')}"
    #print(portfolioUrl)
    root = ET.parse(urllib.request.urlopen(portfolioUrl))
    #Initial xpath to parse the first  records
    portfolios = root.findall(".//portfolio[@link]")
    return portfolios

# Abruf der ersten 100 Portfolios
offset=0
portfolios = getPortfolios(offset,os)

resultSet = []
while portfolios != []: #Schleife zum Abholen weiterer Portfolios solange Respond nicht leer ist
    for record in portfolios:
        resultDet = {}
        portfolioId =record.find(".//id")
        #print(portfolioId.text)
        resultDet["portfolioID"] = portfolioId.text
        mmsId = record.find(".//resource_metadata/mms_id")
        #print(mmsId.text)
        resultDet["MMS_ID"] = mmsId.text
        detPortUrl=f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/electronic/e-collections/{os.getenv('collectionID')}/e-services/{mmsId.text}/portfolios/{portfolioId.text}?apikey={os.getenv('apiKey')}"
        #print(detPortUrl)
        
        linkRoot = etree.parse(urllib.request.urlopen(detPortUrl))
        links = linkRoot.xpath(".//linking_details/*[local-name()='url' or local-name()='dynamic_url' or local-name()='static_url' or local-name()='static_url_override' or local-name()='dynamic_url_override'][text()]")
        for link in links:
            try:
                regex = r"^jkey=.*(http.*)"
                try:
                    matches = re.finditer(regex, link.text, re.MULTILINE)
                    for matchNum, match in enumerate(matches, start=1):
                        print(match.group(1))
                        resultDet["link"] = match.group(1)
                except TypeError:
                    pass
            except AttributeError:
                continue 

        #print(resultDet) 
        resultSet.append(resultDet)

    # Look up for the next 100 portfolios
    offset = offset+100
    portfolios = getPortfolios(offset,os)

# Remove duplicate links
df = pd.DataFrame(resultSet)
df = df.drop_duplicates(subset=["MMS_ID","link"])

# Check Request Status of Links and handle Wayback machine
status = []
wayBackUrlList = []
for index, row in df.iterrows():
    print(row["link"])
    try:
        if pd.isna(row["link"]) == True:
            status.append("kein Link eingetragen")
            wayBackUrlList.append("")
        else:
            linkCheck = requests.get(row["link"], headers=headers)
            status.append(linkCheck.status_code)
            if linkCheck.status_code == 200:
                #saveWaybackUrl(linkUrl)
                wayBackUrlList.append("")
                pass
            else:
                wayBackUrl = getWaybackUrl(row["link"])
                #print(wayBackUrl)
                wayBackUrlList.append(wayBackUrl)
        #print(getWaybackUrl(linkUrl))
    except requests.exceptions.SSLError:
        status.append("SSLError")
        wayBackUrlList.append("")
        print(f"{row['link']} cannot checked due to some python ssl errors")

df["status"] = status
df["wayBackUrl"] = wayBackUrlList

# Delete existing Outputfile
try:
    os.remove('linkChecker.xlsx')
    os.remove('linkChecker_full.xlsx')
except FileNotFoundError:
    pass

# filter resultset (no 200 and no 403 forbidden status) write Output-XLSX
#df = pd.DataFrame(resultSet)
df.to_excel('linkChecker_full.xlsx')
df = df.loc[(df['status'] != 200) & (df['status'] != 403) & (df['status'] != 502) & (df['status'] != 504)  & (df['status'] != "SSLError") & (df['status'] != "504") ]
if len(df.index)>0:
    df.to_excel('linkChecker.xlsx') 
else:
    print("no outputable results")