#from django.shortcuts import render
from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
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
    paginate_by = 30
    filtro=""

    def get_queryset(self):
        return Mercadologica.objects.filter(descricao__contains=self.filtro).order_by('id').values()
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            self.paginate_by = int(request.GET['npaginat'])
        except:
            self.paginate_by = 30
        try:
            self.filtro = request.GET['nfiltro']
        except:
            self.filtro = ""
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MercacologicaView, self).get_context_data(**kwargs)
        caminho = 'itens/static/itens/mercadologica.json'
        obj = lerArquivo(caminho)
        obj = organizaMercadologica(obj)
        #jso = json.dumps(obj)
        obj = [x for x in obj if self.filtro.lower() in x['desc'].lower()]
        context['arqjson'] = obj[(context['page_obj'].number-1)*self.paginate_by:context['page_obj'].number*self.paginate_by]
        context['get'] = {'paginat':self.paginate_by, 'filtro':self.filtro}
        return context
    
def lerArquivo(caminho):
    arq = open(caminho, 'rb')
    retornab = arq.read()
    retorna: str = retornab.decode()
    retornaobj: object = json.loads(retorna)
    arq.close()
    return retornaobj

def salvaMercadologica(obj):
    novomercad = Mercadologica(codigo=obj['cod'], superior=obj['sup'], descricao=obj['desc'])
    try:
        print (novomercad)
    except:
        print (obj)
    finally:
        novomercad.save()
def consultaMercadologica(obj):
    listamerc = []
    for ob in obj:
        m = Mercadologica.objects.filter(codigo=ob['cod'], descricao=ob['desc']).values()
        if m:
            for query in m:
                ob['ID'] = f"ID: {query['id']}"
        #else:
            #salvaMercadologica(ob)
        listamerc.append(ob)            
    return listamerc

def organizaMercadologica(obj):
    mercad = []
    id=0
    for setor in obj:
        id=id+1
        setorid=id
        creceita = obj[setor]
        mercad.append({'id':id, 'cod':0, 'desc':setor, 'sup':0})
        for receita in creceita:
            id=id+1
            receitaid=id
            grupos = creceita[receita]
            if 'tag' in grupos:
                mercad.append({'id':id, 'cod': grupos['cod'] , 'desc': receita, 'sup': setorid, 'tag': grupos['tag']})
            else:
                mercad.append({'id':id, 'cod': grupos['cod'] , 'desc': receita, 'sup': setorid})
            for grupo in grupos:
                if 'tag' != grupo and 'cod' != grupo:
                    id=id+1
                    grupoid=id
                    categorias = grupos[grupo]
                    mercad.append({'id':id, 'cod': categorias['cod'] , 'desc': grupo, 'sup': receitaid})
                    for categoria in categorias:
                        if 'cod'!=categoria:
                            id=id+1
                            mercad.append({'id':id, 'cod':categorias[categoria]['cod'], 'desc':categoria, 'sup': grupoid})

    listamerc = consultaMercadologica(mercad)
    return (listamerc)