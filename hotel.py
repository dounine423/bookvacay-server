import urllib.parse as urlparse
import time
import math
import requests
import json
import os
import copy
import datetime
from urllib.parse import urlencode
from hashlib import sha256
from dotenv import load_dotenv
from jinja2 import Template
from db import getAllDataFromDB ,insertQuery ,insertQueryWithRetValue,selectQuery

load_dotenv()

FAST_END_POINT=os.getenv('FAST_END_POINT')
FAST_API_KEY=os.getenv('FAST_API_KEY')
HOTEL_ENV=os.getenv('HOTEL_ENV')
HOST_URL=os.getenv('HOST_URL')
SECRET_KEY=""
API_KEY=""

if HOTEL_ENV=="1":
    API_KEY=os.getenv('HOTEL_DEV_KEY')
    SECRET_KEY=os.getenv('HOTEL_DEV_SECRET')
    endPoint=os.getenv('TEST_END_POINT')
else:
    API_KEY=os.getenv('HOTEL_LIVE_KEY')
    SECRET_KEY=os.getenv('HOTEL_LIVE_SECRET')
    endPoint=os.getenv('LIVE_END_POINT')

def getHashCode(params):
    hash=sha256(params.encode('utf-8'))
    return hash.hexdigest()[0:20]

def getXSignature():
    utcDate= math.floor(time.time())
    assemble=API_KEY+SECRET_KEY+str(utcDate)
    hash=sha256(assemble.encode('utf-8'))
    encryption=hash.hexdigest()
    return encryption

def getHotelContent(hotelCodes='1524,54909'):
    url=endPoint+"/hotel-content-api/1.0/hotels"
    params={"fields":"all","language":"ENG","useSecondaryLanguage":"false","codes":hotelCodes}
    url_parts = list(urlparse.urlparse(url))
    query= dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    params_url=urlparse.urlunparse(url_parts) 
    header={
        "Api-key":API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(),
        "Accept-Encoding":"gzip"
    }
    codes=hotelCodes.split(',')
    codes.pop()
    result= requests.get(params_url,headers=header)
    json_res=json.loads(result.text)['hotels']
    ret_result=[]
    for code in codes:
        item=find(json_res,int(code))
        parse_item=getHotelDataFromReq(item)
        ret_result.append(parse_item)
    return ret_result
    
def getHotelAvailability(params=None):
    currencyInfo=getCurrency(params['currency'])
    url=endPoint+"/hotel-api/1.0/hotels"
    header={
        "Api-key":API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(),
        "Accept-Encoding":"gzip",
        "Content-Type":"application/json"
    }
    type=params['type']
    code=params['code']
    hotelCodes=getHotelCodes(type,code,params['facility'])
    data={
        "stay":{
            "checkIn":params['inDate'],
            "checkOut":params['outDate']
        },
        "occupancies":[
            {
                "rooms":params['rooms'],
                "adults":params['adults'],
                "children":params['children'],
                "paxes":params['paxes']
            }
        ],
        "hotels": {
            "hotel": hotelCodes
        },
        "reviews": [
            {
                "type": "TRIPADVISOR",
                "maxRate": 5,
                "minRate": 1,
                "minReviewCount": 1
            }
        ]
    }
    if params.get('boards')!=None:
        data['boards']=params.get('boards')
    if params.get('filter')!=None:
        data['filter']=params.get('filter')
    result=requests.post(url, headers=header,json=data)
    json_res=json.loads(result.text)               
    total=json_res['hotels']['total']
   
    select=" id, rate"
    where=" id = (select max(id) from book_mark_up where type = 1) "
    hotel_mark_temp =selectQuery(select,'book_mark_up',where)
    hotel_mark_up={
        "id":hotel_mark_temp[0][0],
        "rate":hotel_mark_temp[0][1]
    }
    where=" id = (select max(id) from bank_mark_up )"
    bank_mark_temp=selectQuery(select,'bank_mark_up',where)
    bank_mark_up={
        "id":bank_mark_temp[0][0],
        "rate":bank_mark_temp[0][1]
    }
    hotels=getAllotment(json_res['hotels']['hotels'],float(hotel_mark_up['rate']),float(bank_mark_up['rate']), currencyInfo)
    response={
        "total":total,
        "hotel_mark_up":hotel_mark_up,
        "bank_mark_up":bank_mark_up,
        "currencyInfo":currencyInfo,
        "hotels":hotels
    }
    return response

def getCurrency(params):
    select="rate"
    where=" id = (select max(id) from bank_mark_up )"
    bank_mark_up=selectQuery(select,'bank_mark_up',where)[0][0]
    clientC=params
    hotelC="EUR"
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

