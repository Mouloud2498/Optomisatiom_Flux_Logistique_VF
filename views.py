from django.shortcuts import render,redirect,HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from transport.models import Commande,Camions,Client,TypeCamion,Roue,Ville,Chauffeur,Mission
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import ConfirmationMission, Confirmation
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.contrib import messages
# datetime

from django.utils import timezone


# pdf
from xhtml2pdf import pisa
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.template.loader import get_template





# Creation d'une mission
@login_required(login_url='my-login')
def create_mission(request,slug=None,id_cam=None):
    commande = get_object_or_404(Commande, id_commande=slug)
    camion = get_object_or_404(Camions, id_camion=id_cam)
    context={'camion':camion, 'commande': commande}
    return render(request, 'create_mission.html',context)

# la liste des missions

@login_required(login_url='my-login')
def mission (request):
    mission = Mission.objects.filter(mission_termine = 1)
    missiont = Mission.objects.filter(mission_termine = 0)
    context = {'mission':mission,'missiont':missiont}
    return render (request,'missions.html',context)


# La confirmation d'une mission apres lui avoir assingnée une commande
@login_required(login_url='my-login')
def confirm_mission(request,slug=None,id_c=None):
    current_user_id = request.user.id
    commande = get_object_or_404(Commande, id_commande=slug)
    camion = get_object_or_404(Camions, id_camion=id_c)
    confirm = ConfirmationMission(request.POST)
    if request.method == 'POST':
        if confirm.is_valid():
            mission = Mission(
              nom_mission='mission' + str(commande.id_commande),
              date_mission=commande.date_c,
              id_dep_mis=commande.ville_dep,
              id_arr_mis=commande.ville_arr,
              )
            mission.id_cam = camion
            mission.mission_termine = 1
            mission.created_by = current_user_id
            mission.save()
            commande.id_mis = mission
            commande.save()
            camion.dispo = 1
            camion.save()
            return redirect(reverse('mission'))
    else:
        # Créer une instance du formulaire et remplir les valeurs
        confirm = ConfirmationMission(initial={
            'nom_mission':('mission'+str(commande.id_commande))  ,
            'date_mission': commande.date_c,
            'id_dep_mis': commande.ville_dep,
            'id_arr_mis': commande.ville_arr,
            'id_cam': camion.id_camion,
    })
    context = {'confirm':confirm,'commande':commande,'camion':camion}
    return render(request,'confirmer_mission.html',context=context)


# Les details d'une mission et l'ajout des commandes a cette mission

@login_required(login_url='my-login')
def mission_info(request,slug=None):
    mission = get_object_or_404(Mission, id_mission=slug)
    camion = Camions.objects.get(id_camion = mission.id_cam.id_camion)
    commande_mis = Commande.objects.filter(id_mis=mission.id_mission).order_by('-date_c')
    # comparaison des dates
    date_m = mission.date_mission
    aujourdhui = timezone.now()
    date_cmd = date_m < aujourdhui

    # la derniere commande de la mission
    pcmd = commande_mis[0]
    mission.date_mission = pcmd.date_c
    mission.id_arr_mis = pcmd.ville_arr
    mission.save()
    ville = pcmd.ville_arr
    date = pcmd.date_c
    cam = pcmd.id_tc
    commande = Commande.objects.filter(id_mis__isnull = True, ville_dep = ville,date_c__gte = date, id_tc = cam,).order_by('profit')
    if request.method == 'POST':
        # Récupérer l'ID de la commande à ajouter
        cmd_id = request.POST.get('cmd_id')
        # Récupérer l'objet Commande correspondant
        cmd = Commande.objects.get(id_commande=cmd_id)
        if request.POST.get('minus'):
            cmd.id_mis = None
            cmd.save()
        elif request.POST.get('plus'):
            cmd.id_mis = mission
            cmd.save()
        return redirect('mission-info', slug=slug)
    show_action = len(commande_mis) > 1
    planificateur = request.user.groups.filter(name = 'Planificateurs')
    profit_total = commande_mis.aggregate(Sum('profit'))['profit__sum']
    context={'mission': mission,'commande':commande_mis,'cmd':commande,'showaction':show_action,'planificateur':planificateur,'camion':camion,'date_cmd':date_cmd,'profit':profit_total}
    return render(request,'mission_details.html',context)


@login_required(login_url='my-login')
def mission_termine(request,slug=None):
    mission = get_object_or_404(Mission,id_mission=slug)
    camion = Camions.objects.get(id_camion=mission.id_cam.id_camion)
    mission.mission_termine = 0
    mission.save()
    camion.dispo = 0
    camion.save()
    return redirect('mission')


# La page html de la feuille de route

@login_required(login_url='my-login')
def feuille_de_route(request,slug):
    mission = get_object_or_404(Mission, id_mission = slug)
    camion = Camions.objects.get(id_camion = mission.id_cam.id_camion)
    commande = Commande.objects.filter(id_mis = mission.id_mission).order_by('date_c')
    context={'mission':mission,'camion':camion,'commande':commande}
    return render(request, 'fdr.html',context)





# le pdf generé par la page html de la feuille de route
@login_required(login_url='my-login')
def create_pdf(request,slug):
    # retrieve data to populate the template
    missions = get_object_or_404(Mission, id_mission = slug)
    camion = Camions.objects.get(id_camion = missions.id_cam.id_camion)
    commandes = Commande.objects.filter(id_mis = missions.id_mission).order_by('date_c')
    context = {'mission': missions, 'commande': commandes,'camion':camion}
    # load the template
    template = get_template('fdr.html')

    # render the template
    html = """
        <style>
            #pdf-link {
                display: none;
            }
           
        </style>
    """
    html += template.render(context)

    # create the PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Feuille de route"'+ missions.nom_mission+'".pdf"'
    buffer = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), buffer)
    if not pdf.err:
        response.write(buffer.getvalue())
        buffer.close()
    return response

@login_required(login_url='my-login')
def supprimer_mission(request, slug=None):
    mission = get_object_or_404(Mission, id_mission=slug)
    commandes = Commande.objects.filter(id_mis=mission.id_mission)
    camion = Camions.objects.get(id_camion=mission.id_cam.id_camion)
    if request.method == 'POST':
        for commande in commandes:
            commande.id_mis = None
            commande.save()
            camion.dispo = 0
            camion.save()
            messages.success(request, 'La mission a été annulée avec succès.')
        mission.delete()
        return redirect('mission')
    return render(request, 'missions.html', {'mission': mission})














