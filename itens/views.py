#from django.shortcuts import render
from typing import Any, Dict, List
from django import http
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.http.response import JsonResponse
from itens.models import Item, ItemEmpresa, Empresa, Mercadologica
from django.views import generic
import json
import datetime

# Create your views here.
def itens(request):
    template = loader.get_template('itens/home.html')
    for key in request.GET:
        print (key ," > ", request.GET[key])
        if 'codigos' == key:
            if request.GET[key] != "":
                atualizararquivo(request.GET[key],'a')
            template = loader.get_template('itens/'+key+'.txt')
        if 'somapaes' == key:
            template = loader.get_template('itens/'+key+'.html')
        #if 'em' == key:
        #    resp = consultaMercadologica(request.GET[key])
        #    return JsonResponse(resp)
    return HttpResponse(template.render())
def atualizararquivo(codigo,tipo):
    #listdir =os.listdir()
    #print (listdir)
    arquivo = open('itens/templates/itens/codigos.txt',tipo)
    arquivo.write(codigo +"\n")
    arquivo.close()

def lerArquivo(caminho):
    arq = open(caminho, 'rb')
    retornab = arq.read()
    retorna: str = retornab.decode()
    try:
        retornaobj: object = json.loads(retorna)
    except:
        retornaobj: object = retorna
    arq.close()
    return retornaobj

def validarcodigoEAN13(codigo):
    somador = 0
    for i in range(12):
        if i%2 == 0:
            somador += int(codigo[i])
        else:
            somador += int(codigo[i])*3
    somador = (somador%10) if (somador%10) == 0 else (10-(somador%10))
    return somador == int(codigo[12])
class MercacologicaView(generic.ListView):
    model = Mercadologica
    paginate_by = 30
    filtro=""
    extrutura=""

    def salvaMercadologica(obj):
        novomercad = Mercadologica(codigo=obj['cod'], superior=obj['sup'], descricao=obj['desc'])
        try:
            print (novomercad)
        except:
            print (obj)
        finally:
            novomercad.save()
    def consultaMercadologica(self, obj):
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
    def organizaMercadologica(self, obj):
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

        listamerc = self.consultaMercadologica(mercad)
        return (listamerc)
    def lerarquivomercadologica(self):
        caminho = 'itens/static/itens/mercadologica.json'
        obj = lerArquivo(caminho)
        obj = self.organizaMercadologica(obj)
        #jso = json.dumps(obj)
        if self.extrutura == "r" or self.extrutura == "g" or self.extrutura == "c":
            r = [x for x in obj if 0 == x['sup']]
            if self.extrutura == "g" or self.extrutura == "c":
                rid = [x['id'] for x in r]
                g = [x for x in obj if x['sup'] in rid or x['id'] in rid]
                if self.extrutura == "c":
                    gid = [x['id'] for x in g]
                    c = [x for x in obj if x['sup'] in gid or x['id'] in gid]
                    g = c
                r = g
            obj = r
        obj = [x for x in obj if self.filtro.lower() in x['desc'].lower()]
        return obj
    def get_queryset(self):
        m = Mercadologica.objects.filter(descricao__contains=self.filtro).order_by('id').values()
        if self.extrutura == "r" or self.extrutura == "g" or self.extrutura == "c":
            ids=[x['id'] for x in m if 0 == x['superior']]      
            if self.extrutura == "g" or self.extrutura == "c":
                r = Mercadologica.objects.filter(superior=0).order_by('id').values('id')
                rid = [x['id'] for x in r]
                rid.append(0)
                ids=[x['id'] for x in m if x['superior'] in rid]
                if self.extrutura == "c":
                    g = Mercadologica.objects.filter(superior__in=rid).order_by('id').values('id')
                    rid = [x['id'] for x in g]
                    rid.append(0)
                    ids=[x['id'] for x in m if x['superior'] in rid ]
            m = Mercadologica.objects.filter(pk__in=ids).order_by('id').values()
        return m
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            self.paginate_by = int(request.GET['npaginat'])
        except:
            self.paginate_by = 30
        try:
            self.filtro = request.GET['nfiltro']
        except:
            self.filtro = ""
        try:
            self.extrutura = request.GET['nextrutura']
        except:
            self.extrutura = ""
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MercacologicaView, self).get_context_data(**kwargs)
        obj = self.lerarquivomercadologica()
        context['arqjson'] = obj[(context['page_obj'].number-1)*self.paginate_by:context['page_obj'].number*self.paginate_by]
        context['get'] = {'paginat':self.paginate_by, 'filtro':self.filtro, 'extrutura':self.extrutura}
        return context   
