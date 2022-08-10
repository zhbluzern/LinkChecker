#!/usr/bin/env python
# coding: utf-8

# # Alma-Link-Checker
# 
# Das ist ein Python-Skript um Ressourcen-Links in Alma zu überprüfen

# In[10]:


import requests
import xml.etree.ElementTree as ET
from lxml import etree
import urllib.parse
import urllib.request, json
import re
import waybackpy
import csv
import os

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
apiKey = ""
collectionID = ""
portfolioUrl = ""

# ---------------------

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

#data = requests.get(portfolioUrl)
#detPortUrl="https://api-eu.hosted.exlibrisgroup.com/almaws/v1/electronic/e-collections/61238282900005505/e-services/9914388509805505/portfolios/53257016710005505?apikey="+apiKey
print(portfolioUrl)

root = etree.parse(urllib.request.urlopen(portfolioUrl))
#Initial xpath to parse the first  records
portfolios = root.findall(".//portfolio[@link]")

resultSet = []
for record in portfolios:
    resultDet = {}
    portfolioId =record.find(".//id")
    print(portfolioId.text)
    resultDet["portfolioID"] = portfolioId.text
    mmsId = record.find(".//resource_metadata/mms_id")
    print(mmsId.text)
    resultDet["MMS_ID"] = mmsId.text
    detPortUrl="https://api-eu.hosted.exlibrisgroup.com/almaws/v1/electronic/e-collections/"+collectionID+"/e-services/"+mmsId.text+"/portfolios/"+portfolioId.text+"?apikey="+apiKey
    print(detPortUrl)
    
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
                    print(wayBackUrl)
                    linkResultDet["wayBackUrl"] = wayBackUrl
                    resultDet["wayBackUrl"] = wayBackUrl
                #print(getWaybackUrl(linkUrl))
        except AttributeError:
            continue 
        #linkResult.append(linkResultDet)
        #resultDet["links"] = linkResult
    
    resultSet.append(resultDet)


# In[11]:

os.remove('linkChecker.csv')

columnNames = ["portfolioID", "MMS_ID", "status", "link", "wayBackUrl"]
with open('linkChecker.csv', 'w',  newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = columnNames)
    writer.writeheader()
    writer.writerows(resultSet)


# In[ ]:




