#-*- coding: UTF-8 -*-
#
# 具体定义和参数说明参考 云之讯REST开发者文档 .docx
#
import base64
import datetime
import urllib2
import md5

# 返回签名
def getSig(accountSid,accountToken,timestamp):
	sig = accountSid + accountToken + timestamp
	return md5.new(sig).hexdigest().upper()

#生成授权信息
def getAuth(accountSid,timestamp):
	src = accountSid + ":" + timestamp
	return base64.encodestring(src).strip()

#发起http请求
def urlOpen(req,data=None):
	try:
		res = urllib2.urlopen(req,data)
		data = res.read()
		res.close()
	except urllib2.HTTPError, error:
		data = error.read()
		error.close()
	return data

#生成HTTP报文
def createHttpReq(req,url,accountSid,timestamp,responseMode,body):
	req.add_header("Authorization", getAuth(accountSid,timestamp))
	if responseMode:
		req.add_header("Accept","application/"+responseMode)
		req.add_header("Content-Type","application/"+responseMode+";charset=utf-8")
	if body:
		req.add_header("Content-Length",len(body))
		req.add_data(body)
	return req

# 参数意义说明
# accountSid 主账号
# accountToken 主账号token
# clientNumber 子账号
# appId 应用的ID
# clientType 计费方式。0  开发者计费；1 云平台计费。默认为0.
# charge 充值或回收的金额
# friendlyName 昵称
# mobile 手机号码
# isUseJson 是否使用json的方式发送请求和结果。否则为xml。
# start 开始的序号，默认从0开始
# limit 一次查询的最大条数，最小是1条，最大是100条
# responseMode 返回数据个格式。"JSON" "XML"
# chargeType  0 充值；1 回收。
# fromClient 主叫的clientNumber
# toNumber 被叫的号码
# toSerNum 被叫显示的号码
# verifyCode 验证码内容，为数字和英文字母，不区分大小写，长度4-8位
# displayNum 被叫显示的号码
# templateId 模板Id
class RestAPI:

	HOST = "https://api.ucpaas.com"
	PORT = ""
	SOFTVER = "2014-06-30"
	JSON = "json"
	XML = "xml"

	#主账号信息查询
	#accountSid  主账号ID
	#accountToken 主账号的Token
	def getAccountInfo(self,accountSid,accountToken,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "?sig=" + signature

		if isUseJson == True:
			responseMode = self.JSON
		else:
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,None))


	#申请client账号
	#accountSid  主账号ID
	#accountToken 主账号的Token
	#appId 应用ID
	#clientType 计费方式。0  开发者计费；1 云平台计费。默认为0.
	#charge 充值的金额
	#friendlyName 昵称
	#mobile 手机号码
	def applyClient(self,accountSid,accountToken,appId,clientType,charge,friendlyName,mobile,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Clients?sig=" + signature

		if isUseJson == True:
			body = '{"client":{"appId":"%s","clientType":"%s","charge":"%s","friendlyName":"%s","mobile":"%s"}}'\
				%(appId,clientType,charge,friendlyName,mobile)
			responseMode = self.JSON
		else:
			body = '<?xml version="1.0" encoding="utf-8"?>\
					<client>\
						<appId>%s</appId>\
						<clientType>%s</clientType>\
						<charge>%s</charge>\
						<friendlyName>%s</friendlyName>\
						<mobile>%s</mobile>\
					</client>\
					'%(appId,clientType,charge,friendlyName,mobile)
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,body))


	#释放client账号
	#accountSid  主账号ID
	#accountToken 主账号的Token
	#clientNumber 子账号
	#appId 应用ID
	def ReleaseClient(self,accountSid,accountToken,clientNumber,appId,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/dropClient?sig=" + signature

		if isUseJson == True:
			body = '{"client":{"clientNumber":"%s","appId":"%s"}}'%(clientNumber,appId)
			responseMode = self.JSON
		else:
			body = '<?xml version="1.0" encoding="utf-8"?>\
					<client>\
						<clientNumber>%s</clientNumber>\
						<appId>%s</appId >\
					</client>\
					'%(clientNumber,appId)
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,body))


	#获取client账号
	#accountSid  主账号ID
	#accountToken 主账号的Token
	#appId 应用ID
	#start 开始的序号，默认从0开始
	#limit 一次查询的最大条数，最小是1条，最大是100条
	def getClientList(self,accountSid,accountToken,appId,start,limit,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/clientList?sig=" + signature

		if isUseJson == True:
			body = '{"client":{"appId":"%s","start":"%s","limit":"%s"}}'%(appId,start,limit)
			responseMode = self.JSON
		else:
			body = "<?xml version='1.0' encoding='utf-8'?>\
					<client>\
						<appId>%s</appId>\
						<start>%s</start>\
						<limit>%s</limit>\
					</client>\
					"%(appId,start,limit)
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,body))


	#client信息查询 注意为GET方法
	#accountSid  主账号ID
	#accountToken 主账号的Token
	#appId 应用ID
	#clientNumber 子账号
	def getClientInfo(self,accountSid,accountToken,appId,clientNumber,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Clients?sig=" + signature \
			+"&clientNumber="+clientNumber+"&appId="+appId

		if isUseJson == True:
			body = '{"client":{"appId":"%s","clientNumber":"%s"}}'%(appId,clientNumber)
			responseMode = self.JSON
		else:
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,None))

        #client信息查询(mobile方式) 注意为GET方法
	#accountSid  主账号ID
	#accountToken 主账号的Token
	#appId 应用ID
	#mobile 手机号
	def getClientInfoByMobile(self,accountSid,accountToken,appId,mobile,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/ClientsByMobile?sig=" + signature \
			+"&mobile="+mobile+"&appId="+appId

		if isUseJson == True:
			body = '{"client":{"appId":"%s","mobile":"%s"}}'%(appId,mobile)
			responseMode = self.JSON
		else:
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,None))

	#应用话单下载
	#accountSid 主账号ID
	#accountToken 主账号Token
	#appId 应用ID
	#date 枚举类型 day 代表前一天的数据（从00:00 – 23:59）；week代表前一周的数据(周一 到周日)；month表示上一个月的数据
	def getBillList(self,accountSid,accountToken,appId,date,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/billList?sig=" + signature

		if isUseJson == True:
			body = '{"appBill":{"appId":"%s","date":"%s"}}'%(appId,date)
			responseMode = self.JSON
		else:
			body = "<?xml version='1.0' encoding='utf-8'?>\
					<appBill>\
						<appId>%s</appId>\
						<date>%s</date>\
					</appBill>\
					"%(appId,date)
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,body))



	#通用话单下载URL
	# def getAccountInfo(accountSid,accountToken,isUseJson=True):
	# now = datetime.datetime.now()
	# timestamp = now.strftime("%Y%m%d%H%M%S")
	# signature = getSig(accountSid,accountToken,timestamp)
	# url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "?sig=" + signature

	# req = urllib2.Request(url)
	# self.setHttpHeader(req)
	# req.add_header("Authorization", getAuth(accountSid,timestamp))
	# if isUseJson == True:
		# responseMode = self.JSON
	# else:
		# responseMode = self.XML
	# req.add_header("Accept","application/"+responseMode)

	# return urlOpen(req)

	#client话单下载
	#accountSid 主账号ID
	#accountToken 主账号Token
	#appId 应用ID
	#clientNumber 子账号ID
	#date 枚举类型 day 代表前一天的数据（从00:00 – 23:59）；week代表前一周的数据(周一 到周日)；month表示上一个月的数据
	def getClientBillList(self,accountSid,accountToken,appId,clientNumber,date,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Clients/billList?sig=" + signature

		if isUseJson == True:
			body = '{"clientBill":{"appId":"%s","clientNumber":"%s","date":"%s"}}'%(appId,clientNumber,date)
			responseMode = self.JSON
		else:
			body = "<?xml version='1.0' encoding='utf-8'?>\
					<clientBill>\
						<appId>%s</appId>\
						<clientNumber>%s</clientNumber>\
						<date>%s</date>\
					</clientBill>\
					"%(appId,clientNumber,date)
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,body))


	#client充值
	#accountSid 主账号ID
	#accountToken 主账号Token
	#appId 应用ID
	#clientNumber 子账号ID
	#chargeType  0 充值；1 回收。
	#charge 充值的金额
	def chargeClient(self,accountSid,accountToken,appId,clientNumber,chargeType,charge,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/chargeClient?sig=" + signature

		if isUseJson == True:
			body = '{"client":{"appId":"%s","clientNumber":"%s","chargeType":"%s","charge":"%s"}}'%(appId,clientNumber,chargeType,charge)
			responseMode = self.JSON
		else:
			body = "<?xml version='1.0' encoding='utf-8'?>\
					<client>\
						<appId>%s</appId>\
						<clientNumber>%s</clientNumber>\
						<chargeType>%s</chargeType>\
						<charge>%s</charge>\
					</client>\
					"%(appId,clientNumber,chargeType,charge)
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,body))


	#双向回拨
	#accountSid 主账号ID
	#accountToken 主账号Token
	#appId 应用ID
	#fromClient 主叫的clientNumber
	#toNumber 被叫的号码
	#maxallowtime 允许的最大通话时长
	def callBack(self,accountSid,accountToken,appId,fromClient,to,fromSerNum,toSerNum,maxAllowTime,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST +  "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Calls/callBack?sig=" + signature
		print("url:%s"%url)
		if isUseJson == True:
			body = '{"callback":{ "appId":"%s","fromClient":"%s","to":"%s", "fromSerNum" : "%s","toSerNum"   : "%s"}}'%(appId,fromClient,to,fromSerNum,toSerNum,maxAllowTime)
			responseMode = self.JSON
			print(body)
		else:
			body = "<?xml version='1.0' encoding='utf-8'?>\
					<callback>\
						<appId>%s</appId>\
						<fromClient>%s</fromClient>\
						<to>%s</to>\
						<fromSerNum>%s</fromSerNum>\
						<toSerNum>%s</toSerNum>\
						<maxallowtime>%s</maxallowtime>\
					</callback>\
					"%(appId,fromClient,to,fromSerNum,toSerNum,maxAllowTime)
			responseMode = self.XML
			print("body:%s"%body)
		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,body))


	# 语音验证码
	#accountSid 主账号ID
	#accountToken 主账号Token
	#appId 应用ID
	#verifyCode 验证码内容，为数字和英文字母，不区分大小写，长度4-8位
	#toNumber 被叫的号码
	def voiceCode(self,accountSid,accountToken,appId,verifyCode,toNumber,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Calls/voiceCode?sig=" + signature

		if isUseJson == True:
			body = '{"voiceCode":{ "appId":"%s","verifyCode":"%s","to":"%s"}}'%(appId,verifyCode,toNumber)
			responseMode = self.JSON

		else:
			body = "<?xml version='1.0' encoding='utf-8'?>\
					<voiceCode>\
						<appId>%s</appId>\
						<verifyCode>%s</verifyCode>\
						<to>%s</to>\
					</voiceCode>\
					"%(appId,verifyCode,toNumber)
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,body))


	#短信验证码（模板短信）
	#accountSid 主账号ID
	#accountToken 主账号Token
	#appId 应用ID
	#toNumber 被叫的号码
	#templateId 模板Id
	#param <可选> 内容数据，用于替换模板中{数字}
	def templateSMS(self,accountSid,accountToken,appId,toNumbers,templateId,param,isUseJson=True):
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y%m%d%H%M%S")
		signature = getSig(accountSid,accountToken,timestamp)
		url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Messages/templateSMS?sig=" + signature

		if isUseJson == True:
			body = '{"templateSMS":{ "appId":"%s","to":"%s","templateId":"%s","param":"%s"}}'%(appId,toNumbers,templateId,param)
			responseMode = self.JSON
		else:
			body = "<?xml version='1.0' encoding='utf-8'?>\
					<templateSMS>\
						<appId>%s</appId>\
						<to>%s</to>\
						<templateId>%s</templateId>\
						<param>%s</param>\
					</templateSMS>\
					"%(appId,toNumbers,templateId,param)
			responseMode = self.XML

		req = urllib2.Request(url)
		return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,body))

