from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
    token = forms.CharField(label='Token', max_length=500)

class CheckForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)