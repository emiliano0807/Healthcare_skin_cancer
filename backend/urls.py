from django.contrib import admin
from django.urls import path, include
from segmentacion.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('segmentacion.urls')),
    path('', index, name='home'), # Ruta raíz carga el HTML
]