def distribute(rcvName,goods,rcvAddress,code,rcvPhone,deliverPhone):
	test = RestAPI()

	accountSid = "33794bdc8d67381a8b15525d34e71497"
	accountToken = "a1e13e2d02168478d5090d261c8336e9"
	appId = "c6428977adc24007aef6068e239d7724"


	isUseJson = True

    # toNumber="18161251991"
	toNumber=rcvPhone

	templateId="23442"

	param=rcvName+','+code+','+goods+','+rcvAddress+','+deliverPhone
    # param="ryh,336,气球,电子科大"

	#短信
	return test.templateSMS(accountSid,accountToken,appId,toNumber,templateId,param,isUseJson)


def warn(code,deliverPhone):
	test = RestAPI()

	accountSid = "33794bdc8d67381a8b15525d34e71497"
	accountToken = "a1e13e2d02168478d5090d261c8336e9"
	appId = "c6428977adc24007aef6068e239d7724"

	isUseJson = True

	toNumber = deliverPhone

	templateId = "23525"

	param=code

	return test.templateSMS(accountSid, accountToken, appId, toNumber, templateId, param, isUseJson)

def getVerify(verifyCode,rcvPhone):
    test = RestAPI()

    accountSid = "33794bdc8d67381a8b15525d34e71497"
    accountToken = "a1e13e2d02168478d5090d261c8336e9"
    appId = "c6428977adc24007aef6068e239d7724"

    isUseJson = True

    toNumber = rcvPhone

    templateId = "23540"

    param = verifyCode+','+'3'

    return test.templateSMS(accountSid, accountToken, appId, toNumber, templateId, param, isUseJson)

def succeedVerify(code,deliverPhone):
    test = RestAPI()

    accountSid = "33794bdc8d67381a8b15525d34e71497"
    accountToken = "a1e13e2d02168478d5090d261c8336e9"
    appId = "c6428977adc24007aef6068e239d7724"

    isUseJson = True

    toNumber = deliverPhone

    templateId = "23576"

    param = code

    return test.templateSMS(accountSid, accountToken, appId, toNumber, templateId, param, isUseJson)
