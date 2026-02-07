from django.urls import path,include
from . import views
from .views import *

urlpatterns = [
    #liste commande




        path('create_mission/<int:slug>/<int:id_cam>',views.create_mission,name="create-mission"),
        path('confirm-mission/<int:slug>/<int:id_c>',views.confirm_mission,name="confirm-mission"),
        path('feuille-de-route/<str:slug>/',views.feuille_de_route,name="feuille-de-route"),
        path('supprimer-mission/<int:slug>/',views.supprimer_mission,name="supprimer-mission"),
        path('create-pdf/<str:slug>/',views.create_pdf,name="create-pdf"),
        path('mission-termine/<int:slug>/',views.mission_termine,name="mission-termine"),
        path('mission/',include([
        path('',views.mission, name='mission'),
        path('<str:slug>/',views.mission_info, name='mission-info'),

])),
]