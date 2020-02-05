from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from .models import User as User_db, Conversation, Message, Participant
from .forms import *

def index(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect("/web/chats/")
	
	return HttpResponseRedirect("/web/auth/")
	
def registration(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect("/web/chats/")
	
	if request.method == 'POST':
		form = Registration(request.POST)
		if form.is_valid():
			input_email = request.POST.get("email")
			input_password = request.POST.get("password")
			input_nickname = request.POST.get("nickname")
			
			if (User.objects.filter(username=input_nickname).exists())!=True: #проверка на существование с таким ником
				user = User.objects.create_user(input_nickname, input_email, input_password)
				user.save()
				user_db = User_db(nickname=input_nickname)
				user_db.save()
				return render(request, "web/registration_complete.html") #пересылка на страницу по типу "вы успешно зарегистрировались, идите логинится"
			else:
				context="Account with nickname '{0}' already exist".format(input_nickname)
				return render(request, "web/auth_error.html", {"context": context})
				
	form = Registration()
	return render(request, "web/registration.html", {"form": form})	
	
def auth(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect("/web/chats/") #если уже аутенфицирован - отослать на -Луну- страницу чатов
		
	form = Authorisation(request.POST or None)

	if request.method == 'POST': #если POST-запрос с данными
		username_input = request.POST.get('username', None)
		password_input = request.POST.get('password', None)
		user = authenticate(username=username_input, password=password_input)
		if user is not None:
			
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect("/web/chats/") #успешный логин, перенаправление на страницу чатов
				
			else:
				context = "Auth cant be done!"
				return render(request, "web/auth_error.html", {"context": context}) 
		else:
			context = "Auth cant be done, invalid login!"
			return render(request, "web/auth_error.html", {"context": context})
			
	return render(request, "web/auth.html", {"form": form})	#если GET-запрос

def registration_complete(request):	
	if request.user.is_authenticated() is not True:
		return HttpResponseRedirect("/web/auth/")
	
	return render(request, "web/registration_complete.html")

def login_out(request):
	if request.user.is_authenticated():
		logout(request)
		return render(request, "web/logout.html")
	else:
		return HttpResponseRedirect("/web/auth/")
	
def chats(request):
	#ДОБАВИТЬ ВЫВОД ПОСЛЕДНИХ СООБЩЕНИЙ И ИХ АВТОРОВ
	
	if request.user.is_authenticated() is not True:
		return HttpResponseRedirect("/web/auth/")
	else:
		user_object = User_db.objects.get(nickname = request.user.username)
		chat_form = NameInput()
		if request.method == 'POST': #если POST-запрос на создание нового чата
			new_title = request.POST.get("name")
			c = Conversation(creator=user_object, title=new_title)
			c.save()
			p = Participant(participant=user_object, conversation=c)
			p.save()
	
		participants_set=Participant.objects.filter(participant=user_object.id)
		chat_list=[]
		
		for participant in participants_set:
			chat_list.append({'chat_id': participant.conversation_id, 'chat_title':Conversation.objects.get(id=participant.conversation_id).title})
			
		context={'chat_list': chat_list, 'chat_form':chat_form}
		return render(request, "web/chats.html", context)
		
def chat_messages(request, chat_id):
	if request.user.is_authenticated() is not True:
		return HttpResponseRedirect("/web/auth/")
	
	user_object = User_db.objects.get(nickname = request.user.username)
	try: #проверка, есть ли пользователь в этом чате
		if Participant.objects.filter(participant=user_object, conversation=Conversation.objects.get(id=chat_id)).exists() != True:
			return HttpResponseRedirect("/web/chats/") #если нет-выкидываем обратно
			
	except ObjectDoesNotExist: #если пытались получить доступ к несуществующему чату
		raise Http404("Chat does not exist")
		
	if request.method == 'POST': 
		#если POST-запрос с новым сообщением
		if request.POST.get("button") == "Send message":
			message_form = MessageInput(request.POST, request.FILES)
			if message_form.is_valid():
				input_message = request.POST.get("message")
				m = Message(message_text=input_message, conversation=Conversation.objects.get(id=chat_id), sender=user_object, attachment=request.FILES.get('file'))
				m.save()
		else:
		#Добавление нового юзера в этот чат
			participant_form = NameInput(request.POST)
			if participant_form.is_valid():
				new_participant_nickname = request.POST.get("name")
				try:
					new_participant=User_db.objects.get(nickname=new_participant_nickname)
				except ObjectDoesNotExist: #если пытались пригласить несуществующего юзера
					return HttpResponseRedirect("/web/chats/{0}/".format(chat_id))
					
				if (Participant.objects.filter(conversation=chat_id).filter(participant=new_participant).exists())!= True:
					p=Participant(conversation=Conversation.objects.get(id=chat_id), participant=new_participant)
					p.save()
		
	message_form=MessageInput()
	participant_form = NameInput()
	messages_list = Message.objects.filter(conversation=chat_id).order_by('id')[:50] #Вывод последних 50-ти сообщений из такого-то чата
	
	participants_set=Participant.objects.filter(conversation=chat_id)
	users_list=[]
		
	for user in participants_set:
		users_list.append({'user_nickname': user.participant.nickname})
			
	context={'messages_list': messages_list, "message_form": message_form, "participant_form": participant_form, "users_list": users_list, "chat_id": chat_id}
	return render(request, "web/chat.html", context)

def chat_exit(request, chat_id):
	if request.user.is_authenticated() is not True:
		return HttpResponseRedirect("/web/auth/")
	
	user_object = User_db.objects.get(nickname = request.user.username)
	try: #проверка, есть ли пользователь в этом чате
		participant = Participant.objects.filter(participant=user_object, conversation=Conversation.objects.get(id=chat_id))
		if participant.exists() != True:
			return HttpResponseRedirect("/web/chats/") #если нет-выкидываем обратно
		else:
			participant.delete()
		return HttpResponseRedirect("/web/chats/")
	except ObjectDoesNotExist: #если пытались пригласить несуществующего юзера
		return HttpResponseRedirect("/web/chats/{0}/".format(chat_id))
				