from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pic/$',views.pic,name='pic'),
    url(r'^sending/$',views.sending,name='sending')
]
