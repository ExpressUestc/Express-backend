# coding:utf8
import os
import shutil

import qrcode
from django.http import JsonResponse
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, render_to_response
from .models import Express

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
    code = (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(16))))[0:16][0:10]

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