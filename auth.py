import random
import smtplib
import os
import datetime
from hashlib import sha256
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db import  InsertData ,selectQuery,updateQuery,insertQuery
from jinja2 import Template
from region import getRegion

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
    random_number=random.randint(100000,999999)
    return str(random_number) 

def login(params):
    email=params['email']
    password=passwordHash(params['password'])
    select=" id, surname, name, country, zipcode, address, email, phone, avatar, type, email_verify, status, password"
    where=f" email = '{email}'"
    user=selectQuery(select,"user",where)
    if len(user) ==0:
        print("user does not exist")
        return 1
    if user[0][10]==0:
        print("email verification needed")
        return 2
    if user[0][11]==0:
        print("complete verification")
        return 2
    if user[0][11]==2:
        print("your acc has been blocked")
        return 3
    if user[0][12]!=password:
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
            "avatar":user[0][8],
            "type":user[0][9]
        }
        if int(user[0][9])  == 1:
            userData['hotelEnv']=HOTEL_ENV
            userData['activityEnv']=ACTIVITY_ENV

        region=getRegion()
        res={
            "region":region,
            "userData":userData
        }
        return res

def register(params):
    email=params['email']
    password=passwordHash(params['password'])
    formatedTime=datetime.datetime.utcnow()
    if checkDuplicate(email) == True:
        rand=random6Digest()
        fields=" email , password, type, create_at, update_at ,email_code, status, email_verify "
        values=f" '{email}', '{password}', 2, '{formatedTime}', '{formatedTime}', {rand}, 0, 0"
        insertQuery('user',fields,values)
        sendEmail(email,rand,0)
        return True
    else:
        return False

def verifyCode(params):
    type=int( params['type'])
    code=params['code']
    email=params['email']
    flag=checkCode(code,email)
    if flag==True:
        if type ==0:
            verifyUser(email)
        # elif type ==1:
        #     resetPwd(email)
    return flag

def verifyUser(email):
    where=f" email = '{email}'"
    update=" email_verify = 1 , status = 1"
    updateQuery('user',update,where)

def checkCode(code,email):
    where=f" email = '{email}'"
    user=selectQuery('email_code','user',where)
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
    type=int(params['type']) 
    code=random6Digest()
    where=f" email='{email}'"
    update=f" email_code = '{code}'"
    updateQuery('user',update,where)
    sendEmail(email,code,type)
    return True

def sendEmail(email,code,type):
    msg=MIMEMultipart()
    msg['Subject']="Verify Email"
    msg['From']=SERVER_USER
    msg['to']=email
    fileName="./static/mail/"
    if type==0:
        fileName+="2fa.html"
    elif type==1:
        fileName+="forgot.html"
    with open(fileName) as f:
            html_template=Template(f.read())
    html=html_template.render(code=code)
    msg.attach(MIMEText(html,'html'))
    try:
        smtp=smtplib.SMTP_SSL('localhost',SMTP_PORT)
        smtp.ehlo()
        smtp.login(SERVER_USER,SERVER_PASSWORD)
        smtp.sendmail(SERVER_USER,email,msg.as_string())
        smtp.close()
    except:
        return "Something went wrong"

def modifiyUserInfo(params,file):
    now=datetime.datetime.utcnow()
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

def forgotPwd(params):
    email=params['email']
    where=f" email = '{email}'"
    result= selectQuery('email','user',where)
    if len(result)==0:
        return False
    else:
        code=random6Digest()
        where=f" email = '{email}'"
        update= f" email_code = '{code}'"
        updateQuery('user',update,where)
        sendEmail(email,code,1)
        return True

def resetPwd(params):
    email=params['email']
    pwd=params['pwd']
    code=params['code']
    where=f" email = '{email}'"
    select=" email_code"
    try:
        email_code=selectQuery(select,'user',where)[0][0]
        if email_code == code:
            hashPwd=passwordHash(pwd)
            update=f" password = '{hashPwd}' "
            updateQuery('user',update,where)
            return True
        else:
            return False
    except Exception as e:
        return False
    
    
   

def main():
     params={
         "code":"333044",
         "email":"dounine423@gmail.com"
     }
     resetPwd(params)

if __name__ == "__main__":
    main()