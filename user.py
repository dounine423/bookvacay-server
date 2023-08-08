import re
import math
import time
import os
import requests
from hashlib import sha256
from dotenv import load_dotenv
from datetime import datetime,timedelta
from db import selectQuery,updateQuery

load_dotenv()

HOTEL_ENV=os.getenv('HOTEL_ENV')
ACTIVITY_ENV=os.getenv('ACTIVITY_ENV')

def getXSignature(API_KEY,SECRET_KEY):
    utcDate= math.floor(time.time())
    assemble=API_KEY+SECRET_KEY+str(utcDate)
    hash=sha256(assemble.encode('utf-8'))
    encryption=hash.hexdigest()
    return encryption

def getHotelBookedDataByUser(params):
    user_id=int(params['user_id'])
    status=int(params['status'])
    offset=int(params['offset'])
    limit=int(params['limit'])
    select=" A.id, A.type, A.create_at, A.reference, A.status, A.cancellation, A.modification, B.name, D.content, A.indate, A.outDate, A.paid_amount, A.c_currency, p_currency, C.rate, A.uuid, A.voucher, A.room_data "
    table_from=" ( hotel_book A, hotel_list B, bank_mark_up C, destination D) "
    where=f" A.h_code = B.code and D.code = B.destination and A.hd_id = {user_id} and A.bank_mark_up = C.id"
    if status != 0:
        where+=f" and A.status = {status}"
    hotelBookedData=selectQuery(select,table_from,where,'A.update_at','DESC',limit,offset)
    select=" count(A.id)"
    total=selectQuery(select,table_from,where)[0][0]
    bookList=[]
    for item in hotelBookedData:
        room_data=[]
        if item[17]!=None:
            roomIds=item[17].split(',')
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
                    "room_count":room[5],
                    "adult":room[9],
                    "child":room[10],
                    "c_date":room[11]
                }
                room_data.append(temp)
        data={
            "id":item[0],   
            "type":item[1],
            "create_at": str(item[2]),
            "reference":item[3],
            "status":item[4],
            "cancellation":item[5],
            "modification":item[6] ,
            "hotel_name":item[7] ,
            "destination":item[8],
            "indate": str(item[9]),
            "outdate":str( item[10]),
            "paid":round(item[11],2),
            "c_currency":item[12],
            "p_currency":item[13],
            "bank_markup":item[14],
            "uuid":item[15],
            "voucher":item[16],
            "room_data":room_data
        }
        bookList.append(data)
    result={
        "list":bookList,
        "total":total
    }
    return result

def getActivityBookedDataByUser(params):
    user_id=int(params['user_id'])
    status=int(params['status']) 
    limit=params['limit']
    offset=params['offset']
    where=f" h_id = {user_id} "
    if status >0:
        where +=f" and status = {status}"
    total=selectQuery('count(id)','activity_book',where)[0][0]
    select=" id, reference, status, paid_amount, currency, invoice_company, invoice_number, activities, create_at, voucher, type"
    tempData=selectQuery(select,'activity_book',where,'create_at','DESC',limit,offset)
    tempList=[]
    for item in tempData:
        activities=[]
        select='C.*'
        table_from=" (select A.*, B.content  from activity_modality A, destination B where A.destination = B.code ) C"
        where=""
        if item[7] !=None:
            ids=item[7].split(',')
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
                    "pax":activity[18],
                    "create_at":str(activity[19]) ,
                    "destination":activity[21]
                }
                activities.append(activityData)
        data={
            "id":item[0],
            "reference":item[1],
            "status":item[2],
            "paid_amount":item[3],
            "currency":item[4],
            "invoice_company":item[5],
            "invoice_vat":item[6],
            "activities":activities,
            "create_at":str(item[8]) ,
            "voucher":item[9],
            "type":item[10]
        }
        tempList.append(data)
    
    result={
        "list":tempList,
        "total":total
    }
    return(result)

