from django import forms

class Registration(forms.Form):
	email = forms.CharField()
	password = forms.CharField(label=(u"Password"), widget=forms.PasswordInput)
	nickname = forms.CharField()

class Authorisation(forms.Form):
	username = forms.CharField()
	password = forms.CharField(label=(u"Password"), widget=forms.PasswordInput)
	
class MessageInput(forms.Form):
	message = forms.CharField(widget=forms.Textarea)
	file = forms.FileField(required=False)
	
class NameInput(forms.Form):
	name = forms.CharField(label=(u"Nickname"))
