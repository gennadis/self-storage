from django import forms


class CreateLeaseForm(forms.Form):
    code = forms.CharField(max_length=10)
    duration = forms.IntegerField(min_value=1, max_value=12)


class RequestDeliveryForm(forms.Form):
    lease_id = forms.IntegerField()
    address = forms.CharField(max_length=200)