class SomarPaesView(generic.TemplateView):
    template_name = 'itens/somapaes_list.html'
    def analizacodigo(self, greq):
        getrec = {}
        int(greq['ncoletor'])
        print('inteiro possivel')
        if len(greq['ncoletor']) == 13 and greq['ncoletor'][0] == '2':
            getrec['codigo'] = greq['ncoletor']
            getrec['local'] = greq['nlocal']
            getrec['data'] = datetime.datetime.now().strftime('%Y-%m-%d')
            getrec['valorkg'] = 1399
            getrec['valortotal'] = int(getrec['codigo'][5:12])
            getrec['peso'] = round(getrec['valortotal'] / getrec['valorkg'], 3)
            getrec['codproduto'] = getrec['codigo'][1:5]
            getrec['quantidade'] = round(getrec['peso']/0.06)
            getrec['valido'] = validarcodigoEAN13(getrec['codigo']) 
            atualizararquivo(json.dumps(getrec),'a')         

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if 'ncoletor' in request.GET:
            self.analizacodigo(request.GET)
        try:
            arquivo = (lerArquivo('itens/templates/itens/codigos.txt'))
            print ("l188 tem arquivo",type(arquivo))
            if isinstance(arquivo, dict):
                print("l190 uma linha")
            else:
                print('l192 tem linha')
                arquivo = arquivo.split("\r\n")
                arquivo.pop()
                #print(f'lista arquivo {arquivo}')
                #nvarquivo = []
                #for x in arquivo:
                #    if x == '':
                #        #print (f'lista v do arq {x}')
                #       pass
                #    else:
                #        #print (f'lista do arq {x}')
                #        nvarquivo.append(x)
                #    arquivo = n
                arquivo = [json.loads(x) for x in arquivo if x != '']
                #print(f'l206 arquivo {arquivo}')
            
        except:
            print('não tem arquivo')
        if 'atualiza' in request.GET:
            try:
                dados = json.loads(request.GET['dados'])
                print(f'l213 dados {dados}')
                dados['peso'] = round(int(dados['peso'])/1000, 3)
                #print(f'l215 dado com peso c {dados}')
                arquivo[int(request.GET['atualiza'])] = dados
                print(f'l217 arquivo {arquivo}')
                d=""
                print (f'l 219')
                indi=0
                for x in arquivo:
                    if indi!=0:
                        print(f'l221 l{x} ')
                        d += "\n"
                    d += json.dumps(x)
                    print(f'l223')
                    indi=indi+1
                print(f'atualizando {d}')
                atualizararquivo(d, 'w')

            except:
                print('não é atualiza')
        try:
            if isinstance(arquivo, list):
                kwargs['codigo']=arquivo
            else:
                kwargs['codigo']=[]
                kwargs['codigo'].append(arquivo)
            #print (f'arquivo 2 {arquivo}')
        except:
            kwargs['codigo'] = ""

        return super().get(request, *args, **kwargs)
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super(SomarPaesView, self).get_context_data(**kwargs)
        
        context['locais'] = ['Saúde', 'CRAS', 'Reciclagem']
        context['totais'] = {'Total':{'peso':0,'quantidade':0}}
        for local in context['locais']:
            context['totais'][local] = {'peso':0,'quantidade':0}
        for codigo in context['codigo']:
            #print(f"context codigo {context['codigo']}")
            if codigo['valido']:
                context['totais']['Total']['peso'] += codigo['peso'] 
                context['totais']['Total']['quantidade'] += codigo['quantidade']
                context['totais'][codigo['local']]['peso'] += codigo['peso'] 
                context['totais'][codigo['local']]['quantidade'] += codigo['quantidade']
        try:
            context['local'] = context['codigo'][-1]['local']
        except:
            print ("não tem local ainda")
        kwargs = context
        return super().get_context_data( **kwargs)