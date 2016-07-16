import datetime
from django.db import models
from mongoengine import *


class Express(Document):
    receive_name = StringField(max_length=100)
    receive_phone = StringField(max_length=20)
    receive_address = StringField(max_length=100)
    receive_postcode = StringField(max_length=20)
    goods = StringField(max_length=100)
    express_company = StringField(max_length=20)
    remarks = StringField(max_length=100)
    code = StringField(max_length=15)
    #
    send_name = StringField(max_length=100)
    send_phone = StringField(max_length=20)
    send_address = StringField(max_length=100)
    send_postcode = StringField(max_length=20)
    extra_price = StringField(max_length=20)
    # add position
    pos = StringField(max_length=100)
    #
    deliverman = ReferenceField(DeliverMan,reverse_delete_rule=CASCADE)
    verifycode = ReferenceField(VerifyCode,reverse_delete_rule=CASCADE)

    def __str__(self):
        return self.receive_name+self.receive_phone+self.code

class DeliverMan(Document):
    # express = models.OneToOneField(Express,on_delete=models.CASCADE)
    deliverPhone = StringField(max_length=20)
    deliverID = StringField(max_length=20)

    def __str__(self):
        return "deliverman's phone is %s" % self.deliverPhone


class VerifyCode(Document):
    # express = models.OneToOneField(Express,on_delete=models.CASCADE)
    verifycode = StringField(max_length=10)
    codestatus = BooleanField(default=False)
    codedate = StringField(max_length=20)

class AuthDeliver(Document):
    deliverPhone = StringField(max_length=20)
    deliverID = StringField(max_length=20)

class Employee(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)