def getFormattedDateTime(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

def hotelBookingCancelHandlerByUser(params):
    reference=params['reference']
    book_id=int(params['book_id']) 
    user_id=int(params['user_id'])
    params={
        "user_id":user_id,
        "offset":0,
        "limit":5,
        "status":0
    }
    select=" id, c_date, c_amount"
    where=f" reference = '{reference}'"
    room_data=selectQuery(select, 'hotel_room',where)
    c_diff_flag=0
    cur_c_date=room_data[0][1].split('+')[0]
    now=datetime.now()
    where=f" id = {book_id}"
    for item in room_data:
        if item[1].split('+')[0] !=cur_c_date and getFormattedDateTime(item[1].split('+')[0]) >now:
            c_diff_flag=1
    if c_diff_flag ==1:
        result_flag=hotelBookingCancel(reference)
        if result_flag ==True:
            update=f" status = 4 , update_at = '{now}'"
            updateQuery('hotel_book',update,where)
        else:
            return False
    else:
        if getFormattedDateTime(cur_c_date)>now:
            result_flag=hotelBookingCancel(reference)
            if result_flag ==True:
                update=f" status = 4 , update_at = '{now}'"
                updateQuery('hotel_book',update,where)
            else:
                return False
        else:
            result_flag=hotelBookingCancel(reference)
            if result_flag ==True:
                update=f" status = 2 , update_at = '{now}'"
                updateQuery('hotel_book',update,where)
            else:
                return False
    result=getHotelBookedDataByUser(params)
    return result

def hotelBookingCancel(reference):
    endPoint=""
    if HOTEL_ENV == '1':
        HOTEL_API_KEY=os.getenv('HOTEL_DEV_KEY')
        HOTEL_SECRET_KEY=os.getenv('HOTEL_DEV_SECRET')
        endPoint=os.getenv('TEST_END_POINT')
    elif HOTEL_ENV == '2':
        HOTEL_API_KEY=os.getenv('HOTEL_LIVE_KEY')
        HOTEL_SECRET_KEY=os.getenv('HOTEL_LIVE_SECRET')
        endPoint=os.getenv('LIVE_END_POINT')
    url=endPoint+"/hotel-api/1.0/bookings/"
    url+=reference+"? cancellationFlag=CANCELLATION"
    header={
        "Api-key":HOTEL_API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(HOTEL_API_KEY,HOTEL_SECRET_KEY),
        "Accept-Encoding":"gzip"
    }
    res=requests.delete(url,headers=header)
    if int(res.status_code )==200:
        return True
    else:
        return False

def activityBookingCancelHandlerByUser(params):
    book_id=int(params['book_id']) 
    user_id=int(params['user_id'])
    reference=params['reference']
    params={
        "user_id":user_id,
        "offset":0,
        "limit":5,
        "status":0
    }
    now=datetime.now()
    select=" id, c_date, c_amount"
    where=f" reference = '{reference}'"
    flag= cancelActivityBook(reference)
    tempResult=selectQuery(select,'activity_modality',where)
    
    c_flag=0
    for item in tempResult:
        if item[1] !=None:
            temp_c_date=item[1].split('T')[0]
            c_date=datetime.strptime(temp_c_date,'%Y-%m-%d') -timedelta(days=1)
            if c_date > now:
                c_flag=1
    if flag ==True:
        where=f" id = {book_id}"
        if c_flag==1:
            update=f" status = 4 , update_at = '{now}'"
        else:
            update=f" status = 2 , update_at = '{now}'"
        updateQuery('activity_book',update,where)
        result=getActivityBookedDataByUser(params)
        return result
    else:
        return False
    
def cancelActivityBook(reference):
    endPoint=""
    if ACTIVITY_ENV == '1':
        ACTIVITY_API_KEY=os.getenv('ACTIVITY_DEV_KEY')
        ACTIVITY_SECRET_KEY=os.getenv('ACTIVITY_DEV_SECRET')
        endPoint=os.getenv('TEST_END_POINT')
    elif ACTIVITY_ENV == '2':
        ACTIVITY_API_KEY=os.getenv('ACTIVITY_LIVE_KEY')
        ACTIVITY_SECRET_KEY=os.getenv('ACTIVITY_LIVE_SECRET')
        endPoint=os.getenv('LIVE_END_POINT')
    url=endPoint+"/activity-api/3.0/bookings/en/"
    url+=reference+"?cancellationFlag=CANCELLATION"
    header={
        "Api-key":ACTIVITY_API_KEY,
        "Accept":"application/json",
        "X-Signature":getXSignature(ACTIVITY_API_KEY,ACTIVITY_SECRET_KEY),
        "Accept-Encoding":"gzip"
    }
    res=requests.delete(url,headers=header)
    if int(res.status_code) == 200:
        return True
    else:
        return False
    # book_id=int(params['book_id']) 
    # user_id=int(params['user_id'])
    # params={
    #     "user_id":user_id,
    #     "offset":0,
    #     "limit":5,
    #     "status":0
    # }
    # now=datetime.now()
   
    # 
    # 
    # 

def main():
    params={
        "user_id":6,
        "book_id":6,
        "offset":0,
        "status":0,
        "limit":5
    }
    result= getHotelBookedDataByUser(params)
    # print(result)

if __name__ == "__main__":
    main()