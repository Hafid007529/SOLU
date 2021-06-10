from django.shortcuts import render,redirect
from django.views.generic import ListView, DetailView #vistas prehechas por django
#from .models import Producto
# Create your views here.
from django.http import HttpResponse #importame desde la libreria y el modulo http, importame http response (medio para hacer estas consultas a la web), recibe un request y mostrar la pantalla que desea

from django.views.generic import FormView, TemplateView,View, UpdateView #para las vistas
from django.urls import reverse_lazy
from django.contrib.auth import login

# Importamos forms.py
from .forms import * #vamos a la carpeta de atrás

#Importamos las clases recien creadas
from .models import * #para las vistas

#lab 5
from django.db.models import F
from random import randint #numeros random
from django.contrib import messages #mensajes de error

class HomePageView(TemplateView): #esta clase esta mejor
  template_name = "main/home.html" #crea sus propio template
  def get_context_data(self, **kwargs): #vamos a agarrar todos los productos
      context = super().get_context_data(**kwargs) #kwags es un comodin te trae las cosas que ya tienes.
      context['latest_products'] = Producto.objects.all()[:5]  #imprimo los últimos 5 productos

      return context

# def home(request): #cuando recibe un request, retorna el hola mundo
#   return HttpResponse("Hola Mundo. Te encuentras en la página de inicio del Linio Express")


class RegistrationView(FormView):
  template_name = 'registration/register.html'
  form_class = UserForm
  success_url = reverse_lazy('home') #cuando me registro exitosamente me lleva al home
  
  def form_valid(self, form):
    # This methos is called when valid from data has been POSTed
    # It should return an HttpResponse

    # Create User
    username = form.cleaned_data['username']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']
    email = form.cleaned_data['email']
    password = form.cleaned_data['password1']

    user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password) #crea el usuario, dentro de los objetos que tenemos
    user.save()

    # Create Profile
    documento_identidad = form.cleaned_data['documento_identidad']
    fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
    estado = form.cleaned_data['estado']
    genero = form.cleaned_data['genero']

    user_profile = Profile.objects.create( user=user, documento_identidad=documento_identidad, fecha_nacimiento=fecha_nacimiento, estado=estado, genero=genero)
    user_profile.save()

    # Create Cliente if needed
    is_cliente = form.cleaned_data['is_cliente']
    if is_cliente:
        cliente = Cliente.objects.create(user_profile=user_profile)

        # Handle special attribute
        preferencias = form.cleaned_data['preferencias']
        preferencias_set = Categoria.objects.filter(pk=preferencias.pk)
        cliente.preferencias.set(preferencias_set)

        cliente.save()
    # Create Colaborador if needed
    is_colaborador = form.cleaned_data['is_colaborador']
    if is_colaborador:
        reputacion = form.cleaned_data['reputacion']
        colaborador = Colaborador.objects.create(user_profile=user_profile, reputacion=reputacion)

        # Handle special attribute
        cobertura_entrega = form.cleaned_data['cobertura_entrega']
        cobertura_entrega_set = Localizacion.objects.filter(pk=cobertura_entrega.pk)
        colaborador.cobertura_entrega.set(cobertura_entrega_set)

        colaborador.save()
        
    # Login the user
    login(self.request,user)

    return super().form_valid(form)


class ProductListView(ListView): #sirve para ver la lista de producto
    model = Producto

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query is not None:
            object_list = Producto.objects.filter(nombre__icontains=query)
            return object_list
        else:
            return Producto.objects.all()

class ProductDetailView(DetailView):
    model = Producto

#todas las paginas se declaran en views con defs


class AddToCartView(View):
    def get(self, request, product_pk):
        # Obten el cliente
        user_profile = Profile.objects.get(user=request.user)
        cliente = Cliente.objects.get(user_profile=user_profile)
        # Obtén el producto que queremos añadir al carrito
        producto = Producto.objects.get(pk=product_pk)
        # Obtén/Crea un/el pedido en proceso (EP) del usuario
        pedido, _  = Pedido.objects.get_or_create(cliente=cliente, estado='EP')
        # Obtén/Crea un/el detalle de pedido
        detalle_pedido, created = DetallePedido.objects.get_or_create(
            producto=producto,
            pedido=pedido,
        )
        if created:
            detalle_pedido.cantidad = 1
        else:
            detalle_pedido.cantidad = F('cantidad') + 1
        # Guardamos los cambios
        detalle_pedido.save()
        # Recarga la página
        return redirect(request.META['HTTP_REFERER'])

class RemoveFromCartView(View):
    def get(self, request, product_pk):
        # Obten el cliente
        user_profile = Profile.objects.get(user=request.user)
        cliente = Cliente.objects.get(user_profile=user_profile)
        # Obtén el producto que queremos añadir al carrito
        producto = Producto.objects.get(pk=product_pk)
        # Obtén/Crea un/el pedido en proceso (EP) del usuario
        pedido, _  = Pedido.objects.get_or_create(cliente=cliente, estado='EP')
        # Obtén/Crea un/el detalle de pedido
        detalle_pedido = DetallePedido.objects.get(
            producto=producto,
            pedido=pedido,
        )
        # Si la cantidad actual menos 1 es 0 elmina el producto del carrito
        # Si no restamos 1 a la cantidad actual
        if detalle_pedido.cantidad - 1 == 0:
            detalle_pedido.delete()
        else:
            detalle_pedido.cantidad = F('cantidad') - 1
            # Guardamos los cambios
            detalle_pedido.save()
        # Recarga la página
        return redirect(request.META['HTTP_REFERER'])

class PedidoDetailView(DetailView):
    
    model = Pedido
    
    def get_object(self):
        # Obten el cliente
        user_profile = Profile.objects.get(user=self.request.user)
        cliente = Cliente.objects.get(user_profile=user_profile)
        # Obtén/Crea un/el pedido en proceso (EP) del usuario
        pedido  = Pedido.objects.get(cliente=cliente, estado='EP')
        return pedido

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detalles'] = context['object'].detallepedido_set.all() #set a una lista, quita los valores repetidos, remover duplicados
        return context

class PedidoUpdateView(UpdateView):
    model = Pedido
    fields = ['ubicacion', 'direccion_entrega']
    success_url = reverse_lazy('payment')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        self.object = form.save(commit=False)
        # Calculo de tarifa
        self.object.tarifa = randint(5, 20)
        return super().form_valid(form)

class PaymentView(TemplateView):
    template_name = "main/payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obten el cliente
        user_profile = Profile.objects.get(user=self.request.user)
        cliente = Cliente.objects.get(user_profile=user_profile)
        context['pedido'] = Pedido.objects.get(cliente=cliente, estado='EP') #en proceso

        return context

class CompletePaymentView(View):
    def get(self, request):
        # Obten el cliente
        user_profile = Profile.objects.get(user=request.user)
        cliente = Cliente.objects.get(user_profile=user_profile)
        # Obtén/Crea un/el pedido en proceso (EP) del usuario
        pedido = Pedido.objects.get(cliente=cliente, estado='EP')
        # Cambia el estado del pedido
        pedido.estado = 'PAG'
        # Asignacion de repartidor
        pedido.repartidor = Colaborador.objects.order_by('?').first()
        # Guardamos los cambios
        pedido.save()
        messages.success(request, 'Gracias por tu compra! Un repartidor ha sido asignado a tu pedido.')
        return redirect('home')