def getCommentsById(commentId,checkIn):
    url=endPoint+"/hotel-content-api/1.0/types/ratecommentdetails?"
    header={
        "Api-key":API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(),
        "Accept-Encoding":"gzip"
    }
    params={"fields":"all","language":"ENG","useSecondaryLanguage":"False","code":commentId,"date":checkIn}
    param_str=""
    for item in params:
        param_str+=f"{item}={params[item]}&"
    param_str=param_str[0:(len(param_str)-1)]
    url+=param_str
    res=requests.get(url,headers=header)
    status=res.status_code
    json_res=json.loads(res.text)
    if int(status) ==200:
        json_res=json.loads(res.text)
        comment=json_res['rateComments'][0]['description']
        return comment
    else:
        return None

def getRoomRateComment(params):
    commentIds=params['ids']
    checkIn=params['checkIn']
    result=[]
    for item in commentIds:
        commentId= item.replace('|','%7C')
        comment=getCommentsById(commentId,checkIn)
        result.append(comment)
    return result

def getChangedRateKey(params):
    availParams={
        "adults":params['adults'],
        "children":params['children'],
        "paxes":params['paxes'],
        'inDate':params['inDate'],
        "outDate":params['outDate'],
        'hotelCode':params['code']        
    }
    for item in params['reserveData']:
        if item['rooms'] != item['roomCnt']:
            availParams['rooms']=item['roomCnt']
            availParams['roomCode']=item['roomCode']
            oldRateKey=item['rateKey'].split('||')[0]
            oldNet=float(item['net']) /int(item['roomCnt'])   
            updateRateKey=changeRateKey(availParams,oldRateKey,oldNet)
            item['rateKey']=updateRateKey
    return params

def changeRateKey(params,rateKey,net):
    url=endPoint+"/hotel-api/1.0/hotels"
    header={
        "Api-key":API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(),
        "Accept-Encoding":"gzip",
        "Content-Type":"application/json"
    }
    data={
        "stay":{
            "checkIn":params['inDate'],
            "checkOut":params['outDate']
        },
        "occupancies":[
            {
                "rooms":params['rooms'],
                "adults":params['adults'],
                "children":params['children'],
                "paxes":params['paxes']
            }
        ],
        "hotels": {
        "hotel": [
                params['hotelCode']
            ]
        },
        "rooms": {
            "room":  [
                params['roomCode']
            ]
        }
    }
    result=requests.post(url, headers=header,json=data)
    json_res=json.loads(result.text)
    ratesInfo=json_res['hotels']['hotels'][0]['rooms'][0]['rates']
    shortlist=[]
    for item in ratesInfo:
        if item['rateKey'].split('||')[0]==rateKey:
            shortlist.append(item)
            item['diffNet']=abs(net-float(item['net']) / int(item['rooms'])) 
    index=0
    diff=shortlist[0]['diffNet']
    count=0
    for item in shortlist:
        if item['diffNet']< diff:
            diff=item['diffNet']
            index=count
        count+=1
    return shortlist[index]['rateKey']
  
def checkRateKey(params):
    url=endPoint+"/hotel-api/1.0/checkrates"
    header={
        "Api-key":API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(),
        "Accept-Encoding":"gzip",
        "Content-Type":"application/json"
    }
    data={
        "rooms": params['rooms']
    }
    result=requests.post(url, headers=header,json=data)
  
    json_res=json.loads(result.text)
    if json_res.get('hotel')!=None:
        return True
    else:
        return False
    
