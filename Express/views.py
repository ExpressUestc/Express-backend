# coding:utf8
import datetime
import json
import os
import sys

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

import Express.utils.sendmessage
from Express.models import Express,DeliverMan,VerifyCode,AuthDeliver
from Express.shortestPath.findShortest import getPath
from Express.tasks import sendMessage
from Express.utils import decrypt, sendmessage
from Express.utils.encrypt import encrypt
from Express.utils.tools import decryptPostInfo
from Expressbackend.celery import app
from models import Employee

reload(sys)

sys.setdefaultencoding('utf8')

@csrf_exempt
def test(request):
    return HttpResponse('This is test')

# Create your views here.
@csrf_exempt
def index(request):

    # 1.get info from the request
    fields = ['myName','myPhone','myAddress','myPostcode','extraPrice',
        'rcvName','rcvPhone','rcvAddress','rcvPostcode','goods','expressCompany',
        'remarks','rcvCity','sendCity','key']

    myName,myPhone,myAddress,myPostcode,extraPrice,rcvName,rcvPhone,rcvAddress,rcvPostcode,goods,expressCompany,remarks,rcvCity,sendCity,key = decryptPostInfo(request,fields)

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
    # Todo:encrypt info in db
    express = Express.objects.create(send_name=myName,send_phone=myPhone,send_address=myAddress,send_postcode=myPostcode,
                    extra_price=extraPrice,receive_name=rcvName,receive_phone=rcvPhone,receive_address=rcvAddress,receive_postcode=rcvPostcode,goods=goods,express_company=expressCompany,remarks=remarks,
                    code=code,receive_city=rcvCity,send_city=sendCity)
    express.path,express.time = getPath(sendCity.encode('utf-8'),rcvCity.encode('utf-8'))
    express.save()

    # 7.create response
    # url = 'http://101.201.79.95/express/pic/?code='+code
    # Todo:use AES to encrypt response
    response = {'code':encrypt(key,code)}
    return JsonResponse(response)

def pic(request):
    code = request.GET['code']
    return render_to_response('Express/showQrcode.html',{'image':code+'.png'})

@csrf_exempt
def authDeliver(request):

    fields = ['deliverPhone','deliverID','key']
    deliverPhone,deliverID,key = decryptPostInfo(request,fields)
    
    flag = '1'
    try:
        deliverman = AuthDeliver.objects(deliverPhone=deliverPhone,deliverID=deliverID)
        deliverman = deliverman[0]
    except IndexError,e:
        flag = '0'

    response = {'flag':encrypt(key,flag)}

    return JsonResponse(response)

