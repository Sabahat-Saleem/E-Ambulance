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
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ["firstname", "lastname", "email", "phonenumber", "password", "confirm_password", "date_of_birth", "address"]
        widgets = {
            "password": forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())