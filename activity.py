import time
import math
import requests
import json
import os
import datetime
from jinja2 import Template
from hashlib import sha256
from dotenv import load_dotenv
from db import insertQuery,insertQueryWithRetValue,selectQuery,updateQuery

load_dotenv()

ACTIVITY_ENV=os.getenv('ACTIVITY_ENV')
HOST_URL=os.getenv('HOST_URL')

if ACTIVITY_ENV=="1":
    API_KEY=os.getenv('ACTIVITY_DEV_KEY')
    SECRET_KEY=os.getenv('ACTIVITY_DEV_SECRET')
    endPoint=os.getenv('TEST_END_POINT')
else:
    API_KEY=os.getenv('ACTIVITY_LIVE_KEY')
    SECRET_KEY=os.getenv('ACTIVITY_LIVE_SECRET')
    endPoint=os.getenv('LIVE_END_POINT')

def getXSignature():
    utcDate= math.floor(time.time())
    assemble=API_KEY+SECRET_KEY+str(utcDate)
    hash=sha256(assemble.encode('utf-8'))
    encryption=hash.hexdigest()
    return encryption


def getAvailActivities(params):
    url=endPoint+"/activity-api/3.0/activities/availability"
    header={
        "Api-key":API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(),
        "Content-Type":"application/json"
    }
    data={
        "filters": [
            {
                "searchFilterItems": [ 
                    {"type": params['type'], "value": params['code']} 
                ]
            }
        ],
        "from": params['from'],
        "to": params['to'],
        "language": "en",
        "paxes": params['paxes'],
        "pagination": {
            "itemsPerPage": params['limit'],
            "page": params['page']
        },
        "order": "DEFAULT"
    }
    result=requests.post(url,headers=header,json=data)
    json_res=json.loads(result.text)
    select=" id, rate"
    where=" id = (select max(id) from tolerance where type = 2)"
    markup=selectQuery(select,'tolerance',where)[0]
    cur_markup={
        "id":markup[0],
        "rate":markup[1]
    }
    total=json_res['pagination']['totalItems']
    data=json_res['activities']
    response={
        "total":total,
        "activities":data,
        "tolerance":cur_markup
    }
    return response

def getActivityDetail(params):
    url=endPoint+"/activity-api/3.0/activities/details/full"
    header={
        "Api-key":API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(),
        "Content-Type":"application/json"
    }
    data={
        "code": params['code'],
        "from": params['from'],
        "to": params['to'],
        "language": "en",
        "paxes": params['paxes']
    }
    res=requests.post(url,headers=header,json=data)
    json_res=json.loads(res.text)
    return json_res['activity']

def searchActivityByHotelCode(params):
    url=endPoint+"/activity-api/3.0/activities/availability"
    header={
        "Api-key":API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(),
        "Content-Type":"application/json"
    }
    data={
        "filters": [
                {
                    "searchFilterItems": [ 
                        {"type": "destination", "value": params['code']}
                    ]
                    
                }
        ],
        "from": params['from'],
        "to": params['to'],
        "language": "en",
        "paxes": params['paxes'],
        "pagination": {
            "itemsPerPage": 8,
            "page": 1
        },
        "order": "DEFAULT"
    }
    res=requests.post(url,headers=header,json=data)
    json_res=json.loads(res.text)
    req={
        "total":json_res['pagination']['totalItems'],
        "activities":json_res['activities']
    }
    return req
    
    

