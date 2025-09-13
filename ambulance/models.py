from django.db import models
from django.contrib.auth.hashers import make_password
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
class Ambulance(models.Model):
    AMBULANCE_STATUS = [
        ("available", "Available"),
        ("on_call", "On Call"),
        ("maintenance", "Maintenance"),
    ]

    EQUIPMENT_LEVELS = [
        ("basic", "Basic"),
        ("advanced", "Advanced"),
    ]

    ambulanceid = models.AutoField(primary_key=True)
    vehicle_number = models.CharField(max_length=50, unique=True)
    equipment_level = models.CharField(max_length=10, choices=EQUIPMENT_LEVELS)
    current_status = models.CharField(max_length=15, choices=AMBULANCE_STATUS, default="available")

    def __str__(self):
        return f"{self.vehicle_number} ({self.get_equipment_level_display()})"
    

class Driver(models.Model):
    driverid = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    

class User(models.Model):
    userid = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phonenumber = models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(default="", blank=True)
    is_admin = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Hash password before saving
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"



class EmergencyRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ambulance = models.ForeignKey(Ambulance, on_delete=models.CASCADE, null=True, blank=True)
    request_time = models.DateTimeField(auto_now_add=True)  # already hai
    expiry_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)  # 👈 yeh add karo

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('completed', 'Completed'),
            ('expired', 'Expired'),
        ],
        default='pending'
    )

    pickup_address = models.CharField(max_length=255, null=True, blank=True)
    hospital_name = models.CharField(max_length=255, null=True, blank=True)
    hospital_address = models.CharField(max_length=255, null=True, blank=True)
    request_type = models.CharField(
        max_length=50,
        choices=[('emergency', 'Emergency'), ('normal', 'Normal')],
        default='emergency'
    )

    def __str__(self):
        return f"{self.hospital_name} ({self.request_type}) - {self.status}"



class Dispatch(models.Model):
    dispatchid = models.AutoField(primary_key=True)
    request = models.ForeignKey(EmergencyRequest, on_delete=models.CASCADE)
    ambulance = models.ForeignKey(Ambulance, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)
    assigned_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        
        max_length=20,
        choices=[("assigned", "Assigned"), ("completed", "Completed")],
        default="assigned"
    )
    eta_minutes = models.IntegerField(default=15)  # estimated arrival
    ambulance_lat = models.FloatField(default=24.8607)  # sample coords (Karachi)
    ambulance_lng = models.FloatField(default=67.0011)

    def __str__(self):
        return f"Dispatch {self.dispatchid} → {self.request.hospital_name}"
    def is_free(self):
        return timezone.now() >= self.assigned_time + timedelta(minutes=30)
    
class ChatMessage(models.Model):
    request = models.ForeignKey("EmergencyRequest", on_delete=models.CASCADE)
    sender = models.ForeignKey("User", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sender.firstname}: {self.message[:20]}"

class NotificationLog(models.Model):
    request = models.ForeignKey("EmergencyRequest", on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=[("sms","SMS"),("email","Email"),("push","Push")])
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.type} - {self.message}"

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, is_admin=False):
        if not email:
            raise ValueError("Email required")
        user = self.model(email=self.normalize_email(email), is_admin=is_admin)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        return self.create_user(email, password, is_admin=True)

    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    phonenumber = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)