def bookHotel(params):
    url=endPoint+"/hotel-api/1.0/bookings"
    header={
        "Api-key":API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(),
        "Accept-Encoding":"gzip",
        "Content-Type":"application/json"
    }
    req={
        "holder":params['holder'],
        "rooms":params['rooms'],
        "clientReference": "IntegrationAgency",
        "remark": "Booking remarks are to be written here."
    }
    select=" id"
    where=" id = (select max(id) from book_mark_up where type = 1)"
    paymentInfo=params['payment']
    hotel_mark_up=selectQuery(select,'book_mark_up',where)[0][0]
    where=" id = (select max(id) from bank_mark_up )"
    bank_mark_up=selectQuery(select,'bank_mark_up',where)[0][0]
    if hotel_mark_up != paymentInfo['hotel_mark_up']['id']:
        failedBookingHandler(params['bookInfo'], params['holder'], paymentInfo)
        res={
            "success":False,
            "error":"Price was changed Please check availability again"
        }
        return res
    if bank_mark_up != paymentInfo['bank_mark_up']['id']:
        failedBookingHandler(params['bookInfo'], params['holder'], paymentInfo)
        res={
            "success":False,
            "error":"Price was changed Please check availability again"
        }
        return res
    result=requests.post(url, headers=header,json=req)
    status=result.status_code
    if int(status) >= 400:
        failedBookingHandler(params['bookInfo'], params['holder'], paymentInfo)
        json_res=json.loads(result.text)
        errorMsg="Something went wrong on server."
        error= json_res.get('error')
        if error!=None:
            errorMsg=error['message']
        res={
            "success":False,
            "error":errorMsg
        }
        return res
    # generate Voucher
    bookingData=json.loads(result.text)['booking']
    voucher= generateVoucherToJson(bookingData,params['bookInfo'],params['holder'],paymentInfo)
    # save book data to database
    saveBookedHotel(params['holder'],bookingData, paymentInfo,voucher)
    bookingData['voucher']=voucher
    bookingData['c_currency']=paymentInfo['clientCurrency']
    res={
        "success":True,
        "data":bookingData
    }
    return res

def parseRateComment(comments):
    texts=comments.split('.')
    result=""
    for item in texts:
        if item.strip() !='':
            result+=item+"<br>"
    return result

def makeRateData(rate):
    board=rate['boardName']
    c_date=None
    if rate['boardCode'] =='HB':
        board="Breakfast & dinner included"
    if rate['boardCode'] == 'FB':
        board="Breakfast, lunch & dinner included"
    if rate.get('cancellationPolicies') !=None:
        cPolicy=rate['cancellationPolicies'][0]
        c_date=cPolicy['from'].split('T')[0]
    if rate.get('rateComments') !=None:
        comments=parseRateComment(rate['rateComments'])
    data={
        "board":board,
        "c_date":c_date,
        "comments":comments,
        "rooms":rate['rooms'],
        "adult":rate['adults'],
        "child":rate['children']
    }
    return data   

def generateVoucherToJson(bookInfo,params,holder,paymentInfo):
    now=datetime.datetime.now().strftime('%y-%m-%d')
    direcotry="static/voucher/hotel/"+getHashCode(str(now)+"+"+bookInfo['reference'])+".json"
    fileName="./"+direcotry
    roomData=[]
    index=0
    currencyInfo=paymentInfo['currencyInfo']
    paid_amount=paymentInfo['totalAmount']*(1+paymentInfo['bank_mark_up']['rate']/100)*currencyInfo['client']
    paid_amount=round(paid_amount,2)
    for item in bookInfo['hotel']['rooms']:
        bookRoom=makeRateData(item['rates'][0])
        chAges=""
        for child in params['paxes']:
            chAges+=str(child['age']) +", "
        size=len(chAges)
        chAges=chAges[0:(size-2)]
        child=bookRoom['child']
        if int(bookRoom['child'])  ==0:
            bookRoom['child']=""
        data={
            **bookRoom,
            "name":item['name'],
            "paxes":params['reserveData'][index]['guest'],
            "facility":params['reserveData'][index]['facility'],
            "chAges":chAges,
            "child":child
        }
        roomData.append(data)
        index+=1
    voucher={
        "holder":holder,
        "name":params['name'],
        "category":params['category'],
        "address":params['address'],
        "accommodation":params['accommodation'],
        "phones":params['phones'],
        "aduts":params['adults'],
        "child":params['children'],
        "inDate":params['inDate'],
        "outDate":params['outDate'],
        "amount":paid_amount,
        "currency":paymentInfo['clientCurrency'],
        "facility":params['extra'],
        "reference":bookInfo['reference'],
        "createAt":bookInfo['creationDate'],
        "supply":bookInfo['hotel']['supplier'],
        "invoice":bookInfo['invoiceCompany'],
        "rooms":roomData,
    }
    with open(fileName,'w+') as f:
        json.dump(voucher,f)
    return HOST_URL+direcotry

def failedBookingHandler(params, holder,paymentInfo):
    currencyInfo=paymentInfo['currencyInfo']
    now=datetime.datetime.now()
    fields='type, create_at, status, h_code, indate, outdate, paid_amount, h_currency, c_currency, p_currency ,update_at, hotel_mark_up, bank_mark_up, uuid, c_h_rate, z_h_rate, rate_update_at'
    values=f" 0 ,'{now}', 4, '{params['code']}', '{params['inDate']}','{params['outDate']}' ,{paymentInfo['totalAmount']}, '{params['currency']}' ,'{paymentInfo['clientCurrency']}', 'ZAR','{now}', {paymentInfo['hotel_mark_up']['id']} , {paymentInfo['bank_mark_up']['id']} ,'{paymentInfo['uuid']}', {currencyInfo['client']}, {currencyInfo['portal']}, '{currencyInfo['update']}'"
    fields+=' , hd_surname, hd_name, hd_email, hd_phone'
    values+=f" , '{holder['name']}', '{holder['surname']}' , '{holder['email']}' , '{holder['phone']}'"
    holder_id=holder.get('id')
    if holder_id !=None:
        fields+=' , hd_id'
        values+=f", {holder_id}"    
    insertQuery('hotel_book',fields,values)

