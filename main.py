#!/usr/bin/env python
# coding: utf-8

# # Alma-Link-Checker
# 
# Das ist ein Python-Skript um Ressourcen-Links in Alma zu überprüfen

import requests
import xml.etree.ElementTree as ET
from lxml import etree
import urllib.parse
import urllib.request, json
import re
import waybackpy
import csv
from dotenv import load_dotenv
import os
import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

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
portfolioUrl = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/electronic/e-collections/{os.getenv('collectionID')}/e-services/62238282890005505/portfolios?limit=100&offset=0&apikey={os.getenv('apiKey')}"

# ---------------------

headers = {'User-Agent': 'LinkChecker of ZHB-Luzern mailto:informatik@zhbluzern.ch'}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.360', 'referer':'https://f601722f1b888e75f8efe02bd2f39850.safeframe.googlesyndication.com/'}

#data = requests.get(portfolioUrl)

root = etree.parse(urllib.request.urlopen(portfolioUrl))
#Initial xpath to parse the first  records
portfolios = root.findall(".//portfolio[@link]")

resultSet = []
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
    links = linkRoot.findall(".//linking_details/*")
    linkResult = []
    for link in links:
        linkResultDet = {}
        try:
            if (link.text.startswith("jkey=http")):
                linkUrl = re.sub("jkey=","",link.text)
                print(linkUrl)
                linkResultDet["linkUrl"] = linkUrl
                resultDet["link"] = linkUrl
                linkCheck = requests.get(linkUrl, headers=headers)
                resultDet["status"] = linkCheck.status_code
                if linkCheck.status_code == 200:
                    #saveWaybackUrl(linkUrl)
                    pass
                else:
                    wayBackUrl = getWaybackUrl(linkUrl)
                    #print(wayBackUrl)
                    linkResultDet["wayBackUrl"] = wayBackUrl
                    resultDet["wayBackUrl"] = wayBackUrl
                #print(getWaybackUrl(linkUrl))
        except AttributeError:
            continue 
        #linkResult.append(linkResultDet)
        #resultDet["links"] = linkResult

    #print(resultDet) 
    resultSet.append(resultDet)


# Delete existing Outputfile
try:
    os.remove('linkChecker.xlsx')
except FileNotFoundError:
    pass


# Filter ReesultSet for non 200 Status Code entries
newResultSet = list()
for entry in resultSet:
    try:
        if entry["status"] != 200:
            newResultSet.append(entry)
    except KeyError:
        #print("kein Link vorhanden?")
        entry["link"] = "kein Link eingetragen!"
        entry["status"] = "kein Link eingetragen!"
        newResultSet.append(entry)

# write Output-XLSX
df = pd.DataFrame(resultSet) 
df.to_excel('linkChecker.xlsx') 