@csrf_exempt
def sending(request):

    # 2.get info
    fields = ['message','pos','city','deliverPhone','deliverID','key']
    decryptmessage,pos,city,deliverPhone,deliverID,key = decryptPostInfo(request,fields)

    # get decryptmessage
    # decryptmessage = decrypt.decryptMessage(encryptmessage)
    dictdecryptmessage = json.loads(decryptmessage)

    code = dictdecryptmessage['code']

    # 3.get express
    try:
        express = Express.objects(code=code)
        express = express[0]
    except IndexError,e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback':encrypt(key,feedback)}
        return JsonResponse(response)

    if express.auth == False:
        return JsonResponse({'feedback':encrypt(key,'抱歉，您的快递单未经验证，无法转运')})

    # 4.save deliverPhone
    deliverman = DeliverMan.objects.create(deliverPhone=deliverPhone, deliverID=deliverID)
    deliverman.save()
    express.update(push__deliverman=deliverman)

    final = False
    if city.encode('utf-8') == express.path[-1]:
        final = True

    if not final:
        try:
            duration = express.time[express.path.index(city.encode('utf-8'))]
        except ValueError,e:
            return JsonResponse({'feedback':encrypt(key,'你转运的城市不在最短路上，转运失败！')})
    #duration = 0.05
    upload_time = datetime.datetime.now()

    try:
        city_gap = express.path.index(city.encode('utf-8'))-express.path.index(express.city.encode('utf-8'))
        if upload_time<express.message_time and city_gap == 1:
            express.pos = pos
            express.city = city
            app.AsyncResult(express.task_id).revoke()
            if not final:
                message_time = express.message_time+datetime.timedelta(hours=duration)
                express.message_time = message_time
                result = sendMessage.apply_async(args=[express.code, city, duration, express.receive_phone],
                                                 eta=message_time + datetime.timedelta(hours=-8))
                express.task_id = result.task_id
        else:
            response = {'feedback': encrypt(key,'抱歉，不在下一站或者转运超时，位置上传失败')}
            return JsonResponse(response)
    except AttributeError,e:
        express.city = city
        express.pos = pos
        if not final:
            message_time = upload_time + datetime.timedelta(hours=duration)
            express.message_time = message_time
            result = sendMessage.apply_async(args=[express.code, city, duration,express.receive_phone],
                                             eta=message_time + datetime.timedelta(hours=-8))
            express.task_id = result.task_id
        #response = sendmessage.lostAlarm(express.code,city,duration,express.receive_phone)
        #return HttpResponse(response)


    # test celery
    # test_time = now_time+datetime.timedelta(hours=-8,seconds=30)
    # testCelery.apply_async(eta=test_time)

    express.save()

    # Todo:add if else
    # 6.create response
    if final:
        feedback = '位置已上传'
    else:
        feedback = '位置已上传,下一站是'+express.path[express.path.index(city.encode('utf-8'))+1].encode('utf-8')
    response = {'feedback':encrypt(key,feedback)}
    return JsonResponse(response)

@csrf_exempt
def find(request):
    # 2.get info
    fields = ['rcvName','rcvPhone','code','key']
    rcvName,rcvPhone,code,key = decryptPostInfo(request,fields)
    # 3.get express
    try:
        express = Express.objects(code=code)
        # cause previous express is queryset so use the following code to get
        # real item
        express = express[0]
    except IndexError, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': encrypt(key,feedback)}
        return JsonResponse(response)
    # 4.check info
    if express.receive_phone != rcvPhone or express.receive_name.encode("utf-8") != rcvName:
        feedback = '对不起，您的信息有误'
        response = {'feedback': encrypt(key,feedback)}
	#response = {'rcvName':rcvName,'rcvPhone':rcvPhone,'receive_name':express.receive_name,'receive_phone':express.receive_phone}
	return JsonResponse(response)
    # 5. get pos
    pos = express.pos
    response = {'pos':encrypt(key,pos.encode('utf-8'))}
    return JsonResponse(response)

@csrf_exempt
def distribute(request):
    # message = decrypt.decryptMessage(request.GET['ciphertext'])
    # dictMessage = json.loads(message)
    fields = ['message','deliverPhone','deliverID','key']
    decryptmessage, deliverPhone, deliverID, key = decryptPostInfo(request,fields)

    dictdecryptmessage = json.loads(decryptmessage)
    # using code to get the express object

    code = dictdecryptmessage['code']
    try:
        express = Express.objects(code=code)
        express = express[0]
    except IndexError, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': encrypt(key,feedback)}
        return JsonResponse(response)
    rcvName =  express.receive_name
    rcvAddress = express.receive_address
    goods = express.goods
    rcvPhone = express.receive_phone
    # saving deliverPhone into database

    deliverman = DeliverMan.objects.create(deliverPhone=deliverPhone, deliverID=deliverID)
    deliverman.save()
    express.update(push__deliverman=deliverman)

    express.save()
    # send message to receiver and return the response
    #response_temp =  sendmessage.distribute(rcvName,goods,rcvAddress,code,rcvPhone,deliverPhone)

    rcvName = rcvName.encode('utf-8')
    goods = goods.encode('utf-8')
    rcvAddress = rcvAddress.encode('utf-8')
    code = code.encode('utf-8')
    rcvPhone = rcvPhone.encode('utf-8')
    deliverPhone = deliverPhone.encode('utf-8')
    response_temp =  sendmessage.distribute(rcvName, goods, rcvAddress, code, rcvPhone, deliverPhone)
    #response = {'rcvName': rcvName,'goods':goods,'rcvAddress':rcvAddress,'code':code,'rcvPhone':rcvPhone,'deliverPhone':deliverPhone}
    #return JsonResponse(response)

    dictresponse_temp = json.loads(response_temp)
    status = dictresponse_temp["resp"]["respCode"]
    if status == '000000':
        feedback = '短信发送成功'
    else:
        feedback = '短信发送失败'
    response = {'feedback':encrypt(key,feedback)}
    return JsonResponse(response)

