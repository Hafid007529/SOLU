from django.contrib import admin

#from .models import Localizacion, Producto, Categoria, Proveedor #va mostrar los objetos, antes se importa, luego los registra
from .models import *
#te permite espiar, estamos creando la opción de visualizar a tus cliente, colaboradores, etc
class ClienteInline(admin.TabularInline):
    model=Cliente

class ColaboradorInline(admin.TabularInline):
    model=Colaborador

class ProfileAdmin(admin.ModelAdmin):
    inlines = [
        ClienteInline,
        ColaboradorInline
    ]

class ProductoImageInline(admin.TabularInline):
    model=ProductoImage


class ProductoAdmin(admin.ModelAdmin):
    inlines = [
        ProductoImageInline,
    ]
# Cliente, Colaborador, Profile, 

# Register your models here.
admin.site.register(Localizacion)
#admin.site.register(Producto)

admin.site.register(Categoria)
admin.site.register(Proveedor)
# Register your models here.
#tmb se pudo poner *
admin.site.register(Cliente)
admin.site.register(Colaborador)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Producto, ProductoAdmin)