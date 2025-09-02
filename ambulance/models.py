from django.db import models
from django.contrib.auth.hashers import make_password

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
    address = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Hash password before saving
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"



class EmergencyRequest(models.Model):
    REQUEST_STATUS = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    requestid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()   # NEW: Reason for emergency
    request_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=REQUEST_STATUS, default="pending")

    def __str__(self):
        return f"Request {self.requestid} - {self.status}"



class Dispatch(models.Model):
    dispatchid = models.AutoField(primary_key=True)
    request = models.OneToOneField(EmergencyRequest, on_delete=models.CASCADE)
    ambulance = models.ForeignKey("Ambulance", on_delete=models.CASCADE)
    driver = models.ForeignKey("Driver", on_delete=models.CASCADE, null=True, blank=True)
    assigned_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dispatch {self.dispatchid} - {self.ambulance.vehicle_number}"