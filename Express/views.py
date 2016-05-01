# coding:utf8
import json
import os
import shutil

import qrcode
from django.http import JsonResponse
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, render_to_response
from Express.models import Express,DeliverMan,VerifyCode
import sendmessage
import datetime


# Create your views here.
def index(request):
    # 1.get info from the request
    if request.method == 'GET':
        myName =  request.GET['myName']
        myPhone = request.GET['myPhone']
        myAddress = request.GET['myAddress']
        myPostcode = request.GET['myPostcode']
        extraPrice = request.GET['extraPrice']
        rcvName = request.GET['rcvName']
        rcvPhone = request.GET['rcvPhone']
        rcvAddress = request.GET['rcvAddress']
        rcvPostcode = request.GET['rcvPostcode']
        goods = request.GET['goods']
        expressCompany = request.GET['expressCompany']
        remarks = request.GET['remarks']

    # 2.create random string with 10 characters
    code = (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(16))))[0:10]

    # 3.create Qrcode
    # Todo:optimize the code structure
    q = qrcode.main.QRCode()
    q.add_data(rcvName+'\n'+rcvPhone+'\n'+code)
    q.make()
    m = q.make_image()

    # 4.produce the picture
    m.save(code+'.png')  #qrcode picture's name is 'code'

    # 5.move it to the pointed directory
    shutil.move(code+'.png','static/polls')

    # 6.save the info into the sqlite3
    express = Express(send_name=myName,send_phone=myPhone,send_address=myAddress,send_postcode=myPostcode,
                    extra_price=extraPrice,receive_name=rcvName,receive_phone=rcvPhone,receive_address=rcvAddress,receive_postcode=rcvPostcode,goods=goods,express_company=expressCompany,remarks=remarks,
                    code=code)
    express.save()

    # 7.create response
    # Todo:the url is hard-coded!
    url = 'http://localhost:8000/express/pic/?code='+code
    response = {'code':code,'url':url}
    return JsonResponse(response)

def pic(request):
    code = request.GET['code']
    return render_to_response('Express/showQrcode.html',{'image':code+'.png'})

def sending(request):
    code = request.GET['code']
    pos = request.GET['pos']
    express = Express.objects.get(code=code)
    express.pos = pos
    express.save()
    # Todo:add if else
    feedback = '位置已上传'
    response = {'feedback':feedback}
    return JsonResponse(response)

def find(request):
    rcvName = request.GET['rcvName']
    rcvPhone = request.GET['rcvPhone']
    code = request.GET['code']
    # using code to get the express object
    express = Express.objects.get(code=code)
    # get position
    pos = express.pos
    response = {'pos':pos}
    return JsonResponse(response)

def distribute(request):
    code = request.GET['code']
    deliverPhone = request.GET['deliverPhone']
    # using code to get the express object
    express = Express.objects.get(code=code)
    rcvName =  express.receive_name
    rcvAddress = express.receive_address
    goods = express.goods
    rcvPhone = express.receive_phone
    # saving deliverPhone into database
    # Todo:the Chinese character in the message have bugs
    deliverman = DeliverMan(express =express,deliverPhone=deliverPhone)
    deliverman.save()
    # send message to receiver and return the response
    response = sendmessage.distribute(rcvName,goods,rcvAddress,code,rcvPhone)
    return HttpResponse(response)

def auth(request):
    flag = request.GET['flag']
    code = request.GET['code']
    # using code to get the express object
    express = Express.objects.get(code=code)
    # if auth fails ,send warning message to the deliverman
    # Todo: response has a lot to consider
    if flag == '0':
        response =  sendmessage.warn(code,express.deliverman.deliverPhone)
    else:
        response = None
    return HttpResponse(response)

def getVerify(request):
    code = request.GET['code']
    express = Express.objects.get(code=code)
    rcvPhone = express.receive_phone
    verifyCode = (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(16))))[0:6]
    # send message
    response = sendmessage.getVerify(verifyCode=verifyCode,rcvPhone=rcvPhone)
    # get createDate
    jsonResponse = json.loads(response)
    createDate =  jsonResponse["resp"]["templateSMS"]["createDate"]
    # saving verifycode into database
    verifycode = VerifyCode(express=express,verifycode=verifyCode,codedate=createDate)
    verifycode.save()
    # Todo:add if else
    feedback = '验证码已发送'
    response = {'feedback':feedback}
    return HttpResponse(response)

def authVerify(request):
    verify = request.GET['verify']
    code = request.GET['code']
    express = Express.objects.get(code=code)
    # 1.during 3 minutes
    past =  int(express.verifycode.codedate)
    now = int(datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d%H%M%S'))
    timePeriod = now-past
    feedback = '验证失败'
    if timePeriod<300:
        # 2.verifycode must be the same and the code should be used only once
        if verify == express.verifycode.verifycode and express.verifycode.codestatus==False :
            feedback = '验证成功'
            sendmessage.succeedVerify(code=code,deliverPhone=express.deliverman.deliverPhone)
            express.verifycode.codestatus = True
            express.verifycode.save()
    else:
        sendmessage.warn(code=code,deliverPhone=express.deliverman.deliverPhone)

    response = {'feedback':feedback}

    return HttpResponse(response)
