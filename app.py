import json
import os
from flask import *
from flask_cors import CORS
from hashlib import sha256
from datetime import timedelta
from activity import getAvailActivities ,bookActivity,getActivityDetail,searchActivityByHotelCode,getActivityVoucher
from hotel import getHotelContent ,getHotelAvailability,getChangedRateKey,checkRateKey,bookHotel,getFilteredCode,getRoomRateComment,getHotelVoucher,getCurrency
from auth import register,verifyUser,login,resendVerifyCode ,modifiyUserInfo,changePwd, sendEmail
from admin import getHotelDataByAdmin,getStatisticByAdmin,getPaymentInfo,getBookMarkUp,insertBookMarkUp,getActivityDataByAdmin,hotelCancellationByAdmin,activityCancellationByAdmin,changeEnvByAdmin,getCSVFileByAdmin,getHotelBookCSVByAdmin,getActivityBookCSVByAdmin
from user import getHotelBookedDataByUser,hotelBookingCancelHandlerByUser,getActivityBookedDataByUser,activityBookingCancelHandlerByUser
from region import getRegion


app = Flask(__name__,
static_folder='./static')
app.debug = True
app.secret_key="0843ce8657267b77208d"
app.permanent_session_lifetime = timedelta(minutes=1)
upload_avatar_folder="./static/avatar"
upload_voucher_folder="./static/voucher"

CORS(app)

@app.route('/' , methods = ['GET','POST'])
def index():
    return 'Flask is running'
    
@app.route('/login' , methods = ['POST'])
def makeLogin():
    params = json.loads(request.data)
    result=login(params)
    if result==1:
        return jsonify({"success":False,"message":"User does not exist"})
    if result==2:
        return jsonify({"success":False,"message":"Please complete the verfication"})
    if result==3:
        return jsonify({"success":False,"message":"Account is blocked"})
    if result ==4:
        return jsonify({"success":False,"message":"Password does not match email"})
    else:
        return jsonify({"success":True,"result":result})
    
@app.route('/register' , methods = ['POST'])
def makeRegister():
    params = json.loads(request.data)
    result=register(params)
    if result==False:
        return jsonify({"success":False,"message":"Email was registered already"})
    else:
        return jsonify({"success":True,"result":result})
 
@app.route('/resendVerifyCode',methods=['POST'])
def makeResendVerifyCode():
    params=json.loads(request.data)
    result=resendVerifyCode(params)
    return jsonify({"success":True,"result":result})

@app.route('/veriycode',methods=['POST'])
def makeVerifyCode():
    params=json.loads(request.data)
    result=verifyUser(params['email'],params['verifycode'])
    if result==True:
        return jsonify({"success":True,"result":"Email verification is successed"})
    else:
        return jsonify({"success":False,"message":"Something went wrong"})

@app.route('/modifyUserInfo',methods=['POST'])
def makeModifiyUserInfo():
    try:
        params=request.form
        fileName=None
        if request.files.get('avatar') !=None:
            file=request.files['avatar']
            ext= os.path.splitext(file.filename)[1]
            new_name=sha256(file.filename.encode('utf-8')).hexdigest()
            fileName='static/'+new_name+ext
            file.save(fileName)
        result=modifiyUserInfo(params,fileName)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/changePwd',methods=['POST'])
def makeChangePwd():
    try:
        params=json.loads(request.data)
        result=changePwd(params)
        if result ==True:
            return jsonify({'success':True,'result':"Password changed successfully"})
        else:
            return jsonify({'success':False,'result':"Your Password is not correct"})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getRegion',methods=['GET'])
def makeRegionResponse():
    try:
        result =getRegion()
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({'success':False ,'message':str(e)}) 

@app.route('/getAvailActivities',methods=['POST'])
def makeGetActivities():
    params=json.loads(request.data)
    try:
        result = getAvailActivities(params)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({'success':False ,'message':str(e)})

@app.route('/searchActivityByHotelCode',methods=['POST'])
def makeSearchActivityByHotelCode():
    params=json.loads(request.data)
    try:
        result = searchActivityByHotelCode(params)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({'success':False ,'message':str(e)})

@app.route('/getActivityDetail',methods=['POST'])
def makeGetActivityDetail():
    params = json.loads(request.data)
    try:
        result = getActivityDetail(params)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({'success':False ,'message':str(e)})

@app.route('/bookActivity',methods=['POST'])
def makeBookActivity():
    params=json.loads(request.data)
    result=bookActivity(params)
    if result['status'] ==True:
        return jsonify({'success':True,'result':result['result']})
    else:
        return jsonify({"success":False,'message':result['error']})

@app.route('/getHotelContent',methods=['POST'])
def makeGetHotelContent():
    params=json.loads(request.data)
    try:    
        result=getHotelContent(params['hotelCodes'])
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({'success':False ,'message':str(e)})

@app.route('/getHotelAvailability',methods=['POST'])
def makeGetHotelAvailability():
    params=json.loads(request.data)
    try:
        result=getHotelAvailability(params)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({'success':False,'message':str(e)})

@app.route('/updateAvailability',methods=['POST'])
def makeRateKey():
    params=json.loads(request.data)
    try:
        result=getChangedRateKey(params)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({'success':False,'message':str(e)})
    
@app.route('/checkRateKey',methods=['POST'])
def makeCheckRateKey():
    params=json.loads(request.data)
    try:
        result =checkRateKey(params)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({'success':False,'message':str(e)})
    
