import datetime
import os
import time
import requests
import math
import csv
from hashlib import sha256
from dotenv import load_dotenv,set_key
from db import selectQuery,insertQuery,updateQuery

load_dotenv()

HOST_URL=os.getenv('HOST_URL')
ACTIVITY_ENV=os.getenv('ACTIVITY_ENV')
HOTEL_ENV=os.getenv('HOTEL_ENV')

def passwordHash(password):
    hash=sha256(password.encode('utf-8')) 
    return hash.hexdigest()[0:20]

def getXSignature(API_KEY,SECRET_KEY):
    utcDate= math.floor(time.time())
    assemble=API_KEY+SECRET_KEY+str(utcDate)
    hash=sha256(assemble.encode('utf-8'))
    encryption=hash.hexdigest()
    return encryption

def getCSVFileByAdmin(params):
    result=getStatisticByAdmin(params)
    fileName="static/csv/"+passwordHash(str(datetime.datetime.now()))+".csv"
    with open("./"+fileName,'w+') as f:
        writer=csv.writer(f)
        writer.writerow(['DateTime','Value'])
        for item in result:
            writer.writerow([item['time'],item['value']])
    return "./"+fileName

def getStatisticByAdmin(params):
    type=int(params['type'])
    group=int(params['group'])
    date=params['date']
    table_from=""
    select=" sum( profit_amount * z_h_rate)"
    groupBy=""
    where=" type = 1  "
    orderBy=""
    if type == 1:
        table_from=" hotel_book "
    else:
        # activity book
        table_from=" hotel_book "
    if group ==1:
        select+=" ,DATE_FORMAT(create_at, '%Y-%m-%d %H:00:00') "
        date=date['year']+"-"+date['month']+"-"+date['day']
        where+=f" and DATE_FORMAT(create_at, '%Y-%m-%d') = '{date}'"
        groupBy=" DATE_FORMAT(create_at, '%Y-%m-%d %H:00:00') "
    elif group ==2:
        select+=" ,DATE_FORMAT(create_at, '%Y-%m-%d') "
        date=date['year']+"-"+date['month']
        where+=f" and DATE_FORMAT(create_at, '%Y-%m') = '{date}'"
        groupBy=" DATE_FORMAT(create_at, '%Y-%m-%d') "
    elif group == 3:
        select+=" ,DATE_FORMAT(create_at, '%Y-%m') "
        date=date['year']
        where+=f" and DATE_FORMAT(create_at, '%Y') = '{date}'"
        groupBy=" DATE_FORMAT(create_at, '%Y-%m') "
    elif group == 4:
        select+=" ,DATE_FORMAT(create_at, '%Y-%m') "

        groupBy=" DATE_FORMAT(create_at, '%Y-%m') "

    tempResult=selectQuery(select,table_from,where,groupBy,'ASC',None,None,groupBy) 
    result=[]
    for item in tempResult:
        data={
            "time":item[1],
            "value":round(float(item[0]),2) 
        }
        result.append(data)
    return result

