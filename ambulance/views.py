# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from .forms import AmbulanceForm, DriverForm, DispatchForm, EmergencyRequestForm, RegistrationForm, LoginForm
from .models import User, EmergencyRequest, Driver, Ambulance, Dispatch, ChatMessage
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
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

            # ✅ Update request + ambulance status
            dispatch.request.status = "Dispatched"
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
        dispatch.request.status = "Completed"
        dispatch.request.save()

        dispatch.ambulance.current_status = "available"
        dispatch.ambulance.save()

        dispatch.save()
        return redirect("dispatch_list")
    return render(request, "dispatch_complete_confirm.html", {"dispatch": dispatch})

def mark_as_dispatched(self, request, queryset):
    available_ambulance = Ambulance.objects.filter(current_status="Available").first()
    if not available_ambulance:
        self.message_user(request, "No available ambulance right now.", level="error")
        return

    for req in queryset:
        req.status = "Dispatched"
        req.save()

        Dispatch.objects.create(
            emergency_request=req,
            ambulance=available_ambulance,
            current_lat=24.8607,   # Example: Karachi lat
            current_lng=67.0011,  # Example: Karachi lng
            estimated_arrival=timezone.now() + timedelta(minutes=15)  # Dummy ETA
        )

        available_ambulance.current_status = "On Call"
        available_ambulance.save()

    self.message_user(request, "Requests dispatched successfully!")

# List all emergency requests
def emergency_request(request):
    if request.method == "POST":
        form = EmergencyRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = User.objects.get(pk=request.session["user_id"])
            req.save()
            messages.success(request, "🚑 Your emergency request has been submitted!")
            return redirect("home")
    else:
        form = EmergencyRequestForm()
    return render(request, "emergency_request.html", {"form": form})

def emergency_request_list(request):
    requests = EmergencyRequest.objects.all().order_by("-created_at")
    return render(request, "emergency_request_list.html", {"requests": requests})

def track_request(request, pk):
    emergency_request = get_object_or_404(EmergencyRequest, pk=pk)
    dispatch = Dispatch.objects.filter(request=emergency_request).first()
    return render(request, "track_request.html", {
        "request": emergency_request,
        "dispatch": dispatch
    })

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        print("POST data:", request.POST)   # Debugging purpose only
        if form.is_valid():
            print("Form is valid!")
            user = form.save(commit=False)
            user.save()
            return redirect("login")
        else:
            print("Form errors:", form.errors) # Debugging purpose only
    else:
        form = RegistrationForm()
        print("Rendering empty form")

    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                user = User.objects.get(email=email)
                if check_password(password, user.password):  #   Check hashed password
                    request.session["user_id"] = user.userid
                    messages.success(request, "Login successful!")
                    return redirect("home")   # Redirect to a dashboard or home page
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
        return redirect("login")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect("login")

    # User requests
    requests = EmergencyRequest.objects.filter(user=user).order_by("-created_at")

    # Show all ambulances + drivers
    ambulances = Ambulance.objects.all()
    drivers = Driver.objects.all()

    return render(request, "home.html", {
        "user": user,
        "requests": requests,
        "ambulances": ambulances,
        "drivers": drivers
    })
def about(request):
    return render(request, "about-us.html")

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

def my_requests(request):
    requests = EmergencyRequest.objects.all()  # or filter by logged-in user
    return render(request, "my_requests.html", {"requests": requests})
def user_login(request):
    return render(request, "login.html")
 
# views.py
def ambulance_list_user(request):
    ambulances = Ambulance.objects.all()   # sirf show karna, add/edit nahi
    return render(request, "ambulance_list.html", {"ambulances": ambulances})

# views.py
def drivers_list_user(request):
    drivers = Driver.objects.all()  # sirf show karna
    return render(request, "drivers_list_user.html", {"drivers": drivers})

def remove_expired_requests():
    now = timezone.now()
    EmergencyRequest.objects.filter(
        expiry_time__lt=now, 
        status__in=['pending','accepted']
    ).update(status='expired')

def release_ambulances():
    for dispatch in Dispatch.objects.filter(status="assigned"):
        if dispatch.is_free():
            dispatch.status = "completed"
            dispatch.ambulance.current_status = "available"
            dispatch.ambulance.save()
            dispatch.save()

def communication_dashboard(request):
    requests = EmergencyRequest.objects.all()
    return render(request, "communication_dashboard.html", {"requests": requests})


def chat_view(request, request_id):
    # Get the emergency request object
    req = get_object_or_404(EmergencyRequest, id=request_id)
    
    # Get all chat messages for this request
    messages = ChatMessage.objects.filter(request=req).order_by("timestamp")
    
    if request.method == "POST":
        message_text = request.POST.get("message")
        if message_text:
            # Create a new chat message
            ChatMessage.objects.create(
                request=req,
                sender=request.user,
                message=message_text
            )
            # After sending, redirect to the same chat page (prevents double submission)
            return redirect('chat_view', request_id=request_id)
    
    # Render the chat page
    return render(request, 'chat_view.html', {
        'req': req,
        'messages': messages
    })

def get_messages(request, request_id):
    req = get_object_or_404(EmergencyRequest, id=request_id)
    messages = ChatMessage.objects.filter(request=req).order_by("timestamp")
    data = [{"sender": m.sender.firstname, "message": m.message, "time": m.timestamp.strftime("%H:%M")} for m in messages]
    return JsonResponse(data, safe=False)

@csrf_exempt
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        req = EmergencyRequest.objects.get(id=data["request_id"])
        user = User.objects.get(id=data["sender_id"])
        msg = ChatMessage.objects.create(request=req, sender=user, message=data["message"])
        return JsonResponse({"status": "ok", "message": msg.message})
    return JsonResponse({"status": "error"}, status=400)
