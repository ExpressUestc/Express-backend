# coding:utf8
import json
import os
import shutil
from Crypto.PublicKey import RSA

import qrcode
from django.http import JsonResponse
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, render_to_response
from Express.models import Express,DeliverMan,VerifyCode,AuthDeliver
import sendmessage
import datetime
from django.db.models.query import *
import decrypt
from django.views.decorators.csrf import csrf_exempt
import sys
from models import Employee
reload(sys)

sys.setdefaultencoding('utf8')

def test(request):
    return HttpResponse('This is test')

# Create your views here.
@csrf_exempt
def index(request):

    # 1.get info from the request
    myName =  decrypt.decryptMessage(request.POST['myName'])
    myPhone = decrypt.decryptMessage(request.POST['myPhone'])
    myAddress = decrypt.decryptMessage(request.POST['myAddress'])
    myPostcode = decrypt.decryptMessage(request.POST['myPostcode'])
    extraPrice = decrypt.decryptMessage(request.POST['extraPrice'])
    rcvName = decrypt.decryptMessage(request.POST['rcvName'])
    rcvPhone = decrypt.decryptMessage(request.POST['rcvPhone'])
    rcvAddress = decrypt.decryptMessage(request.POST['rcvAddress'])
    rcvPostcode = decrypt.decryptMessage(request.POST['rcvPostcode'])
    goods = decrypt.decryptMessage(request.POST['goods'])
    expressCompany = decrypt.decryptMessage(request.POST['expressCompany'])
    remarks = decrypt.decryptMessage(request.POST['remarks'])

    # 2.create random string with 10 characters
    code = (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(16))))[0:10]

    # 3.create Qrcode
    # q = qrcode.main.QRCode()
    # q.add_data(rcvName+'\n'+rcvPhone+'\n'+code)
    # q.make()
    # m = q.make_image()

    # 4.produce the picture
    # m.save('/home/projects/Expressbackend/static/Express/'+code+'.png')  #qrcode picture's name is 'code'

    # 5.move it to the pointed directory
    # shutil.move(code+'.png','static/polls')

    # 6.save the info into the sqlite3
    # Todo:transform the code
    # Todo:encrypt info in db
    express = Express.objects.create(send_name=myName,send_phone=myPhone,send_address=myAddress,send_postcode=myPostcode,
                    extra_price=extraPrice,receive_name=rcvName,receive_phone=rcvPhone,receive_address=rcvAddress,receive_postcode=rcvPostcode,goods=goods,express_company=expressCompany,remarks=remarks,
                    code=code)
    express.save()

    # 7.create response
    # url = 'http://101.201.79.95/express/pic/?code='+code
    response = {'code':code}
    return JsonResponse(response)

def pic(request):
    code = request.GET['code']
    return render_to_response('Express/showQrcode.html',{'image':code+'.png'})

@csrf_exempt
def authDeliver(request):
    
    deliverPhone = decrypt.decryptMessage(request.POST['deliverPhone'])
    deliverID = decrypt.decryptMessage(request.POST['deliverID'])
    
    flag = 1
    try:
        deliverman = AuthDeliver.objects(deliverPhone=deliverPhone,deliverID=deliverID)
    except AuthDeliver.DoesNotExist,e:
        flag = 0

    response = {'flag':flag}

    return JsonResponse(response)

@csrf_exempt
def sending(request):

    # 2.get info
    decryptmessage = decrypt.decryptMessage(request.POST['message'])
    pos = decrypt.decryptMessage(request.POST['pos'])
    deliverPhone =  decrypt.decryptMessage(request.POST['deliverPhone'])
    deliverID = decrypt.decryptMessage(request.POST['deliverID'])

    # get decryptmessage
    # decryptmessage = decrypt.decryptMessage(encryptmessage)
    dictdecryptmessage = json.loads(decryptmessage)

    code = dictdecryptmessage['code']

    # 3.get express
    try:
        express = Express.objects(code=code)
    except Express.DoesNotExist,e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback':feedback}
        return JsonResponse(response)
    # 4.save deliverPhone
    try:
        express.deliverman.deliverPhone = deliverPhone
        express.deliverman.deliverID = deliverID
        express.deliverman.save()
    except DeliverMan.DoesNotExist, e:
        deliverman = DeliverMan.objects.create(express=express, deliverPhone=deliverPhone,deliverID=deliverID)
        deliverman.save()
    # 5.save pos
    express.pos = pos
    express.save()
    # Todo:add if else
    # 6.create response
    feedback = '位置已上传'
    response = {'feedback':feedback}
    return JsonResponse(response)

