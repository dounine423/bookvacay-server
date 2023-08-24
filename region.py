import os
import json
import requests
import hashlib
import urllib.parse
from  db import selectQuery
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

FAST_END_POINT=os.getenv('FAST_END_POINT')
FAST_API_KEY=os.getenv('FAST_API_KEY')
PAYFAST_END_POINT=os.getenv('PAYFAST_END_POINT')

def getCountries():
    select =" country_id , name ,iso2 ,phonecode ,currency"
    countryData=selectQuery(select,'countries')
    result=[]
    for item in countryData:
        data={
            "countryCode":item[0],
            "name":item[1],
            "code":item[2],
            "phoneCode":item[3],
            "currency":item[4]
        }
        result.append(data)
    return result

def getDestinations():
    select =" destination.code, destination.content, destination.country_code, countries.name"
    where= " destination.country_code = countries.iso2" 
    destinations=selectQuery(select,'destination ,countries',where)
    result=[]
    for item in destinations:
        data={
            "code":item[0],
            "name":item[1],
            "countryCode":item[2],
            "countryname":item[3]
        }
        result.append(data)
    return result

def getCurrencyInfo(params):
    select="id,rate"
    where=" id = (select max(id) from bank_mark_up )"
    bank_mark_up=selectQuery(select,'bank_mark_up',where)[0][0]
    clientC=params
    hotelC="USD"
    portalC="ZAR"
    header={
       "accept": "application/json"
    }
    url=FAST_END_POINT+"/fetch-multi?api_key="+FAST_API_KEY+"&from="+hotelC+"&to="
    if portalC==clientC:
        url+=portalC
    else:
        url+=portalC+","+clientC
    res=requests.get(url,headers=header)
    temp=json.loads(res.text)
    result={
        "client":temp['results'][clientC],
        "portal":temp['results'][portalC],
        "update":temp['updated'],
        "bank_mark_up":bank_mark_up
    }
    return result


def getFacilities():
    result=[]
    wifi=[
        {
            "code": "70*550",
            "facilityCode": 550,
            "facilityGroupCode": 70,
            "name": "Wi-Fi (Hotel)",
            "checked": False
        },
        {
            "code": "70*250",
            "facilityCode": 250,
            "facilityGroupCode": 70,
            "name": "Wired Internet",
            "checked": False
        },
        {
            "code": "60*261",
            "facilityCode": 261,
            "facilityGroupCode": 60,
            "name": "Wi-Fi (Room)",
            "checked": False
        },
        {
            "code": "60*100",
            "facilityCode": 100,
            "facilityGroupCode": 60,
            "name": "Internet Access",
            "checked": False
        }
    ]
    wifiGroup={
        "code":70,
        "name":"Internet Access",
        "column":"wifi",
        "data":wifi
    }
    result.append(wifiGroup)
    select=" code, content"
    where=" code = 73 or code = 74 or code = 90"
    fGroup=selectQuery(select,'facilitygroup',where)
    for item in fGroup:
        select=" code, facilityGroupCode, content"
        where=f" facilityGroupCode = {item[0]}"
        facilities=selectQuery(select,'facility',where)
        facilityData=[]
        for facility in facilities:
            tempFacility={
                "facilityCode":facility[0],
                "facilityGroupCode":facility[1],
                "name":facility[2],
                "code":str(facility[1])+"*"+str(facility[0]),
                "checked":False
            }
            facilityData.append(tempFacility)
        tempFacilityGroup={
            "code":item[0],
            "name":item[1],
            "column":item[1].lower(),
            "data":facilityData
        }
        result.append(tempFacilityGroup)
    return result

def getCurrency():
    select=" code, content"
    table_from=" currency"
    result=[]
    temp=selectQuery(select=select,table=table_from)
    for item in temp:
        data={
            "code":item[0],
            "content":item[1]
        }
        result.append(data)
    return result

def generateApiSignature(dataArray, passPhrase = ''):
    payload = ""
    if passPhrase != '':
        dataArray['passphrase'] = passPhrase
    sortedData = sorted (dataArray)
    for key in sortedData:
        payload += key + "=" + urllib.parse.quote_plus(dataArray[key].replace("+", " ")) + "&"
    payload = payload[:-1]
    return hashlib.md5(payload.encode()).hexdigest()

def getPfPaymentId(token):
    url=PAYFAST_END_POINT+"process/query/"+token
    header={
        "merchant-id":"13307418",
        "version":"v1"
    }
    timestamp=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    header['timestamp']=timestamp
    header['signature']=generateApiSignature(header)
    res=requests.get(url=url,headers=header)
    json_res=json.loads(res.text)
    pfData=json_res['data']['response']['pf_payment_id']
    return str(pfData) 

def getRegion():
    select =" destination.code, destination.content, destination.country_code, countries.name"
    where= " destination.country_code = countries.iso2" 
    destinations=selectQuery(select,'destination ,countries',where,'countries.name','DESC')
    resultDes=[]
    for item in destinations:
        data={
            "code":item[0],
            "name":item[1],
            "countryCode":item[2],
            "countryname":item[3]
        }
        resultDes.append(data)
    countries=getCountries()
    facilities=getFacilities()
    currencyInfo=getCurrencyInfo("ZAR")
    result={
        "destination":resultDes,
        "country":countries,
        "facility":facilities,
        "currency":getCurrency(),
        "currencyInfo":currencyInfo
    }
    return result
    
def main():
    result=getCurrencyInfo('CAD')
    print(result)

if __name__ == "__main__":
    main()

