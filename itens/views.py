#from django.shortcuts import render
from typing import Any, Dict
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from itens.models import Item, ItemEmpresa, Empresa, Mercadologica, Tag
from django.views import generic
import json
import datetime
import pandas as pd
from django.db.models import Count

# Create your views here.
def menu():
    menu = {
            'index' : 'Home',
            'itensemp' : 'Itens por Empresa',
            'mercadologica' : 'Extr. Mercadol. 2020',
            'somapaes' : 'Soma pães prefeitura',
            'empresa' : 'Empresas',
            'tag' : 'Tags',
        }
    return menu
class HomeView(generic.TemplateView):
    template_name = 'itens/home.html'
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super(HomeView, self).get_context_data(**kwargs)
        context["menu"] = menu()
        kwargs=context
        return super().get_context_data(**kwargs)
#def itens(request):
#    template = loader.get_template('itens/home.html')
#    for key in request.GET:
#        print (key ," > ", request.GET[key])
#        if 'codigos' == key:
#            if request.GET[key] != "":
#                atualizararquivo(request.GET[key],'a')
#            template = loader.get_template('itens/'+key+'.txt')
#        if 'somapaes' == key:
#            template = loader.get_template('itens/'+key+'.html')
#        #if 'em' == key:
#        #    resp = consultaMercadologica(request.GET[key])
#        #    return JsonResponse(resp)
#        if 'xlsx' == key:
#            lerxlsx()
#    return HttpResponse(template.render())
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
            #m = Mercadologica.objects.filter(codigo=ob['cod'], descricao=ob['desc']).all()
            #if 'tag' in ob:
            #    for tag in ob['tag'].items():
            #        #print(f'linha 93 obj {tag} mtag{m[0].tag.all()}')
            #        t = Tag.objects.filter(tipo=tag[0].capitalize(), tag=tag[1], detalhe='Mercadologica')
            #        if t.exists():
            #            #print (f"existe t {t}")
            #            if t[0] not in m[0].tag.all():
            #                #print (f"\nexiste mtag\n t{t.values()}\n m{m[0].tag.values()}\n ")
            #                m[0].tag.add(t[0])
            #        else:
            #            #ntag = m[0].tag.create(tipo=tag[0].capitalize(), tag=tag[1], detalhe='Mercadologica')
            #            print(f'nova tag criada e adicionada ')
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
        m = Mercadologica.objects.filter(descricao__contains=self.filtro).order_by('id').all()
        if self.extrutura == "r" or self.extrutura == "g" or self.extrutura == "c":
            ids=[x['id'] for x in m.values() if 0 == x['superior']]      
            if self.extrutura == "g" or self.extrutura == "c":
                r = Mercadologica.objects.filter(superior=0).order_by('id').values('id')
                rid = [x['id'] for x in r]
                rid.append(0)
                ids=[x['id'] for x in m.values() if x['superior'] in rid]
                if self.extrutura == "c":
                    g = Mercadologica.objects.filter(superior__in=rid).order_by('id').values('id')
                    rid = [x['id'] for x in g]
                    rid.append(0)
                    ids=[x['id'] for x in m.values() if x['superior'] in rid ]
            m = Mercadologica.objects.filter(pk__in=ids).order_by('id').all()
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
        context["menu"] = menu()
        obj = self.lerarquivomercadologica()
        context['arqjson'] = obj[(context['page_obj'].number-1)*self.paginate_by:context['page_obj'].number*self.paginate_by]
        context['get'] = {'paginat':self.paginate_by, 'filtro':self.filtro, 'extrutura':self.extrutura}
        return context   
class SomarPaesView(generic.TemplateView):
    template_name = 'itens/somapaes_list.html'
    def analizacodigo(self, greq):
        getrec = {}
        if len(greq['ncoletor']) == 13 and greq['ncoletor'][0] == '2' and greq['ncoletor'].isnumeric() :
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
            if not isinstance(arquivo, dict):
                arquivo = arquivo.split("\r\n")
                arquivo.pop()
                arquivo = [json.loads(x) for x in arquivo if x != '']
            
        except:
            print('não tem arquivo')
        if 'atualiza' in request.GET:
            try:
                dados = json.loads(request.GET['dados'])
                dados['peso'] = round(int(dados['peso'])/1000, 3)
                arquivo[int(request.GET['atualiza'])] = dados
                d=""
                indi=0
                for x in arquivo:
                    if indi!=0:
                        d += "\n"
                    d += json.dumps(x)
                    indi=indi+1
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
        context["menu"] = menu()
        context['locais'] = ['Saúde', 'Reciclagem', 'Conselho tutelar', 'CRAS']
        context['totais'] = {'Total':{'peso':0,'quantidade':0}}
        for local in context['locais']:
            context['totais'][local] = {'peso':0,'quantidade':0}
        for codigo in context['codigo']:
            #print(f"context codigo {context['codigo']}")
            if codigo['valido']:
                context['totais']['Total']['peso'] = round(context['totais']['Total']['peso'],3)+round(codigo['peso'],3) 
                context['totais']['Total']['quantidade'] += int(codigo['quantidade'])
                context['totais'][codigo['local']]['peso'] = round(context['totais'][codigo['local']]['peso'],3) + round(codigo['peso'],3) 
                context['totais'][codigo['local']]['quantidade'] += int(codigo['quantidade'])
                context['totais']['Total']['peso'] = round(context['totais']['Total']['peso'],3) 
                context['totais'][codigo['local']]['peso'] = round(context['totais'][codigo['local']]['peso'],3)
        try:
            context['local'] = context['codigo'][-1]['local']
        except:
            print ("não tem local ainda")
        kwargs = context
        return super().get_context_data( **kwargs)