@csrf_exempt
def find(request):
    # 1.decrypt the message
    # message = decrypt.decryptMessage(request.GET['ciphertext'])

    # dictMessage = json.loads(message)
    # 2.get info
    rcvName = decrypt.decryptMessage(request.POST['rcvName'])
    rcvPhone = decrypt.decryptMessage(request.POST['rcvPhone'])
    code = decrypt.decryptMessage(request.POST['code'])
    # 3.get express
    try:
        express = Express.objects(code=code)
    except Express.DoesNotExist, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': feedback}
        return JsonResponse(response)
    # 4.check info
    if express.receive_phone != rcvPhone or express.receive_name.encode("utf-8") != rcvName:
        feedback = '对不起，您的信息有误'
        response = {'feedback': feedback}
	#response = {'rcvName':rcvName,'rcvPhone':rcvPhone,'receive_name':express.receive_name,'receive_phone':express.receive_phone}
	return JsonResponse(response)
    # 5. get pos
    pos = express.pos
    response = {'pos':pos}
    return JsonResponse(response)

@csrf_exempt
def distribute(request):
    # message = decrypt.decryptMessage(request.GET['ciphertext'])
    # dictMessage = json.loads(message)
    decryptmessage = decrypt.decryptMessage(request.POST['message'])
    deliverPhone = decrypt.decryptMessage(request.POST['deliverPhone'])
    deliverID = decrypt.decryptMessage(request.POST['deliverID'])

    # decryptmessage = decrypt.decryptMessage(encryptmessage)
    dictdecryptmessage = json.loads(decryptmessage)
    # using code to get the express object

    code = dictdecryptmessage['code']
    try:
        express = Express.objects(code=code)
    except Express.DoesNotExist, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': feedback}
        return JsonResponse(response)
    rcvName =  express.receive_name
    rcvAddress = express.receive_address
    goods = express.goods
    rcvPhone = express.receive_phone
    # saving deliverPhone into database
    # Todo:the Chinese character in the message have bugs
    try:
        express.deliverman.deliverPhone = deliverPhone
        express.deliverman.deliverID = deliverID
        express.deliverman.save()
    except DeliverMan.DoesNotExist,e:
        deliverman = DeliverMan.objects.create(express=express, deliverPhone=deliverPhone)
        deliverman.save()
    # send message to receiver and return the response
    #response_temp =  sendmessage.distribute(rcvName,goods,rcvAddress,code,rcvPhone,deliverPhone)

    rcvName = rcvName.encode('utf-8')
    goods = goods.encode('utf-8')
    rcvAddress = rcvAddress.encode('utf-8')
    code = code.encode('utf-8')
    rcvPhone = rcvPhone.encode('utf-8')
    deliverPhone = deliverPhone.encode('utf-8')
    response_temp =  sendmessage.distribute(rcvName,goods,rcvAddress,code,rcvPhone,deliverPhone)
    #response = {'rcvName': rcvName,'goods':goods,'rcvAddress':rcvAddress,'code':code,'rcvPhone':rcvPhone,'deliverPhone':deliverPhone}
    #return JsonResponse(response)

    dictresponse_temp = json.loads(response_temp)
    status = dictresponse_temp["resp"]["respCode"]
    if status == '000000':
        feedback = '短信发送成功'
    else:
        feedback = '短信发送失败'
    response = {'feedback':feedback}
    return JsonResponse(response)

