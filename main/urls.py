from django.urls import path

from . import views #. dentro de este grupo de carpetas (main)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'), #aqui llamas al view de home
    path('productos', views.ProductListView.as_view(), name='product-list'),
    path('productos/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),
    path('registro/', views.RegistrationView.as_view(), name='register'),  
    path('add_to_cart/<int:product_pk>', views.AddToCartView.as_view(), name='add-to-cart'),
    path('remove_from_cart/<int:product_pk>', views.RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('carrito/', views.PedidoDetailView.as_view(), name='pedido-detail'),
    path('checkout/<int:pk>', views.PedidoUpdateView.as_view(), name='pedido-update'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('complete_payment/', views.CompletePaymentView.as_view(), name='complete-payment'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#dentro de url patterns se pone todas las urls, de cada paginas, el path es lo que va luego del /, para home es vacio usualmente
#y desde aqui digo este es el url
#luego debemos asociar esta vista con el url