@app.route('/bookHotel',methods=['POST'])
def makeBookHotel():
    params=json.loads(request.data)
    result=bookHotel(params)
    if result['success'] ==True:
        return jsonify({'success':True,'result':result['data']})
    else:
        return jsonify({"success":False,'message':result['error']})
 
@app.route('/getHotelIndexes',methods=['POST'])
def makeHotelIndexes():
    try:
        params=json.loads(request.data)
        result=getFilteredCode(params)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getRoomRateComment',methods=['POST'])
def makeRoomRateComment():
    try:
        params=json.loads(request.data)
        result=getRoomRateComment(params)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getCurrentCurrency',methods=['POST'])
def makeGetCurrentCurrency():
    try:
        params=json.loads(request.data)
        result=getCurrency(params)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getHotelBookDataByAdmin',methods=['POST'])
def makeGetBookingData():
    try:
        params=json.loads(request.data)
        result=getHotelDataByAdmin(params)
        return jsonify({'success':True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getStatisticsByAdmin',methods=['POST'])
def makeGetStatisticsByAdmin():
    try:
        params=json.loads(request.data)
        result=getStatisticByAdmin(params)
        return jsonify({"success":True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getPaymentInfoByAdmin',methods=['GET'])
def makeGetPaymentInfoByAdmin():
    try:
        result=getPaymentInfo()
        return jsonify({"success":True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getMarkUpByAdmin',methods=['POST'])
def makeGetMarkUpByAdmin():
    try:
        params=json.loads(request.data)
        result=getBookMarkUp(params)
        return jsonify({"success":True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})
    
@app.route('/insertNewMarkUpByAdmin',methods=['POST'])
def insertNewMarkUpByAdmin():
    try:
        params=json.loads(request.data)
        result=insertBookMarkUp(params)
        return jsonify({"success":True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getActivityDataByAdmin',methods=['POST'])
def makeGetActivityDataByAdmin():
    try:
        params=json.loads(request.data)
        result=getActivityDataByAdmin(params)
        return jsonify({"success":True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/changeAdminSettingByAdmin',methods=['POST'])
def makeChangeAdminSettingByAdmin():
    try:
        params=json.loads(request.data)
        result=changeEnvByAdmin(params)
        if result == True:
            return jsonify({"success":True,'result':"Successfully Changed"})
        else:
            return jsonify({"success":False,'result':"Password is not correct"})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getStatisticsCSVByAdmin',methods=['POST'])
def makeGetStatisticsCSVByAdmin():
    try:
        params=json.loads(request.data)
        path=getCSVFileByAdmin(params)
        return send_file(path,as_attachment=True)
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getHotelBookCSVByAdmin',methods=['POST'])
def makeGetHotelBookCSVByAdmin():
    try:
        # params=json.loads(request.data)
        path=getHotelBookCSVByAdmin()
        return send_file(path,as_attachment=True)
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getActivityBookCSVByAdmin',methods=['POST'])
def makeGetActivityBookCSVByAdmin():
    try:
        # params=json.loads(request.data)
        path=getActivityBookCSVByAdmin()
        return send_file(path,as_attachment=True)
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getHotelDataByUser',methods=['POST'])
def makeGetHotelDataByUser():
    try:
        params=json.loads(request.data)
        result=getHotelBookedDataByUser(params)
        return jsonify({"success":True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/getActivityDataByUser',methods=['POST'])
def makeGetActivityDataByUser():
    try:
        params=json.loads(request.data)
        result=getActivityBookedDataByUser(params)
        return jsonify({"success":True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/cancelHotelBookByUser',methods=['POST'])
def makeCancelHotelBookByUser():
    try:
        params=json.loads(request.data)
        result=hotelBookingCancelHandlerByUser(params)
        if result ==False:
            return jsonify({"success":False,'message':"Cancellation Failed"})
        else:
            return jsonify({"success":True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/cancelHotelBookByAdmin',methods=['POST'])
def makeCancelHotelBookByAdmin():
    try:
        params=json.loads(request.data)
        result=hotelCancellationByAdmin(params)
        if result['status'] ==True:
            return jsonify({"success":True,'result':result['result']})
        else:
            return jsonify({"success":False,'result':result['result']})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/cancelActivityBookByUser',methods=['POST'])
def makeCancelActivityBookByUser():
    try:
        params=json.loads(request.data)
        result=activityBookingCancelHandlerByUser(params)
        if result ==False:
            return jsonify({"success":False,'message':"Something went wrong"})
        else:
            return jsonify({"success":True,'result':result})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})

@app.route('/cancelActivityBookByAdmin',methods=['POST'])
def makeCancelActiviyBookByAdmin():
    try:
        params=json.loads(request.data)
        result=activityCancellationByAdmin(params)
        if result['status'] ==True:
            return jsonify({"success":True,'result':result['result']})
        else:
            return jsonify({"success":False,'result':result['result']})
    except Exception as e:
        return jsonify({"success":False,'message':str(e)})


@app.route('/static/voucher/hotel/<name>')
def makeGetHotelVoucher(name):
    result=getHotelVoucher(name)
    return result

@app.route('/static/voucher/activity/<name>')
def makeGetActivityVoucher(name):
    result=getActivityVoucher(name)
    return result


@app.route('/static/avatar/<name>')
def makeGetImage(name):
    return send_from_directory(upload_avatar_folder, name)

@app.route('/test',methods=['GET'])
def makeTest():
    try:
        sendEmail()
        return "successfully send email verify code"
    except Exception as e:
        return str(e)



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)

