from django.urls import path
from . import views

    
urlpatterns = [
    
    # Home page urls************************#
    path("home", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("gallery/", views.gallery, name="gallery"),
    path("contact/", views.contact, name="contact"),
    path("ambulance-types/", views.ambulance_types, name="ambulance_types"),
    path("feedback/", views.feedback, name="feedback"),
    path("costs/", views.costs, name="costs"),
    path("drivers-list/", views.drivers_list, name="drivers_list"),

    # User accounts
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("home/", views.home, name="home"),

    # Ambulance URLs
    path("ambulances/", views.ambulance_list, name="ambulance_list"),
    path("ambulances/create/", views.ambulance_create, name="ambulance_create"),
    path("ambulances/<int:pk>/update/", views.ambulance_update, name="ambulance_update"),
    path("ambulances/<int:pk>/delete/", views.ambulance_delete, name="ambulance_delete"),

    # Driver URLs   ************ 
    path("drivers/", views.driver_list, name="driver_list"),
    path("drivers/add/", views.driver_create, name="driver_create"),
    path("drivers/<int:pk>/edit/", views.driver_update, name="driver_update"),
    path("drivers/<int:pk>/delete/", views.driver_delete, name="driver_delete"),

    # Dispatch URLs
    path("dispatch/", views.dispatch_list, name="dispatch_list"),
    path("dispatch/create/", views.dispatch_create, name="dispatch_create"),
    path("dispatch/<int:pk>/complete/", views.dispatch_complete, name="dispatch_complete"),
    path("emergency-request/", views.emergency_request, name="emergency_request"),
    path("emergency-requests/", views.emergency_request_list, name="emergency_request_list"),
    path("my-requests/", views.my_requests, name="my_requests"),
    path("logout/", views.logout_view, name="logout"),
    path("track-request/<int:pk>/", views.track_request, name="track_request"),
    path("ambulance-list/", views.ambulance_list_user, name="ambulance_list"),
    path("drivers-list/", views.drivers_list_user, name="drivers_list"),
    path("communication/", views.communication_dashboard, name="communication_dashboard"),
    path("communication/chat/<int:request_id>/", views.chat_view, name="chat_view"),
    path("communication/messages/<int:request_id>/", views.get_messages, name="get_messages"),
    path("communication/send/", views.send_message, name="send_message"),    
]
  