def getHotelDataByAdmin(params):
    status=int(params['status'])
    offset=int(params['offset'])
    limit=int(params['limit'])
    select=" A.id, A.type, A.create_at, A.reference, A.status, A.cancellation, A.modification, B.name, D.content, A.indate, A.outDate, A.pending_amount, A.paid_amount, A.net_amount, A.profit_amount, A.h_currency, A.c_currency, A.p_currency, A.invoice_company, A.invoice_number, A.supply_name, A.supply_ref, C.rate, E.rate, A.z_h_rate, A.c_h_rate, A.rate_update_at, A.uuid, A.voucher, A.room_data, A.update_at, A.hd_id, A.hd_name, A.hd_surname, A.hd_email, A.hd_phone "
    table_from=" ( hotel_book A, hotel_list B, book_mark_up C, destination D, bank_mark_up E) "
    where=" A.h_code = B.code and A.hotel_mark_up = C.id and D.code = B.destination and E.id = A.bank_mark_up"
    if status != 0:
        where+=f" and A.status = {status}"
    if params.get('duration') !=None:
        duration=params['duration']
        where+=f" and A.create_at between '{duration['from']}' and '{duration['to']}'"
    if params.get('keyword') !="":
        keyword=params['keyword']
        where+=f" and B.name like '%{keyword}%'"   
    hotelBookedData=selectQuery(select,table_from,where,'A.create_at','DESC',limit,offset)
    select=" count(A.id)"
    total=selectQuery(select,table_from,where,'A.create_at','DESC')[0][0]
    bookList=[]
    for item in hotelBookedData:
        room_data=[]
        if item[29] !=None :
            roomIds=item[29].split(',')
            where=""
            for roomId in roomIds:
                where=f" id = {int(roomId)} or"
            size=len(where)
            where=where[0:(size-2)]
            temp_rooms=selectQuery('*','hotel_room', where)
            for room in temp_rooms:
                temp={
                    "id":room[0],
                    "room_name":room[3],
                    "room_code":room[4],
                    "room_count":room[5],
                    "net_price":room[7],
                    "payment_type":room[8],
                    "adult":room[9],
                    "child":room[10],
                    "c_date":room[11],
                    "c_amount":room[12],
                    "tax":room[15],
                    "total":room[16]
                }
                room_data.append(temp)
          
        data={
            "id":item[0],   
            "type":item[1],
            "create_at":str(item[2]),
            "reference":item[3],
            "status":item[4],
            "cancellation":item[5],
            "modification":item[6] ,
            "hotel_name": item[7],
            "destination":item[8],
            "inDate":str(item[9]) ,
            "outDate":str(item[10]) ,
            "pending":item[11],
            "paid":item[12],
            "net":item[13],
            "profit":item[14],
            "h_currency":item[15],
            "c_currency":item[16],
            "p_currency":item[17],
            "invoice_company":item[18],
            "invoice_number":item[19],
            "supply_name":item[20],
            "supply_ref":item[21],
            "hotel_markup":item[22],
            "bank_markup":item[23],
            "z_h_rate":item[24],
            "c_h_rate":item[25],
            "rate_update":item[26],
            "uuid":item[27],
            "voucher":item[28],
            "room_data":room_data,
            "update_at":str(item[30]), 
            "holder_id":item[31],
            "holder_name":item[32]+" "+item[33],
            "holder_email":item[34],
            "holder_phone":item[35]
        }
        bookList.append(data)
    result={
        "list":bookList,
        "total":total
    }
    return result

def getPaymentInfo():
    select=" sum( profit_amount * z_h_rate)"
    hotel=selectQuery(select,'hotel_book')
    # activity=selectQuery(select,'activity_book')
    totalHotel=0
    totalActivity=0
    if hotel[0][0]!=None:
        totalHotel=round(hotel[0][0],2)
    # if activity[0][0] !=None:
    #     totalActivity=round(activity[0][0],2)
    paymentInfo={
        "hotel":totalHotel,
        "activity":totalActivity,
        "currency":"ZAR"
    }
    return paymentInfo

def getBookMarkUp(params):
    type=int(params['type'])
    limit=params['limit']
    offset=params['offset']
    where=None
    if type > 0 :
        where= f" type = {type}"
    total=selectQuery('count(id)','book_mark_up',where)[0][0]
    temp=selectQuery('*','book_mark_up',where,'update_at','DESC',limit,offset)
    markup=markUpListToArray(temp)
    result={
        "list":markup,
        "total":total
    }
    return result

def markUpListToArray(listData):
    result=[]
    for item in listData:
        data={
            "id":item[0],
            "rate":item[1],
            "comment":item[2],
            "create":item[3],
            "update":item[4],
            "type":item[5]
        }
        result.append(data)
    return result

def insertBookMarkUp(params):
    type=params['type']
    rate=params['rate']
    comment=params['comment']
    now=datetime.datetime.now()
    fields=" rate, comment, create_at, update_at, type"
    values=f" {rate}, '{comment}', '{now}', '{now}', {type}"
    insertQuery('hotel_mark_up',fields,values)
    where={
        "type":0,
        "limit":5,
        "offset":0
    }
    result=getBookMarkUp(where)

    return result
    
