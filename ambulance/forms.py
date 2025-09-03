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
        # Only show pending requests
        self.fields["request"].queryset = EmergencyRequest.objects.filter(status="pending")
        # Show meaningful text for requests
        self.fields["request"].label_from_instance = (
            lambda obj: f"{obj.emergency_type} - {obj.description[:30]} (#{obj.requestid})"
        )
        # Only available ambulances
        self.fields["ambulance"].queryset = Ambulance.objects.filter(current_status="available")
        # Drivers (all for now, can filter later)
        self.fields["driver"].queryset = Driver.objects.all()

class EmergencyRequestForm(forms.ModelForm):
    class Meta:
        model = EmergencyRequest
        fields = ["description"]   # user auto-fill hoga, status default pending
        widgets = {
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
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


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': ' '
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': ' '
    }))