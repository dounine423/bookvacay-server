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
from region import getCurrencyInfo,getPfPaymentId


load_dotenv()

HOST_URL=os.getenv('HOST_URL')
API_KEY=os.getenv('ACTIVITY_DEV_KEY')
SECRET_KEY=os.getenv('ACTIVITY_DEV_SECRET')
endPoint=os.getenv('TEST_END_POINT')
 
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
    c_currency=params['currency']
    result=requests.post(url,headers=header,json=data)
    json_res=json.loads(result.text)
    total=json_res['pagination']['totalItems']
    billRate=getCurrentBillRate()
    bookRate=getCurrentBookRate()
    currency=getCurrencyInfo(c_currency)
    c_h_rate=float(currency['client']) 
    book_rate=float( bookRate['rate'])
    bill_rate=float( billRate['rate'])
    data=makeActivityListData(json_res['activities'],c_h_rate,book_rate,bill_rate)
    response={
        "total":total,
        "activities":data,
        "currencyInfo":currency
    }
    return response

def makeModalityData(modality,book_rate,bill_rate,c_h_rate):
    result=modality
    for mItem in result:
        for mAmount in mItem['amountsFrom']:
            mAmount['b_amount']=round(mAmount['amount']*(1+book_rate/100)*(1+bill_rate/100),2)
            mAmount['c_amount']=round(mAmount['amount']* (1+book_rate/100)*(1+bill_rate/100)*c_h_rate,2)
        for rate in mItem['rates'][0]['rateDetails']:
            rate['totalAmount']['c_amount']=round(float(rate['totalAmount']['amount'])*(1+book_rate/100)*(1+bill_rate/100)*c_h_rate,2) 
            rate['totalAmount']['b_amount']=round(rate['totalAmount']['amount']*(1+book_rate/100)*(1+bill_rate/100),2)
            for pax in rate['paxAmounts']:
                pax['c_amount']=round(pax['amount'] * (1+book_rate/100)*(1+bill_rate/100)*c_h_rate,2)
                pax['b_amount']=round(pax['amount'] * (1+book_rate/100)*(1+bill_rate/100),2)
               
    return result

def makeActivityListData(activityData,c_h_rate,book_rate,bill_rate):
    result=[]
    for item in activityData:
        data={
            "code":item['code'],
            "name":item['name'],
            "image":getMainImg(item['content']['media']['images'][0]['urls']),
            "description":item['content']['description'],
            "amount":getAmounts(item['amountsFrom'],c_h_rate,book_rate,bill_rate),
        }
        result.append(data)
    return result

def getCurrentBillRate():
    select=" id, rate"
    where=" id = (select max(id) from bank_mark_up )"
    markup=selectQuery(select,'bank_mark_up',where)[0]
    cur_markup={
        "id":markup[0],
        "rate":markup[1]
    }
    return cur_markup

def getAmounts(paxes,c_h_rate,book_rate,bill_rate):
    amounts=paxes
    for item in amounts:
        item['amount']=round(float(item['amount'])*(1+book_rate/100) *(1+bill_rate/100) *c_h_rate,2) 
    return amounts
        
def getCurrentBookRate():
    select=" id, rate"
    where=" id = (select max(id) from book_mark_up where type = 2)"
    markup=selectQuery(select,'book_mark_up',where)[0]
    cur_markup={
        "id":markup[0],
        "rate":markup[1]
    }
    return cur_markup

