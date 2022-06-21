from django import forms

class CreateLeaseForm(forms.Form):
    code = forms.CharField(max_length=10)
    duration = forms.IntegerField(min_value=1, max_value=12)