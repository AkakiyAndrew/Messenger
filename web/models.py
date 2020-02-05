from django.db import models

# Create your models here.

class User(models.Model):
	email = models.EmailField() 				#УДАЛИТЬ
	password = models.CharField(max_length=24) 	#УДАЛИТЬ
	nickname = models.CharField(max_length=16)
	active = models.BooleanField(default=False)
	avatar = models.ImageField(upload_to='uploads/')
	
class Conversation(models.Model):
	title = models.CharField(max_length=30)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	
class Message(models.Model):
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
	sender = models.ForeignKey(User, on_delete=models.CASCADE)
	message_text = models.TextField()
	attachment = models.FileField()
	#ДОБАВИТЬ дату
	
class Participant(models.Model):
	participant = models.ForeignKey(User, on_delete=models.CASCADE)
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