def bookActivity(params):
    url=endPoint+"/activity-api/3.0/bookings"
    header={
        "Api-key":API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(),
        "Content-Type":"application/json"
    }
    data={
        "language":"en",
        "clientReference": "TestedAG",
        "holder":params['holder'],
        "activities":params['activities']
    }
    tolerance=params['tolerance']['id']
    select=" id"
    where=" id = (select max(id) from tolerance where type = 2)"
    curTolerance=selectQuery(select,'tolerance',where)[0][0]
    if tolerance != curTolerance:
        response={
            "status":False,
            "error":"Price was changed Please check availability again"
        }
        failedBookActivity(params['totalAmount'],params['currency'],params['holder'],curTolerance)
        return response
    result=requests.put(url,headers=header,json=data)
    json_res=json.loads(result.text)
    bookingData=json_res.get('booking')
    error=json_res.get('errors')
    if bookingData ==None:
        response={
            "status":False,
            "error":error[0]['text']
        }
        failedBookActivity(params['totalAmount'],params['currency'],params['holder'],curTolerance)
        return response
    else:
        bookingData['paidAmount']=params['totalAmount']
        response={
            "status":True,
            "result":bookingData
        }
        voucher=generateVoucher(bookingData)
        bookingData['voucher']=voucher
        saveBookedActivity(params['holder'],voucher,curTolerance,bookingData)
        return response

def failedBookActivity(totalAmount,currency,markup,holder):
    now=datetime.datetime.now()
    fields=" status, paid_amount, currency, h_surname, h_name, h_email, h_phone, h_country, h_zipcode, h_address, tolerance, create_at, update_at, type"
    values=f" 4, {totalAmount}, '{currency}','{holder['surname']}', '{holder['name']}', '{holder['email']}', '{holder['telephones'][0]}', '{holder['country']}', '{holder['zipCode']}', '{holder['address']}',{markup}, '{now}', '{now}', 2"
    if holder.get('id') !=None:
        fields +=" , h_id"
        values+=f", {holder['id']}"
    insertQuery('activity_book',fields,values)

def getStatusCode(str):
    if str=="CONFIRMED":
        return 1
    else:
        return 0 

def booleanToInt(value):
    if value==True:
        return 1
    else:
        return 0

def saveBookedModality(booking):
    ids=""
    for item in booking:
        fields=" status, reference, a_type, a_code, m_code, o_from, o_to, destination, amount, supply_name, supply_vat, provider_name ,pax, create_at, update_at, a_name, m_name, a_comment "
        paxes=""
        now=datetime.datetime.now()
        for pax in item['paxes']:
            paxes+=pax['name']+" "+pax['surname']+"#"+str(pax['age'])+"*"
        values=f" {getStatusCode(item['status'])}, '{item['activityReference']}', '{item['type']}', '{item['code']}', '{item['modality']['code']}', '{item['dateFrom']}', '{item['dateTo']}', '{item['contactInfo']['country']['destinations'][0]['code']}', '{item['amountDetail']['totalAmount']['amount']}', '{item['supplier']['name']}', '{item['supplier']['vatNumber']}', '{item['providerInformation']['name']}', '{paxes}', '{now}', '{now}' "
        values+=', "'+ item['name']+'" ,"'+item['modality']['name']+'"'
        values+=', "'+ item['comments'][0]['text']+'"'
        if item.get('cancellationPolicies')!=None:
            cPolicy=item['cancellationPolicies'][0]
            fields+=' , c_date, c_amount'
            values+=f" , '{cPolicy['dateFrom']}', '{cPolicy['amount']}'"
        
        id= insertQueryWithRetValue('activity_modality',fields,values)
        ids+=str(id)+","
    size=len(ids)
    ids=ids[0:(size-1)]
    return ids

def getHashCode(params):
    hash=sha256(params.encode('utf-8'))
    return hash.hexdigest()[0:20]

def getPaxInfor(paxes):
    adult=0
    child=0
    age=[]
    for item in paxes:
        if item['paxType'] == 'AD':
            adult+=1
        else:
            child+=1
            age.append(item['age'])
    result={}
    if child == 0:
        result={
            "adult":adult,
            "child":"",
            "childAge":""
        }
    else:
        separator = ", "
        age_str = separator.join([str(element) for element in age])
        result={
            "adult":adult,
            "child":child,
            "childAge":age_str
        }
    return result