class ItensEmpresaView(generic.ListView):
    
    def lerxlsx(self):
        caminho="itens/static/itens/"
        nomearq="2-59"
        ext="xlsx"
        file=f"{caminho}{nomearq}.{ext}"
        import os
        print('linha 277')
        if f'{nomearq}.{ext}' in os.listdir(caminho):
            print(f'file{file}')
            arq = pd.read_excel(file,converters={'BARRA':str})
            dct = arq.to_dict('index')
        else:
            dct={}
            print('linha 284')
        empresa=self.verificaEmpresa( nomearq)
        #self.cadastraProdutos(empresa,dct)
        return [empresa,dct]
    
    def verificaEmpresa(self, empr):
        empresas = Empresa.objects.filter(cnpj__contains=empr)
        print(f'linha 292 empresa {empresas}')
        if empresas.count()==1:
            for empresa in empresas:
                return empresa

    def verificaTag(self, *tags):
        tag = Tag.objects.filter(tipo=tags[0],tag=tags[1]).all()
        #print(f'tags {tags} tag {tag}')
        if tag.count()==1:
            return tag
        elif tag.count()==0:
            #print(f'count 0 {tags}')
            tag = Tag(tipo=tags[0],tag=tags[1],detalhe='ItemEmpresa')
            tag.save()
            return self.verificaTag(*tags)
    def cadastraProdutos(self, empres, itens):
        titulodados = {
            'tituloitem':['BARRA','Column1','CODPROD','NCM','COMPOSICAO'],
            'titulotag':['PERCENTUAL_ICMS','CLASSIFICACAO_PISCOFINS','VENDIDOS','PRECO_CUSTO','PRECO_UNITARIO']
        }
        print(f'empresa {empres}\nitens {itens}')
        for item in itens.values():
            its = ItemEmpresa.objects.filter(codigo=item['CODPROD'], empresa=empres).all()
            novoitem = ItemEmpresa(empresa=empres,codigo=item['CODPROD'],descricao=item['Column1'],
                                barras=item['BARRA'],composicao=item['COMPOSICAO']=="S",ncm=item['NCM'])
            if its.count()==1:
                if its[0]['codigo'] == novoitem.codigo:
                        print (f"it: {its[0]} codigo igual novoitem")
                        if its[0]['descricao'] != novoitem.descricao:
                            its[0]['descricao'] = novoitem.descricao
                            #novoitem.save()
                            print (f"it: {its[0]} descricao diferente novoitem")
                        if its[0]['barras'] != novoitem.barras:
                            its[0]['barras'] = novoitem.barras
                            #novoitem.save()
                            print (f"it: {its[0]} barras diferente novoitem")
                        if its[0]['composicao'] != novoitem.composicao:
                            its[0]['composicao'] = novoitem.composicao
                            #novoitem.save()
                            print (f"it: {its[0]} composicao diferente novoitem")
                        if its[0]['ncm'] != novoitem.ncm:
                            its[0]['ncm'] = novoitem.ncm
                            #novoitem.save()
                            print (f"it: {its[0]} ncm diferente novoitem")
                        for ttag in titulodados['titulotag']:
                            ta = self.verificaTag(ttag,item[ttag])
                            print (f'item {its[0]} tag {ta} ttag {ttag}:{item[ttag]}')
                            #ta['tagsitemp'].add(it)
                            if ta[0] not in its[0].tag.all():
                                its[0].tag.add(ta[0])    
                else:
                    print (f"it: {its[0]} diferente {novoitem}")
                
            elif its.count()==0:
                novoitem.save()
            else:
                print(f"its: {its}")
    def get_queryset(self) -> QuerySet[Any]:
        self.queryset = ItemEmpresa.objects.all()
        return super().get_queryset()
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.model = ItemEmpresa
        self.paginate_by = 20
        #self.ordering = 'descricao'
        #response = super(ItensEmpresaView, self).get(request)
        #print(f'response: {request}')
        return super().get(request, *args, **kwargs)   #response#
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        #kwargs = super(ItensEmpresaView, self).get_context_data(**kwargs)
        kwargs['menu']=menu() 
        #kwargs['empresa'], kwargs['itens'] = self.lerxlsx()
        #print (f'linha 360 kwargs {kwargs}')
        return super().get_context_data(**kwargs)#kwargs#
class EmpresaView(generic.ListView):
    model = Empresa
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs = super(EmpresaView, self).get_context_data(**kwargs)
        kwargs['menu']=menu()

        return super().get_context_data(**kwargs)
class TagView(generic.ListView):
    model= Tag
    paginate_by = 25
    ordering = 'tipo','tag'
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        #print (f'query 0 tip {queryset[0].tipo}: tag {queryset[0].tag} - det {queryset[0].detalhe} (merc {queryset[0].tagsmerc.all()})')
        return queryset
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        #kwargs = super(TagView,self).get_context_data(**kwargs)
        kwargs['menu']=menu()
        return super().get_context_data(**kwargs)