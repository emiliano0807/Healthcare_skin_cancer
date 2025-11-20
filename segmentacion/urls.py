from django.urls import path
# CAMBIO IMPORTANTE AQUÍ: Usamos el nuevo nombre 'SkinAnalysisView'
from .views import SkinAnalysisView 

urlpatterns = [
    path('predict/', SkinAnalysisView.as_view(), name='predict'),
]