def makeActivityData(total):
    result=[]
    for item in total:
        comment=item['comments'][0]['text'].replace('//','<br>')
        comment=comment.replace('\n','<br>')
        c_date=None
        pax=getPaxInfor(item['paxes'])
        if item.get('cancellationPolicies') !=None:
            c_data=item['cancellationPolicies'][0]
            c_date=datetime.datetime.strptime(c_data['dateFrom'].split('T')[0],'%Y-%m-%d') -datetime.timedelta(days=1)
            c_date=c_date.strftime('%Y-%m-%d')
        data={
            **pax,
            "supply":item['supplier'],
            "comment":comment,
            "modality":item['modality']['name'],
            "from":item['dateFrom'],
            "to":item['dateTo'],
            "c_date":c_date,
            "provider":item['providerInformation'],
        }
        result.append(data)
    return result

def generateVoucher(book):
    now=datetime.datetime.now().strftime('%y-%m-%d')
    direcotry="static/voucher/activity/"+getHashCode(str(now)+"+"+book['reference'])+".json"
    fileName="./"+direcotry
    activityData=makeActivityData(book['activities'])
    destination=book['activities'][0]['contactInfo']['country']['destinations'][0]['name']
    params={
        "reference":book['reference'],
        "currency":book['currency'],
        "paidAmount":book['paidAmount'],
        "createAt":book['creationDate'].split('T')[0],
        "holder":book['holder'],
        "name":book['activities'][0]['name'],
        "type":book['activities'][0]['type'],
        "destination":destination,
        "activity":activityData
    }
    with open(fileName,'w+') as f:
        json.dump(params,f)
    return HOST_URL+direcotry


def getActivityVoucher(name):
    fileName='./static/voucher/activity/'+name
    with open(fileName,'r') as f:
        bookData=json.load(f)
    with open('./static/template/activityVoucher.html') as f:
        html_template=Template(f.read())
    holder=bookData['holder']
    html=html_template.render(titel="Acitivty Voucher",host=HOST_URL+"static/template/index.css",reference=bookData['reference'],activityName=bookData['name'],destination=bookData['destination'], currency=bookData['currency'],total=bookData['paidAmount'],createAt=bookData['createAt'],holderName=holder['name']+" "+holder['surname'],activities=bookData['activity'])
    return html


def saveBookedActivity(holder, voucher,tolerance,booking):
    activities=saveBookedModality(booking['activities'])
    paymentData=booking['paymentData']
    pending_amount=booking['pendingAmount']
    paidAmount=booking['paidAmount']
    earn=float(paidAmount-pending_amount) 
    now=datetime.datetime.now()
    fields=" reference, status, type, voucher, pending_amount, total_amount, paid_amount, profit_amount, currency, payment_type ,invoice_company, invoice_number, activities, h_surname, h_name, h_email, h_phone, h_country, h_zipcode, h_address, tolerance, create_at, update_at"
    values=f" '{booking['reference']}', {getStatusCode(booking['status'])}, 1, '{voucher}',{booking['pendingAmount']}, {booking['total']}, {paidAmount},{earn} ,'{booking['currency']}',  '{paymentData['paymentType']['code']}',  '{paymentData['invoicingCompany']['name']}', '{paymentData['invoicingCompany']['registrationNumber']}', '{activities}', '{holder['surname']}', '{holder['name']}', '{holder['email']}', '{holder['telephones'][0]}', '{holder['country']}', '{holder['zipCode']}', '{holder['address']}', {tolerance}, '{now}', '{now}'"
    if holder.get('id') !=None:
        fields +=" , h_id"
        values+=f", {holder['id']}"
    insertQuery('activity_book',fields,values)


def main():
    holder={
        "id":1,
        "surname":"3333",
        "name":"sssdf",
        "email":"dounine423@gmail.com",
        "telephones":['1234567898'],
        "address":"ssss",
        "zipCode":"Ssss",
        "country":"AF"
    }
    

if __name__ == "__main__":
    main()