def changeBoolean(value):
    if value==True:
        return 1
    else:
        return 0

def saveBookedHotel(holder,booking, paymentInfo,voucher):
    currencyInfo=paymentInfo['currencyInfo']
    room_data=saveBookedRoom(booking['hotel']['rooms'],booking['reference'])
    room_ids=room_data['roomIds']
    totalAmount=0
    if booking.get('totalSellingRate') !=None:
        totalAmount=booking['totalSellingRate']
    else:
        totalAmount=booking['totalNet']
    profit=paymentInfo['totalAmount']-(totalAmount) 
    now=datetime.datetime.now()
    formatTime=now.strftime('%Y-%m-%d %H:%M:%S')
    fields=' reference, cancellation, modification, type, voucher, create_at, status, h_code, indate, outdate, room_data, pending_amount, net_amount, paid_amount,  profit_amount,h_currency, invoice_company, invoice_number,update_at, hotel_mark_up, supply_name, supply_ref, uuid,c_h_rate, z_h_rate, rate_update_at, bank_mark_up, c_currency, p_currency'
    values=f" '{booking['reference']}', {changeBoolean( booking['modificationPolicies']['cancellation'])}, {changeBoolean(booking['modificationPolicies']['modification']) },1 , '{voucher}', '{now}', {getStatus(booking['status'])}, '{booking['hotel']['code']}', '{booking['hotel']['checkIn']}', '{booking['hotel']['checkOut']}', '{room_ids}',{booking['pendingAmount']} ,{totalAmount}, {paymentInfo['totalAmount']}, {profit},'{booking['currency']}', '{booking['invoiceCompany']['company']}', '{booking['invoiceCompany']['registrationNumber']}', '{formatTime}', {paymentInfo['hotel_mark_up']['id']}, '{booking['hotel']['supplier']['name']}', '{booking['hotel']['supplier']['vatNumber']}', '{paymentInfo['uuid']}',{currencyInfo['client']}, {currencyInfo['portal']}, '{currencyInfo['update']}', {paymentInfo['bank_mark_up']['id']}, '{paymentInfo['clientCurrency']}', 'ZAR'"
    fields+=' , hd_surname, hd_name, hd_email, hd_phone'
    values+=f" , '{holder['name']}', '{holder['surname']}' , '{holder['email']}' , '{holder['phone']}'"
    holder_id=holder.get('id')
    if holder_id !=None:
        fields+=' , hd_id'
        values+=f", {holder_id}" 
    insertQuery('hotel_book',fields,values)
    
def getStatus(str):
    if str=='CONFIRMED':
        return 1
    if str=='CANCELLED':
        return 2
    if str=='COMPLETED':
        return 3
    if str == 'PROCESSING':
        return 4
    else:
        return 0

def saveBookedRoom(roomData,bookingId):
    values=' '
    room_ids=""
    total_amount=0
    for room in roomData:
        tax=0
        net=0
        total=0
        now=datetime.datetime.now()
        formatTime=now.strftime('%Y-%m-%d %H:%M:%S')
        curRate=room['rates'][0]
        net=float(curRate['net']) 
        hotelMandatory=curRate.get('hotelMandatory')
        if hotelMandatory==True:
            total=float(curRate['sellingRate']) 
            if curRate.get('taxes') !=None:
                tax=float(curRate['taxes']['taxes'][0]['amount'])
        else:
            total=net
            if curRate.get('taxes') !=None:
                tax=float(curRate['taxes']['taxes'][0]['amount']) 
                if curRate['taxes']['allIncluded']==False:
                    total+=tax
        total_amount+=total
        fields=' reference, status, r_name, r_code, r_count, payment_type, adult, child,create_at ,update_at, net ,tax, total'
        values = f" '{bookingId}', {getStatus(room['status'])}, '{room['name']}', '{room['code']}', {curRate['rooms']}, '{curRate['paymentType']}', {curRate['adults']}, {curRate['children']}, '{formatTime}', '{formatTime}', {net}, {tax}, {total}"
        if curRate.get('cancellationPolicies') !=None:
            fields+=" , c_date, c_amount "
            values+=f" , '{curRate['cancellationPolicies'][0]['from']}', '{curRate['cancellationPolicies'][0]['amount']}'"
        result= insertQueryWithRetValue('hotel_room',fields,values)
        room_ids+=str(result) +","
    size=len(room_ids)
    retValue={
        "roomIds":room_ids[0:(size-1)],
        "total":total_amount
    }
    return retValue

