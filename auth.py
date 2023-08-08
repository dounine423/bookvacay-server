import random
import math
import smtplib
import os
import datetime
from hashlib import sha256
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db import  InsertData ,selectQuery,updateQuery,insertQuery
from bs4 import BeautifulSoup

load_dotenv()

ACTIVITY_ENV=os.getenv('ACTIVITY_ENV')
HOTEL_ENV=os.getenv('HOTEL_ENV')
SMTP_SERVER=os.getenv('SMTP_SERVER')
SMTP_PORT=os.getenv('SMTP_PORT')
SERVER_USER=os.getenv('SERVER_USER')
SERVER_PASSWORD=os.getenv('SERVER_PASSWORD')
HOST_URL=os.getenv('HOST_URL')

def passwordHash(password):
    hash=sha256(password.encode('utf-8'))
    return hash.hexdigest()[0:20]

def random6Digest():
    rand=random.random()
    rand=rand*math.pow(10,6)
    rand=int(rand)
    return rand

def login(params):
    email=params['email']
    password=passwordHash(params['password'])
    where=f" email = '{email}'"
    user=selectQuery("*","user",where)
    if len(user) ==0:
        print("user does not exist")
        return 1
    # if user[0][8]==0:
    #     print("email verification needed")
    #     return 2
    # if user[0][10]==0:
    #     print("first email verification needed")
    #     return 2
    # if user[0][10]==2:
    #     print("your acc has been blocked")
    #     return 3
    if user[0][10]!=password:
        return 4
    else:
        userData={
            "id":user[0][0],
            "surname":user[0][1],
            "name":user[0][2],
            "country":user[0][3],
            "zipcode":user[0][4],
            "address":user[0][5],
            "email":user[0][6],
            "phone":user[0][7],
            "avatar":user[0][11],
            "type":user[0][12]
        }
        if int(user[0][12])  == 1:
            userData['hotelEnv']=HOTEL_ENV
            userData['activityEnv']=ACTIVITY_ENV

        return userData

def register(params):
    email=params['email']
    password=passwordHash(params['password'])
    formatedTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if checkDuplicate(email) == True:
        rand=random6Digest()
        fields=" email , password, type, create_at, update_at ,email_code "
        values=f" '{email}', '{password}', 2, '{formatedTime}', '{formatedTime}', {rand}"
        insertQuery('user',fields,values)
        sendEmail(email,rand)
        return rand
    else:
        return False

def verifyUser(email,code):
    flag=checkCode(code,email)
    if flag==True:
        where=f" email = '{email}'"
        update=" email_verify = 1 , status = 1"
        updateQuery('user',update,where)
    return flag
    
def checkCode(code,email):
    where=f" email = '{email}'"
    user=selectQuery('verify_code','user',where)
    if code == user[0][0]:
        return True
    else:
        return False
        
def checkDuplicate(email):
    where=f"email = '{email}'"
    result=selectQuery('id','user',where)
    if len(result) ==0:
        return True
    else:
        return False

def resendVerifyCode(params):
    email=params['email']
    code=random6Digest()
    sendEmail(email,code)
    return code

def sendEmail(email="dounine423@gmail.com",code=123456):
    msg=MIMEMultipart()
    msg['Subject']="Verify Email"
    msg['From']=SMTP_SERVER
    msg['to']=email
    with open('mail.html') as f:
        html=f.read()
    mailData=BeautifulSoup(html,'html.parser')
    name_td= mailData.find('td',{'id':'user-name'})
    name_td.string=f"Hi "
    code_td=mailData.find('div',{'id':'verify-code'})
    code_td.string=str(code)
    print(mailData)
    msg.attach(MIMEText(mailData,'html'))
    try:
        smtp=smtplib.SMTP_SSL(SMTP_SERVER,SMTP_PORT)
        smtp.ehlo()
        smtp.login(SERVER_USER,SERVER_PASSWORD)
        smtp.sendmail(SERVER_USER,email,msg.as_string())
        smtp.close()
    except:
        return "Something went wrong"

def modifiyUserInfo(params,file):
    now=datetime.datetime.now()
    update=f" surname = '{params['surname']}', name = '{params['name']}', country = '{params['country']}', zipcode = '{params['zipcode']}', address = '{params['address']}', phone= '{params['phone']}' ,  update_at = '{now}'"
    if file!=None:
        update+=f" , avatar = '{HOST_URL+ file}'"
    where=f" id = {params['id']}"
    updateQuery('user',update,where)
    user=selectQuery('*','user',where)
    userData={
        "id":user[0][0],
        "surname":user[0][1],
        "name":user[0][2],
        "country":user[0][3],
        "zipcode":user[0][4],
        "address":user[0][5],
        "email":user[0][6],
        "phone":user[0][7],
        "avatar":user[0][11],
        "type":user[0][12]
    }
    return userData

def changePwd(params):
    select=' password'
    where = f" id = {params['id']}"
    curPwd=selectQuery(select,'user',where)[0][0]
    if passwordHash(params['curPwd']) ==curPwd:
        update=f" password = '{passwordHash(params['newPwd'])}'"
        updateQuery('user',update,where)
        return True
    else:
        return False

def main():
    request={
        "surname":"kristen",
        "lastname":"kropf",
        "country":"ES",
        "zipcode":"12345",
        "address":"willington",
        "email":"dounine423@gmail.com",
        "phone":"1232222",
        "password":"12345678"
    }
    sendEmail()

if __name__ == "__main__":
    main()