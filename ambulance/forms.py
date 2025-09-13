from .models import Ambulance
from django import forms
from .models import Driver, Dispatch, EmergencyRequest, User


class AmbulanceForm(forms.ModelForm):
    class Meta:
        model = Ambulance
        fields = ["vehicle_number", "equipment_level", "current_status"]
        widgets = {
            "vehicle_number": forms.TextInput(attrs={"class": "form-control"}),
            "equipment_level": forms.Select(attrs={"class": "form-control"}),
            "current_status": forms.Select(attrs={"class": "form-control"}),
        }

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ["firstname", "lastname", "phonenumber"]

class DispatchForm(forms.ModelForm):
    class Meta:
        model = Dispatch
        fields = ["request", "ambulance", "driver"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['request'].queryset = EmergencyRequest.objects.filter(status="pending")
        self.fields["ambulance"].queryset = Ambulance.objects.filter(current_status="available")
        self.fields["driver"].queryset = Driver.objects.all()


class EmergencyRequestForm(forms.ModelForm):
    class Meta:
        model = EmergencyRequest
        fields = ["hospital_name", "hospital_address", "pickup_address", "request_type"]
        widgets = {
            "hospital_name": forms.TextInput(attrs={"class": "form-control"}),
            "hospital_address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "customer_mobile": forms.TextInput(attrs={"class": "form-control"}),
            "pickup_address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "request_type": forms.Select(attrs={"class": "form-control"}),
        }

class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["firstname", "lastname", "email", "phonenumber", "password", "date_of_birth", "address"]
        widgets = {
            "firstname": forms.TextInput(attrs={"class": "form-control"}),
            "lastname": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phonenumber": forms.TextInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
        }
        def save(self, commit=True, make_admin=False):
            user = super().save(commit=False)
            user.set_password(self.cleaned_data['password'])
            if make_admin:
                user.is_admin = True
            if commit:
                user.save()
            return user

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': ' '
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': ' '
    }))