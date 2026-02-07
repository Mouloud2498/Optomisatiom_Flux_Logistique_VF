from django import forms
from transport.models import Commande
from datetime import datetime

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ('id_cl', 'date_c', 'prix', 'id_tc', 'ville_dep', 'ville_arr')
        exclude=['profit']
        labels = {'id_cl': 'Votre Client', 'date_c': 'Date et Heure', 'prix': 'Prix', 'profit':'Profit', 'id_tc': 'Type Camion', 'ville_dep': 'Ville de départ', 'ville_arr': 'Ville Arrivée'}
        widgets={
            'id_cl': forms.Select(attrs={'class': 'form-control form-select form-select-lg mb-3'}),
            'date_c': forms.DateTimeInput(attrs={'type':'datetime-local','class':'form-control datepicker'},format='%Y-%m-%dT%H:%M'),
            # 'date_et_heure': DateTimeInput(attrs={'type':'datetime-local'}, format='%Y-%m-%dT%H:%M')
            'prix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Inserez Le Prix"}),
            'id_tc': forms.Select(attrs={'class': 'form-control form-select form-select-lg mb-3'}),
            'ville_dep': forms.Select(attrs={'class': 'form-control form-select form-select-lg mb-3'}),
            'ville_arr': forms.Select(attrs={'class': 'form-control form-select form-select-lg mb-3 '}),            
        }
        def clean_date_c(self):
            date_c = self.cleaned_data.get('date_c')
            if date_c and date_c < datetime.now():
                raise forms.ValidationError("La date de l'événement ne peut pas être antérieure à la date d'aujourd'hui.")
            return date_c