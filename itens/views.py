#from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http.response import JsonResponse
from itens.models import Item, ItemEmpresa, Empresa, Mercadologica
from django.views import generic
import json

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
            resp = consultaMercadologica(request.GET[key])
            return JsonResponse(resp)
    return HttpResponse(template.render())

def atualizararquivo(codigo):
    #listdir =os.listdir()
    #print (listdir)
    arquivo = open('itens/templates/itens/codigos.txt','a')
    arquivo.write(codigo +"\n")
    arquivo.close()

class MercacologicaView(generic.ListView):
    model = Mercadologica
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super(MercacologicaView, self).get_context_data(**kwargs)
        caminho = 'itens/static/itens/mercadologica.json'
        obj = lerArquivo(caminho)
        jso = json.dumps(obj)
        context['arqjson'] = jso
        print (context)

        return context
    
def lerArquivo(caminho):
    arq = open(caminho, 'rb')
    retornab = arq.read()
    retorna: str = retornab.decode()
    retornaobj: object = json.loads(retorna)
    arq.close()
    return retornaobj

def consultaMercadologica(conteudo=0):
    print (type(conteudo))
    objcont = json.loads(conteudo)
    m = Mercadologica.objects.filter(codigo=objcont['cod'],descricao=objcont['desc']).values()
    obj: object = {}
    for i in m:
        for j in i:
            obj[j] = i[j]
    return obj