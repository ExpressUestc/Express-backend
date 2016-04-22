# coding:utf8
import os
import qrcode
from django.http import JsonResponse
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, render_to_response


# Create your views here.
def index(request):
    # 1.get info from the request
    if request.method == 'GET':
        name =  request.GET['name']
        address = request.GET['address']
        phone = request.GET['phone']
    # 2.create Qrcode
    # Todo:Qrcode directory,optimize the code structure
    q = qrcode.main.QRCode()
    q.add_data(name+'\n'+address+'\n'+phone)
    q.make()
    m = q.make_image()
    # 3.create random string with 10 characters
    code = (''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(16))))[0:16][0:10]
    m.save(code+'.png')
    # 4.create response
    # Todo:fix the response
    url = 'http://localhost:8000/express/pic/?code='+code
    response = {'code':code,'url':url}
    return JsonResponse(response)

def pic(request):
    code = request.GET['code']
    return render_to_response('Express/showQrcode.html',{'image':code+'.png'})