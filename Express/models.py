import datetime
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible  #used for support python2
class Express(models.Model):
    receive_name = models.CharField(max_length=100)
    receive_phone = models.CharField(max_length=20)
    receive_address = models.CharField(max_length=100)
    receive_postcode = models.CharField(max_length=20)
    goods = models.CharField(max_length=100)
    express_company = models.CharField(max_length=20)
    remarks = models.CharField(max_length=100)
    code = models.CharField(max_length=15)
    #
    send_name = models.CharField(max_length=100)
    send_phone = models.CharField(max_length=20)
    send_address = models.CharField(max_length=100)
    send_postcode = models.CharField(max_length=20)
    extra_price = models.CharField(max_length=20)
    # add position
    pos = models.CharField(max_length=100)

    def __str__(self):
        return self.receive_name+self.receive_phone+self.code


