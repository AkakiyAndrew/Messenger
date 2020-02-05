from django.conf.urls import url

from . import views

app_name = 'web'
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^auth/$', views.auth, name='auth'),
	url(r'^auth/new/$', views.registration, name='registration'),
	url(r'^auth/new/complete/$', views.registration_complete, name='registration_complete'), 
	url(r'^logout/$', views.login_out, name='logout'),
	url(r'^chats/$', views.chats, name='chats'), 
	url(r'^chats/(?P<chat_id>[0-9]+)/$', views.chat_messages, name='chat_messages'), 
	url(r'^chats/(?P<chat_id>[0-9]+)/exit/$', views.chat_exit, name='chat_exit'), 
]