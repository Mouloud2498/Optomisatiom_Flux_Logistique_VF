from django import forms
from transport.models import Mission,Commande


class ConfirmationMission(forms.ModelForm):
    password = None

    class Meta:
        model = Mission

        fields = ['nom_mission', 'date_mission','id_dep_mis','id_arr_mis','id_cam']
        labels = {'nom_mission': "Nom de la Mssion", 'date_mission': "Date de Depart",'id_dep_mis':"Ville de Depart",'id_arr_mis': "Ville d'Arrivée",'id_cam':'Le Camion'}



class Confirmation(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['id_commande','id_mis']