def getAllotment(hotelsAvail,hotel_mark_up,bank_mark_up,currencyInfo):
    temp=hotelsAvail
    index=0
    minRate=0
    for hotel in  hotelsAvail:
        availRooms=0
        minRate=getRoomRatePrice(hotel['rooms'][0]['rates'][0],hotel['currency'])
        for rooms in hotel['rooms']:
            for rate in rooms['rates']:
                purePrice=getRoomRatePrice(rate,hotel['currency'])
                hotelPrice=round(purePrice*(1+hotel_mark_up/100),2)
                portalPrice=round(hotelPrice*(1+bank_mark_up/100)*currencyInfo['portal'],2)
                clientPrice=round(hotelPrice*(1+bank_mark_up/100)*currencyInfo['client'],2)
                rate['hotelPrice']=hotelPrice
                rate['purePrice']=round(purePrice,2) 
                rate['portalPrice']=portalPrice
                rate['clientPrice']=clientPrice
                if rate.get('taxes') !=None:
                    pureTax=getRoomTaxes(rate.get('taxes'),hotel['currency'])
                    clientTax=round(pureTax*currencyInfo['client'],2)
                    rate['pureTax']=pureTax
                    rate['clientTax']=clientTax
                if minRate>purePrice:
                    minRate=purePrice
                availRooms+=rate['allotment']
        hotel['allotment']=availRooms
        hotel['minRate']=round(minRate*(1+hotel_mark_up/100)*(1+bank_mark_up/100)*currencyInfo['client'],2) 
        index+=1
    return temp

def getRoomTaxes(taxInfo,currency):
    taxCurrency=taxInfo['taxes'][0]['currency']
    if taxCurrency!=currency:
        tax=taxInfo['taxes'][0]['clientAmount']
    else:
        tax=taxInfo['taxes'][0]['amount']
    return round(float(tax),2) 

def getRoomRatePrice(rate,currency):
    flag=rate.get('hotelMandatory')
    net=rate.get('net')
    taxInfo=rate.get('taxes')
    sellingRate=rate.get('sellingRate')
    if flag ==True:
        return float(sellingRate) 
    else:
        if taxInfo !=None:
            taxCurrency=taxInfo['taxes'][0]['currency']
            tax=0
            if taxCurrency  != currency:
                tax=taxInfo['taxes'][0]['clientAmount']
            else:
                tax=taxInfo['taxes'][0]['amount']
            taxFlag=taxInfo.get('allIncluded')
            if taxFlag ==True:
                return net
            else:
                return float(net) +float(tax)
        else:
            return float(net) 

def getHotelDataFromReq(hotel):
    code=hotel.get('code')
    name=hotel['name']['content']
    description=hotel['description']['content']
    coordinates=hotel.get('coordinates')
    accommodation=None
    category=None
    groupCategory=None
    boards=None
    address=hotel['address']['content']
    phones=hotel.get('phones')
    segments=None
    facilities=None
    ranking=hotel.get('ranking')
    images=None
    city=hotel.get('city')['content']
    cityDistance=None
    roomData=[]
    interestPoints=None
    terminals=None
    issues=None
    webUrl=None
    accommodation=None
    facilities=None
    if hotel.get('web') !=None and hotel.get('web').find('http')==-1:
        webUrl="https://"+hotel.get('web')
    if hotel.get('categoryCode')!= None:
        category=getCategoryFromHotol(hotel.get('categoryCode'))
    if hotel.get('categoryGroupCode') !=None:
        groupCategory=getGroupCategoryFromHotel(hotel.get('categoryGroupCode'))
    if hotel.get('boardCodes') != None:
        boards= getBoardFromHotel(hotel.get('boardCodes'))
    # if hotel.get('segmentCodes') !=None:
    #     segments=getSegmentFromHotel(hotel.get('segmentCodes'))
    if hotel.get('interestPoints') != None:
        interestPoints=hotel.get('interestPoints')
    if hotel.get('terminals') != None:
        terminals= getTerminals(hotel.get('terminals'))
    if hotel.get('issues') !=None:
        issues=getIssue(hotel.get('issues') )
    for room in hotel.get('rooms'):
        roomFacilities=None
        roomStays=None
        if room.get('roomFacilities')!=None:
            roomFacilities=getRoomFacility(room.get('roomFacilities'))
        if room.get('roomStays')!=None:
            roomStays=getRoomStays(room['roomStays'])
        data={
            **room,
            "roomFacilities":roomFacilities,
            "roomStays":roomStays
        }
        roomData.append(data)
    if hotel.get('accommodationTypeCode')!=None:
         accommodation=getAccommodation(hotel.get('accommodationTypeCode'))
    if hotel.get('facilities') !=None:
        facilities=getHotelFacilities(hotel.get('facilities'))
        cityDistance=getCityDistance(facilities[0])
    if hotel.get('images')!=None:
        images=hotel.get('images')
    hotelData={
        "code":code,
        "name":name,
        "accommodation":accommodation,
        "description":description,
        "coordinates":coordinates,
        "category":category,
        "groupCategory":groupCategory,
        "boards":boards,
        "phones":phones,
        "address":address,
        "segments":segments,
        "facilities":facilities,
        "ranking":ranking,
        "images":images,
        "city":city,
        "cityDistance":cityDistance,
        "roomData":roomData,
        "interestPoints":interestPoints,
        "terminals":terminals,
        "issues":issues,
        "webUrl":webUrl
    }
    return hotelData

