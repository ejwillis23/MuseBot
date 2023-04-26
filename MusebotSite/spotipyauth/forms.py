from django import forms
from django.forms import ModelForm, TextInput

class NameForm(forms.Form):
    your_name = forms.CharField(label='Enter your Discord name and discriminator', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'YourName#0000', 'style': 'width: 300px;', 'class': 'form-control'}))
    token = forms.CharField(label='Token (do not change)', max_length=500)

class CheckForm(forms.Form):
    your_name = forms.CharField(label='Your Dicord name and discriminator', max_length=100)