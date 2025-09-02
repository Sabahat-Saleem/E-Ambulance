# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from .models import Ambulance, Driver, Dispatch, EmergencyRequest, User
from .forms import AmbulanceForm, DriverForm, DispatchForm, EmergencyRequestForm, RegistrationForm, LoginForm

# List all ambulances
def ambulance_list(request):
    ambulances = Ambulance.objects.all()
    return render(request, "ambulance_list.html", {"ambulances": ambulances})

# Create new ambulance
def ambulance_create(request):
    if request.method == "POST":
        form = AmbulanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("ambulance_list")
    else:
        form = AmbulanceForm()
    return render(request, "ambulance_form.html", {"form": form, "title": "Add Ambulance"})

# Update ambulance
def ambulance_update(request, pk):
    ambulance = get_object_or_404(Ambulance, pk=pk)
    if request.method == "POST":
        form = AmbulanceForm(request.POST, instance=ambulance)
        if form.is_valid():
            form.save()
            return redirect("ambulance_list")
    else:
        form = AmbulanceForm(instance=ambulance)
    return render(request, "ambulance_form.html", {"form": form, "title": "Edit Ambulance"})

# Delete ambulance
def ambulance_delete(request, pk):
    ambulance = get_object_or_404(Ambulance, pk=pk)
    if request.method == "POST":
        ambulance.delete()
        return redirect("ambulance_list")
    return render(request, "ambulance_confirm_delete.html", {"ambulance": ambulance})


 #*************************************** Driver Views ***************************************#

 # List all drivers
def driver_list(request):
    drivers = Driver.objects.all()
    return render(request, "driver_list.html", {"drivers": drivers})

# Create new driver
def driver_create(request):
    if request.method == "POST":
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("driver_list")
    else:
        form = DriverForm()
    return render(request, "driver_form.html", {"form": form, "title": "Add Driver"})

# Update driver
def driver_update(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == "POST":
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            return redirect("driver_list")
    else:
        form = DriverForm(instance=driver)
    return render(request, "driver_form.html", {"form": form, "title": "Edit Driver"})

# Delete driver
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == "POST":
        driver.delete()
        return redirect("driver_list")
    return render(request, "driver_confirm_delete.html", {"driver": driver})  

#*************************************** Dispatch Views ***************************************#                                                              
def dispatch_list(request):
    dispatches = Dispatch.objects.all()
    return render(request, "dispatch_list.html", {"dispatches": dispatches})

# Assign a new dispatch
def dispatch_create(request):
    if request.method == "POST":
        form = DispatchForm(request.POST)
        if form.is_valid():
            dispatch = form.save(commit=False)
            # Update statuses
            dispatch.request.status = "assigned"
            dispatch.request.save()
            dispatch.ambulance.current_status = "on_call"
            dispatch.ambulance.save()
            dispatch.save()
            return redirect("dispatch_list")
    else:
        form = DispatchForm()
    return render(request, "dispatch_form.html", {"form": form, "title": "Assign Dispatch"})

# Mark dispatch completed
def dispatch_complete(request, pk):
    dispatch = get_object_or_404(Dispatch, pk=pk)
    if request.method == "POST":
        dispatch.request.status = "completed"
        dispatch.request.save()
        dispatch.ambulance.current_status = "available"
        dispatch.ambulance.save()
        return redirect("dispatch_list")
    return render(request, "dispatch_complete_confirm.html", {"dispatch": dispatch})

def emergency_request_create(request):
    if request.method == "POST":
        form = EmergencyRequestForm(request.POST)
        if form.is_valid():
            emergency_request = form.save(commit=False)
            emergency_request.user = request.user  # logged in user
            emergency_request.save()
            return redirect("emergency_request_list")
    else:
        form = EmergencyRequestForm()
    return render(request, "emergency_request_form.html", {"form": form})

# List all emergency requests
def emergency_request_list(request):
    requests = EmergencyRequest.objects.all().order_by("-request_time")
    return render(request, "emergency_request_list.html", {"requests": requests})


# Login and Registration Views

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Hash password
            user.password = make_password(form.cleaned_data["password"])
            user.save()

            # Send confirmation email
            send_mail(
                "Welcome to E-Ambulance!",
                f"Hi {user.firstname}, your account has been successfully created!",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, "Registration successful! Please login now.")
            print("Registration successful, redirecting to login...")
            return redirect("login")  
        
             # 👈 make sure urls.py has name="login"
    else:
        form = RegistrationForm()
        print("Rendering registration form...")
    return render(request, "register.html", {"form": form})
     


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                user = User.objects.get(email=email)
                if check_password(password, user.password):  # ✅ Check hashed password
                    request.session["user_id"] = user.userid
                    messages.success(request, "Login successful!")
                    return redirect("home")   # 👈 this should be dashboard/home
                else:
                    messages.error(request, "Invalid password.")
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect("login")
#*************************************** Static Page Views ***************************************#

# Static Pages
def home(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")  # agar login nahi hai to login page bhej do

    user = User.objects.get(userid=user_id)
    return render(request, "home.html", {"user": user})

def about(request):
    return render(request, "about.html")

def gallery(request):
    return render(request, "gallery.html")

def contact(request):
    return render(request, "contact.html")

def ambulance_types(request):
    return render(request, "ambulance_types.html")

def feedback(request):
    return render(request, "feedback.html")

def costs(request):
    return render(request, "costs.html")

def drivers_list(request):
    return render(request, "drivers_list.html")
# User Registration and Login 

def register(request):
    return render(request, "register.html")

def user_login(request):
    return render(request, "login.html")
 