def getAccommodation(code):
    select=" content"
    where=f" code ='{code}'"
    result=selectQuery(select,'accommodation',where)
    return result[0][0]

def getCategoryFromHotol(code):
    select=" simpleCode" 
    where=f" code  = '{code}'"
    result=selectQuery(select,'category',where)
    return result[0][0]

def getRoomFacility(facilities):
    temp=bubbleSort(facilities)
    select=" A.content"
    table_from=" (select * from facility where facilityGroupCode = 60 order by code ) A"
    where=f" code = '{temp[0]['facilityCode']}'"
    index=0
    for item in temp:
        where+=f" or code ='{item['facilityCode']}'"
    result=selectQuery(select,table_from,where)
    for item in result:
        temp[index]['name']=item[0]
        index+=1
    return temp

def findFacility(facilityList,groupCode,code):
    index=0
    for item in facilityList:
        if item['facilityGroupCode']== groupCode and item['facilityCode'] == code:
            facilityList.pop(index)
            data={
                "list":facilityList,
                "item":item
            }
            return data
        index+=1
        
def getIssue(issues):
    result=[]
    select=" description , type"
    where=f" code = '{issues[0]['issueCode']}'"
    for issue in issues:
        where+=f" or code = '{issue['issueCode']}' "
    queryResult=selectQuery(select,'issue',where)
    for item in queryResult:
        data={
            "type":item[1],
            "content":item[0],
            **issue
        }
        result.append(data)
    return result

def getRoomStays(facilities):
    result=[]
    roomFacilities=[]
    index=0
    query="select content,facilityGroupCode ,code from  facility where "
    for facility in facilities:
        stayFacilities= facility.get('roomStayFacilities')
        if stayFacilities!=None and facility.get('stayType') =='BED':
            for stayFacility in stayFacilities:
                roomFacilities.append(stayFacility)
    if len(roomFacilities)==0:
        return None

    for item in roomFacilities:
        query+=f" facilityGroupCode = '{item['facilityGroupCode']}' and code = '{item['facilityCode']}' or"
    size=len(query)
    query=query[0:(size-3)]
    bedFacility=getAllDataFromDB(query)
    for item in bedFacility:
        findResult=findFacility(roomFacilities,item[1],item[2])
        facility=findResult['item']
        roomFacilities=findResult['list']
        data={
            "img":(str(item[2])+"-"+ str(item[1])),
            "content":item[0],
            "number":facility['number'],
        }
        result.append(data)
        index+=1
    return result

def getTerminals(terminals):
    temp=copy.copy(terminals)
    airport=[]
    harbour=[]
    railway=[]
    select=" code, name, description"
    where=f" code = '{terminals[0]['terminalCode']}'"
    for terminal in terminals:
        where+=f" or code = '{terminal['terminalCode']}'  "
    terminalResult=selectQuery(select,'terminal',where)
    for item in terminalResult:
        if item[2] == 'Airport':
           temp= makeTerminalData(temp,airport,item)
        if item[2]== 'Harbour':
           temp= makeTerminalData(temp,harbour,item)
        if item[2]== 'Railway station':
           temp= makeTerminalData(temp,railway,item)
    data={
        "airport":airport,
        "harbour":harbour,
        "railway":railway
    }
    return data 

