from django import forms


class CreateLeaseForm(forms.Form):
    code = forms.CharField(max_length=10, required=True)
    duration = forms.IntegerField(min_value=1, max_value=12, required=True)


class RequestDeliveryForm(forms.Form):
    lease_id = forms.IntegerField(required=True)
    address = forms.CharField(max_length=200, required=True)