def getActivityDataByAdmin(params):
    status=int(params['status']) 
    limit=params['limit']
    offset=params['offset']
    select=" A.id, A.reference, A.status, A.paid_amount, A.pending_amount, A.total_amount, A.profit_amount, A.currency, A.invoice_company, A.invoice_number, A.activities, A.h_id, A.h_name, A.h_surname, A.h_email, A.h_phone, A.h_address, A.h_zipcode, A.create_at, A.update_at, A.voucher, A.type , B.rate"
    table_from=" activity_book A, tolerance B"
    where=" A.tolerance = B.id "
    if status >0:
        where +=f" and A.status = {status}"
    if params.get('duration') !=None:
        duration=params['duration']
        where +=f" and A.create_at between '{duration['from']}' and '{duration['to']}'"
    total=selectQuery('count(A.id)',table_from,where)[0][0]
    tempData=selectQuery(select,table_from,where,'A.create_at','DESC',limit,offset)
    tempList=[]
    for item in tempData:
        activities=[]
        if item[10] !=None:
            select='C.*'
            table_from=" (select A.*, B.content  from activity_modality A, destination B where A.destination = B.code ) C"
            where=""
            ids=item[10].split(',')
            for id in ids:
                where+=f" C.id = {id} or"
            where=where[0:(len(where)-2)]
            tempActivities=selectQuery(select,table_from,where)
            for activity in tempActivities:
                activityData={
                    "id":activity[0],
                    "comment":activity[3],
                    "type":activity[4],
                    "name":activity[6],
                    "modality":activity[8],
                    "from":str(activity[9]) ,
                    "to":str(activity[10]) ,
                    "c_date":activity[12],
                    "c_amount":activity[13],
                    "amount":activity[14],
                    "supply_name":activity[15],
                    "supply_vat":activity[16],
                    "provider_name":activity[17],
                    "pax":activity[18],
                    "create_at":activity[19],
                    "update_at":activity[20],
                    "destination":activity[21]
                }
                activities.append(activityData)
        data={
            "id":item[0],
            "reference":item[1],
            "status":item[2],
            "paid_amount":item[3],
            "pending_amount":item[4],
            "total_amount":item[5],
            "profit_amount":item[6],
            "currency":item[7],
            "invoice_company":item[8],
            "invoice_vat":item[9],
            "activities":activities,
            "holder_id":item[11],
            "holder_name":item[12]+" " +item[13],
            "holder_email":item[14],
            "holder_phone":item[15],
            "holder_address":item[16],
            "holder_zipcode":item[17],
            "create_at":str(item[18]) ,
            "update_at":str(item[19]),
            "voucher":item[20],
            "type":item[21],
            "markup":item[22]
        }
        tempList.append(data)
    result={
        "list":tempList,
        "total":total
    }
    return(result)

def hotelCancellationByAdmin(params):
    book_id=params['book_id']
    where=f" id = {book_id}"
    now=datetime.datetime.now()
    update=f" status = 5, update_at= '{now}'"
    updateQuery('hotel_book',update,where)
    params={
        "status":0,
        "offset":0,
        "limit":5,
        "keyword":""
    }
    result={
        "status":True,
        "result":getHotelDataByAdmin(params)
    }
    return result

def activityCancellationByAdmin(params):
    book_id=params['book_id']
    where=f" id = {book_id}"
    now=datetime.datetime.now()
    update=f" status = 5, update_at= '{now}'"
    updateQuery('activity_book',update,where)
    params={
        "status":0,
        "offset":0,
        "limit":5,
        "keyword":""
    }
    result={
        "status":True,
        "result":getActivityDataByAdmin(params)
    }
    return result

def changeEnvByAdmin(params):
    select=" password"
    where=f" email = '{params['email']}'"
    result= selectQuery(select,'user',where)
    if passwordHash(params['pwd']) ==result[0][0]:
        set_key('.env','HOTEL_ENV',params['hotelEnv'])
        set_key('.env','ACTIVITY_ENV',params['activityEnv'])
        return True
    else:
        return False
    
def getHotelBookCSVByAdmin():
    result=getHotelBookCSVData()
    fileName="static/csv/"+passwordHash(str(datetime.datetime.now()))+ "-hotel.csv"
    with open("./"+fileName,'w+') as f:
        writer=csv.writer(f)
        fields=[]
        for item in result[0]:
            fields.append(item)
        writer.writerow(fields)
        for item in result:
            values=[]
            for index in fields:
                if item.get(index)!=None:
                    values.append(item[index])
                else:
                    values.append("")
            writer.writerow(values)
    return "./"+fileName

def type2Str(param):
    if param ==1:
        return "Booked"
    else:
        return "Failed"