@csrf_exempt
def auth(request):

    decryptmessage = decrypt.decryptMessage(request.POST['message'])
    rcvPhone = decrypt.decryptMessage(request.POST['rcvPhone'])
    dictdecryptmessage = json.loads(decryptmessage)
    code = dictdecryptmessage['code']
    # using code to get the express object
    try:
        express = Express.objects(code=code)
    except Express.DoesNotExist, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': feedback}
        return JsonResponse(response)
    # if auth fails ,send warning message to the deliverman
    # Todo: response has a lot to consider

    flag = 1
    try:
        if express.receive_phone != rcvPhone:
            sendmessage.warn(code, express.deliverman.deliverPhone)
            flag = 0
            response = '抱歉，手机号验证失败'
        else:
            response = '恭喜，手机号验证成功，稍后我们会给您发送一条验证码，请耐心等待'
    except DeliverMan.DoesNotExist,e:
        response = '对不起，该快件没有对应的快递员'

    jsonResponse = {'flag':flag,'response':response}
    return JsonResponse(jsonResponse)

@csrf_exempt
def getVerify(request):
    decryptmessage = decrypt.decryptMessage(request.POST['message'])
    dictdecryptMessage = json.loads(decryptmessage)
    code = dictdecryptMessage['code']

    try:
        express = Express.objects(code=code)
    except Express.DoesNotExist, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': feedback}
        return JsonResponse(response)

    rcvPhone = express.receive_phone
    verifyCode = (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(16))))[0:6]

    # send message
    response = sendmessage.getVerify(verifyCode=verifyCode,rcvPhone=rcvPhone)

    dictResponse = json.loads(response)
    # Todo:if send 10 or more messages there'll be an exception
    try:
        createDate =  dictResponse["resp"]["templateSMS"]["createDate"]
        # saving verifycode into database

        express.verifycode.verifycode = verifyCode
        express.verifycode.codedate = createDate
        express.verifycode.save()

        feedback = '验证码已发送'
    except KeyError ,e:
        feedback = '请求过于频繁，请稍后再试'
    except VerifyCode.DoesNotExist,e:
        verifycode = VerifyCode.objects.create(express=express, verifycode=verifyCode, codedate=createDate)
        verifycode.save()
        feedback = '验证码已发送'

    response = {'feedback':feedback}
    return JsonResponse(response)

@csrf_exempt
def authVerify(request):

    verify = decrypt.decryptMessage(request.POST['verify'])
    decryptmessage = decrypt.decryptMessage(request.POST['message'])

    # decryptmessage = decrypt.decryptMessage(encryptmessage)
    dictdecryptmessage = json.loads(decryptmessage)
    code = dictdecryptmessage['code']

    try:
        express = Express.objects(code=code)
    except Express.DoesNotExist, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': feedback}
        return JsonResponse(response)
    # 1.during 3 minutes
    try:
        past = int(express.verifycode.codedate)
        now = int(datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S'))
        timePeriod = now - past
        feedback = '验证失败'
        if timePeriod < 300:
            # 2.verifycode must be the same and the code should be used only once
            if verify == express.verifycode.verifycode and express.verifycode.codestatus == False:
                feedback = '验证成功'
                sendmessage.succeedVerify(code=code, deliverPhone=express.deliverman.deliverPhone)
                express.verifycode.codestatus = True
                express.verifycode.save()
        else:
            sendmessage.warn(code=code, deliverPhone=express.deliverman.deliverPhone)
    except VerifyCode.DoesNotExist,e:
        feedback = '很抱歉，数据库没有该快件的验证码，无法进行验证'
    except DeliverMan.DoesNotExist,e:
        feedback = '对不起，该快件没有对应的快递员'


    response = {'feedback':feedback}

    return JsonResponse(response)

# test for mongoengine ORM
def employee(request):
    employee = Employee.objects.create(
        email = "1971990184@qq.com",
        first_name = "Pedro",
        last_name = "Kong"
    )
    employee.save()
    feedback = 'succeed'
    return JsonResponse({'feedback':feedback})