def makeTerminalData(terminalList,currentList,item):
    temp=terminalList
    findResult=findTerminal(temp,item[0])
    terminal=findResult['item']
    data={
        "content":item[1],
        "distance":terminal['distance']
    }
    currentList.append(data)
    return temp

def findTerminal(terminalList,code):
    index=0
    for item in terminalList:
        if item['terminalCode'] ==code:
           newList= terminalList.pop(index)
           terminal=item
           data={
               "list":newList,
               "item":terminal
           }
           return data
        index+=1

def getGroupCategoryFromHotel(code):
    select=" description"
    where=f" code = '{code}'"
    result=selectQuery(select,'groupcategory',where)
    return result[0][0]

def getBoardFromHotel(codes):
    select="content"
    where=f" code ='{codes[0]}'"
    board=[]
    for code in codes:
        where+=f" or code = '{code}' "
    result=selectQuery(select,'board',where)
    for item in result:
        board.append(item[0])
    return board

def getSegmentFromHotel(codes):
    select=" content"
    where=f" code = '{codes[0]}'"
    segments=[]
    for code in codes:
        where+=f" or code = '{code}' "
    result=selectQuery(select,'segment',where)
    for item in result:
        segments.append(item[0])
    return segments

def find(elements,ele):
    for item in elements:
        if item['code']==ele:
            return item

def getHotelFacilities(facilities=None):
    temp=copy.copy(facilities)
    select=" code ,content"
    where=" code != 10 and code != 100 and code != 20"
    groupCodes=selectQuery(select,'facilitygroup',where)
    tempTotal=[]
    total=[]
    facts=[]
    checkout=[]
    facility=[]
    roomFacility=[]
    payable=[]
    for group in groupCodes:
        item=findHotelFacility(temp,group[0])
        if len(item)>0:
            data={
                "code":group[0],
                "name":group[1],
                "data":item
            }
            tempTotal.append(data)
       
    for item in tempTotal:
        select=" A.content ,A.code"
        table_from=f" (select * from facility where facilityGroupCode = {item['code']}) A"
        where= " A.code = "+str(item['data'][0]['facilityCode']) 
        fIndex=0
        for fItem in item['data']:
            where+=f" or A.code = {str(fItem['facilityCode'])}"
        result=selectQuery(select,table_from,where,'A.code')
        for rItem in result:
            item['data'][fIndex]['name']=rItem[0]
            fIndex+=1
        data={
            **item
        }
        if data['code']==70:
            for fItem in data['data']:
                if fItem['facilityCode']==260 or fItem['facilityCode']==390:
                    checkout.append(fItem)  
                # elif fItem.get('indFee') ==True:
                #     payable.append(fItem)
                #     facility.append(fItem)
                else:
                    facility.append(fItem)
        if int(data['code']) ==60:
            for rItem in data['data']:
                if rItem.get('indFee') == True:
                    payable.append(rItem)
                roomFacility.append(rItem)
        elif int(data['code']) ==30:
            factItem={
                "code":30,
                "name":"Accepted Payment methods",
                "icon":"payment",
                "data":item['data']
            }
            facts.append(factItem)
        elif int(data['code']) ==40:
            factItem={
                "code":40,
                "name":"Getting Around",
                "icon":"icon-location-pin",
                "data":item['data']
            }
            facts.append(factItem)
        else:
            total.append(data)
    hotelFacility={
        "code":70,
        "name":"Facility",
        "data":facility
    }
    # total.append(hotelFacility)
    # factItem={
    #     "code":70,
    #     "name":"Extra",
    #     "icon":"icon-ticket",
    #     "data":payable
    # }
    # facts.append(factItem)
    factItem={
        "code":0,
        "name":"Check-in/ Check-out",
        "icon":"icon-calendar   ",
        "data":checkout
    }
    facts.append(factItem)
    roomStandard={
        "code":60,
        "name":"Room Facilities",
        "data":roomFacility
    }
    total.insert(0,facts)
    total.append(roomStandard)
    return total

def findHotelFacility(facilityList,code):
    sameGroup=[]
    index=0
    for item in facilityList:
        if int(item['facilityGroupCode']) == int(code):
            sameGroup.append(item)
        index+=1
    if len(sameGroup)>0:
        result=bubbleSort(sameGroup)
        return result
    else:
        return sameGroup

def bubbleSort(arr):
    n=len(arr)
    for i in range(n):
        swapped=False
        for j in range(0,n-i-1):
            if arr[j]['facilityCode']>arr[j+1]['facilityCode']:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped=True
        if swapped==False:
            break
    return arr

