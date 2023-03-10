#from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http.response import JsonResponse
from itens.models import Item, ItemEmpresa, Empresa, Mercadologica
from django.views import generic


# Create your views here.
def itens(request):
    template = loader.get_template('itens/home.html')
    for key in request.GET:
        print (key ," > ", request.GET[key])
        if 'codigos' == key:
            if request.GET[key] != "":
                atualizararquivo(request.GET[key])
            template = loader.get_template('itens/'+key+'.txt')
        if 'somapaes' == key:
            template = loader.get_template('itens/'+key+'.html')
        if 'em' == key:
            #ler = lerXls()
            #salvararq(ler)
            return JsonResponse()
    return HttpResponse(template.render())

def atualizararquivo(codigo):
    #listdir =os.listdir()
    #print (listdir)
    arquivo = open('itens/templates/itens/codigos.txt','a')
    arquivo.write(codigo +"\n")
    arquivo.close()

class MecacologicaView(generic.ListView):
    model = Mercadologica