@csrf_exempt
def auth(request):

    fields = ['message','rcvPhone','key']
    decryptmessage,rcvPhone,key = decryptPostInfo(request,fields)
    dictdecryptmessage = json.loads(decryptmessage)
    code = dictdecryptmessage['code']
    # using code to get the express object
    try:
        express = Express.objects(code=code)
        express = express[0]
    except IndexError, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': encrypt(key,feedback)}
        return JsonResponse(response)
    # if auth fails ,send warning message to the deliverman
    # Todo: response has a lot to consider

    flag = '1'
    try:
        if express.receive_phone != rcvPhone:
            sendmessage.warn(code, express.deliverman.deliverPhone)
            flag = '0'
            response = '抱歉，手机号验证失败'
        else:
            response = '恭喜，手机号验证成功，稍后我们会给您发送一条验证码，请耐心等待'
    except AttributeError,e:
        response = '对不起，该快件没有对应的快递员'

    jsonResponse = {'flag':encrypt(key,flag),'response':encrypt(key,response)}
    return JsonResponse(jsonResponse)

@csrf_exempt
def getVerify(request):

    fields = ['message','key']
    decryptmessage,key = decryptPostInfo(request,fields)
    dictdecryptMessage = json.loads(decryptmessage)
    code = dictdecryptMessage['code']

    try:
        express = Express.objects(code=code)
        express = express[0]
    except IndexError, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': encrypt(key,feedback)}
        return JsonResponse(response)

    rcvPhone = express.receive_phone
    verifyCode = (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(16))))[0:6]

    # send message
    response = sendmessage.getVerify(verifyCode=verifyCode, rcvPhone=rcvPhone)

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
    except AttributeError,e:
        verifycode = VerifyCode.objects.create(verifycode=verifyCode, codedate=createDate)
        verifycode.save()
        express.verifycode = verifycode
        feedback = '验证码已发送'
        
    express.save()
    response = {'feedback':encrypt(key,feedback)}
    return JsonResponse(response)

@csrf_exempt
def authVerify(request):

    fields = ['verify','message','key']
    verify,decryptmessage,key = decryptPostInfo(request,fields)

    # decryptmessage = decrypt.decryptMessage(encryptmessage)
    dictdecryptmessage = json.loads(decryptmessage)
    code = dictdecryptmessage['code']

    try:
        express = Express.objects(code=code)
        express = express[0]
    except IndexError, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': encrypt(key,feedback)}
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
    except AttributeError,e:
        feedback = '很抱歉，该快件没有对应的快递员或者数据库没有该快件的验证码，无法进行验证'


    response = {'feedback':encrypt(key,feedback)}

    return JsonResponse(response)

@csrf_exempt
def authPost(request):

    fields = ['message','key']
    decryptmessage,key = decryptPostInfo(request,fields)
    dictdecryptMessage = json.loads(decryptmessage)
    code = dictdecryptMessage['code']

    try:
        express = Express.objects(code=code)
        express = express[0]
    except IndexError, e:
        feedback = '很抱歉，该快件ＩＤ不存在'
        response = {'feedback': encrypt(key,feedback)}
        return JsonResponse(response)

    express.auth = True
    express.save()
    response = {'flag':encrypt(key,'1')}
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