def deg2rad(deg):
    return deg* math.pi/180

def rad2deg(rad):
    return rad*180/math.pi

def calculateBetweenTwoPoints(lat1,lng1,lat2,lng2):
    pointsDiff=lng1-lng2
    toSin=(math.sin((deg2rad(lat1))) *math.sin(deg2rad(lat2)))+(math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2))* math.cos(deg2rad(pointsDiff)))
    toAcos = math.acos(toSin)
    toRad2Deg = rad2deg(toAcos)
    toMiles  =  toRad2Deg * 60 * 1.1515
    toKilometers = toMiles * 1.609344
    toNauticalMiles = toMiles * 0.8684
    toMeters = toKilometers * 1000
    toFeets = toMiles * 5280
    toYards = toFeets / 3
    return round(toKilometers,1)

def getHotelCodes(type,code,facility):
    if type==1:
        where=f" destination='{code}'"
        for group in facility:
            for item in group['facility']:
                where+=f" and JSON_SEARCH({group['column']}, 'all', '{item}' ) IS NOT NULL "
        hotels=selectQuery(" code ",'hotel_list',where)
        codes=[]
        for item in hotels:
            codes.append(item[0])
        return codes 
    else:
        codes=[]
        select=" * "
        where =f" code ='{code}'"
        hotel=selectQuery(select,'hotel_list',where)
        hotel_id=hotel[0][0]
        hotel_code=code
        hotel_lat=hotel[0][3]
        hotel_lng=hotel[0][4]
        hotel_des=hotel[0][5]
        select=" code, lat, lng"
        where=f" type = 0 "
        for group in facility:
            for item in group['facility']:
                where+=f" and JSON_SEARCH({group['column']}, 'all', '{item}' ) IS NOT NULL "
        hotels=selectQuery(select,'hotel_list',where)
        for item in hotels:
            if calculateBetweenTwoPoints(hotel_lat,hotel_lng,item[1],item[2]) <101:
                codes.append(item[0])
        # codes.insert(0,hotel_code)
        return codes

def getFilteredCode(params):
    result=[]
    index=params['index']
    select=" A.code ,A.name, A.type, B.name"
    table_from=f" (select * from hotel_list where name like '%{index}%' order by type DESC limit 5) A, countries B "
    where=" A.destination =B.iso2"
    destination=selectQuery(select,table_from,where)
    for item in destination:
        data={
            "code":item[0],
            "name":item[1],
            "type":item[2],
            "content":item[3]
        }
        result.append(data)
    select=" A.code ,A.name, A.type ,B.content"
    table_from=f" (select * from hotel_list where name like '%{index}%' order by type DESC limit 5) A, destination B"
    where=" A.destination = B.code"
    hotels=selectQuery(select,table_from,where)
    for item in hotels:
        data={
            "code":item[0],
            "name":item[1],
            "type":item[2],
            "content":item[3]
        }
        result.append(data)
    return result

def getCityDistance(params):
    for item1 in params:
        if item1['code']==40:
            for item2 in item1['data']:
                if item2['facilityCode']==10:
                    return item2
    return None

def getHotelVoucher(name):
    fileName='./static/voucher/hotel/'+name
    with open(fileName,'r') as f:
        bookData=json.load(f)
    with open('./static/template/hotelVoucher.html') as f:
        html_template=Template(f.read())
    diff=datetime.datetime.strptime(bookData['outDate'],'%Y-%m-%d') -datetime.datetime.strptime(bookData['inDate'],'%Y-%m-%d')
    html=html_template.render(host= HOST_URL+"static/template/index.css",title="Voucher",reference=bookData['reference'], supplyName=bookData['supply']['name'],supplyVat=bookData['supply']['vatNumber'],company=bookData['invoice']['company'],regNumber=bookData['invoice']['registrationNumber'],roomData=bookData['rooms'],phones=bookData['phones'],extra=bookData['facility'],accommodation=bookData['accommodation'],name=bookData['name'],address=bookData['address'],category=bookData['category'],inDate=bookData['inDate'],outDate=bookData['outDate'],diff=diff.days,amount=bookData['amount'],currency=bookData['currency'],createAt=bookData['createAt'],holderName=bookData['holder']['name']+" "+bookData['holder']['surname'])
    return html

def test():
    select=" code "
    where=" destination = 'PTE'"
    temp=selectQuery(select,'hotel_list',where)
    result=[]
    for item in temp:
        result.append(int(item[0]) )
    print(result)

def main():
    print("")
    # getChangedRateKey(reserve)

if __name__ == "__main__":
    main()