def getHotelBookCSVData():
    select=" A.id, A.type, A.create_at, A.reference, A.status, A.cancellation, A.modification, B.name, D.content, A.indate, A.outDate, A.pending_amount, A.paid_amount, A.net_amount, A.profit_amount, A.h_currency, A.c_currency, A.p_currency, A.invoice_company, A.invoice_number, A.supply_name, A.supply_ref, C.rate, E.rate, A.z_h_rate, A.c_h_rate, A.rate_update_at, A.uuid, A.voucher, A.room_data, A.update_at, A.hd_id, A.hd_name, A.hd_surname, A.hd_email, A.hd_phone "
    table_from=" ( hotel_book A, hotel_list B, book_mark_up C, destination D, bank_mark_up E) "
    where=" A.h_code = B.code and A.hotel_mark_up = C.id and D.code = B.destination and E.id = A.bank_mark_up"
    hotelBookedData=selectQuery(select,table_from,where,'A.type','DESC')
    bookList=[]
    for item in hotelBookedData:
        data={
            # "id":item[0],   
            "Type":type2Str(item[1]) ,
            "CreateAt":str(item[2]),
            "Reference":item[3],
            "Status":statusCode2Str(item[4]),
            # "cancellation":item[5],
            # "modification":item[6],
            "HotelName":item[7],
            "Destination":item[8],
            "Check-in":str(item[9]) ,
            "Check-out": str(item[10]),
            "Invoice-Company":item[18],
            "Invoice-Registration-Number":item[19],
            "Supplier-Name":item[20],
            "Supplier-Vat-Number":item[21],
            "Booking-Markup": str(item[22]) +" "+"%",
            "Billing-Rate": str(item[23]) +" "+"%",
            "Rate1":(item[15]+"-"+item[16]+" "+str(item[25])) ,
            "Rate2":(item[15]+"-"+item[17]+" "+str(item[24])),
            "GUID":item[27],
            "HolderName":item[32]+ " " +item[33],
            "HolderEmail":item[34],
            "HolderPhone":item[35],
            "Total": item[16] +" "+ str(round(item[12]))
        }
        if item[13] !=None:
            data['Net']=item[15] +" "+str(item[13])
        if item[14] !=None:
            data['Profit']=item[17] +" "+str(item[14])
        bookList.append(data)
    return bookList

def statusCode2Str(code):
    code=int(code)
    if code == 1:
        return "Confirmed"
    if code == 2:
        return "Cancelled"
    if code == 3:
        return "Completed"
    if code == 4:
        return "Refund Pending"
    if code == 5:
        return "Cancelled & Refunded"

def getActivityBookCSVByAdmin():
    result=getActivityBookCSVData()
    fileName="static/csv/"+passwordHash(str(datetime.datetime.now()))+"activity.csv"
    with open("./"+fileName,'w+') as f:
        writer=csv.writer(f)
        writer.writerow(['Reference','Total','Net','Profit','Invoice Company','Invoice Registration Number','HolderName','HolderEmail','HolderPhone','HolderAddress','HolderZipCode','MarkUp','Create At'])
        for item in result:
            writer.writerow([item['reference'],item['paid_amount'],item['total_amount'],item['profit_amount'],item['invoice_company'],item['invoice_vat'],item['holder_name'],item['holder_email'],item['holder_phone'],item['holder_address'],item['holder_zipcode'],item['markup'],item['create_at']])
    return "./"+fileName

def getActivityBookCSVData():
    select=" A.id, A.reference, A.status, A.paid_amount, A.pending_amount, A.total_amount, A.profit_amount, A.currency, A.invoice_company, A.invoice_number, A.activities, A.h_id, A.h_name, A.h_surname, A.h_email, A.h_phone, A.h_address, A.h_zipcode, A.create_at, A.update_at, A.voucher, A.type , B.rate"
    table_from=" activity_book A, tolerance B"
    where=" A.tolerance = B.id "
    tempData=selectQuery(select,table_from,where,'A.create_at','DESC')
    tempList=[]
    for item in tempData:
        data={
            "id":item[0],
            "reference":item[1],
            "status":statusCode2Str(item[2]),
            "paid_amount":item[7]+" " +str(item[3]) ,
            "pending_amount":item[7]+" "+ str(item[4]) ,
            "total_amount":item[7]+" "+ str(item[5]) ,
            "profit_amount":item[7]+" "+ str(item[6]) ,
            "invoice_company":item[8],
            "invoice_vat":item[9],
            # "activities":activities,
            # "holder_id":item[11],
            "holder_name":item[12]+" " +item[13],
            "holder_email":item[14],
            "holder_phone":item[15],
            "holder_address":item[16],
            "holder_zipcode":item[17],
            "create_at":str(item[18]) ,
            "update_at":str(item[19]),
            # "voucher":item[20],
            # "type":item[21],
            "markup":str(item[22]) +" %" 
        }
        tempList.append(data)
    return tempList

def main():
    params={
        "limit":4,
        "status":0,
        "offset":0,
        "keyword":""
    }
    params={
        "group":1,
        "type":1,
        "date":{"year":'2023',"month":"08","day":"06"}
    }
    result= getHotelBookCSVByAdmin()
    # print(result)
    

if __name__ == "__main__":
    main()