def getMainImg(urls):
    for item in urls:
        if item['sizeType']=='LARGE':
            return item['resource']

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
    bookRate=getCurrentBookRate()
    billRate=getCurrentBillRate()
    currencyInfo=getCurrencyInfo(params['currency'])
    res=requests.post(url,headers=header,json=data)
    json_res=json.loads(res.text)
    result=json_res['activity']
    result['modalities']=makeModalityData(result['modalities'],float(bookRate['rate']),float(billRate['rate']),float(currencyInfo['client']))
    res={
        "data":result,
        "bookMarkUp":bookRate,
        "billRate":billRate,
        "currencyInfo":currencyInfo
    }
    return res

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
    paymentInfo=params['payment']
    bookMarkUp=getCurrentBookRate()
    bankMarkUp=getCurrentBillRate()
    pf_id=getPfPaymentId(paymentInfo['uuid'])
    paymentInfo['book_mark_up']=bookMarkUp
    paymentInfo['bank_mark_up']=bankMarkUp
    paymentInfo['pf_id']=pf_id
    result=requests.put(url,headers=header,json=data)
    status=result.status_code
    json_res=json.loads(result.text)
    if int(status) >200 :
        error=json_res.get('errors')
        response={
            "success":False,
            "error":error[0]['text']
        }
        failedBookActivity(paymentInfo,params['holder'])
        return response
    else:
        bookingData=json_res.get('booking')
        bookingData['paidAmount']=round(paymentInfo['totalAmount'] *paymentInfo['client'],2) 
        bookingData['currency']=paymentInfo['clientCurrency']
        response={
            "success":True,
            "data":bookingData
        }
        voucher=generateVoucher(bookingData)
        print(voucher)
        bookingData['voucher']=voucher
        saveBookedActivity(params['holder'],bookingData,paymentInfo)
        return response

def failedBookActivity(paymentInfo,holder):
    now=datetime.datetime.utcnow()
    fields=" status, create_at, update_at, type, paid_amount, c_currency, p_currency, h_currency, book_mark_up, bank_mark_up, uuid, pf_id, c_h_rate, z_h_rate, h_surname, h_name, h_email, h_phone, h_country, h_zipcode, h_address"
    values=f" 4, '{now}', '{now}', 0, {paymentInfo['totalAmount']}, '{paymentInfo['clientCurrency']}', 'ZAR', 'USD', {paymentInfo['book_mark_up']['id']}, {paymentInfo['bank_mark_up']['id']}, '{paymentInfo['uuid']}', '{paymentInfo['pf_id']}', {paymentInfo['client']}, {paymentInfo['portal']}, '{holder['surname']}', '{holder['name']}', '{holder['email']}', '{holder['telephones'][0]}', '{holder['country']}', '{holder['zipCode']}', '{holder['address']}'"
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
        now=datetime.datetime.utcnow()
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

def saveBookedActivity(holder,booking,paymentInfo):
    activities=saveBookedModality(booking['activities'])
    paymentData=booking['paymentData']
    totalAmount=booking['total']
    paidAmount=paymentInfo['totalAmount']
    profit=float(paidAmount-totalAmount)
    now=datetime.datetime.utcnow()
    fields=" create_at, type, reference, status, paid_amount, total_amount, profit_amount,c_currency, h_currency, p_currency, payment_type, invoice_company, invoice_number, book_mark_up, uuid, pf_id, bank_mark_up, c_h_rate, z_h_rate, rate_update_at, activities,voucher, h_surname, h_name, h_email, h_phone, h_country, h_zipcode, h_address, update_at"
    values=f" '{now}', 1, '{booking['reference']}', {getStatusCode(booking['status'])}, {paymentInfo['totalAmount']}, {totalAmount}, {profit}, '{paymentInfo['clientCurrency']}', 'USD', 'ZAR', '{paymentData['paymentType']['code']}', '{paymentData['invoicingCompany']['name']}', '{paymentData['invoicingCompany']['registrationNumber']}', {paymentInfo['book_mark_up']['id']}, '{paymentInfo['uuid']}', '{paymentInfo['pf_id']}', {paymentInfo['bank_mark_up']['id']}, {paymentInfo['client']}, {paymentInfo['portal']}, '{paymentInfo['update']}', '{activities}', '{booking['voucher']}', '{holder['surname']}', '{holder['name']}', '{holder['email']}', '{holder['telephones'][0]}', '{holder['country']}', '{holder['zipCode']}', '{holder['address']}', '{now}'"
    if holder.get('id') !=None:
        fields +=" , h_id"
        values+=f", {holder['id']}"
    insertQuery('activity_book',fields,values)


def main():
    print("ss")

if __name__ == "__main__":
    main()