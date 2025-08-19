from django.urls import path
from .views import home_view, health_check

urlpatterns = [
    path('', health_check, name='health_check'),  # Rota raiz da API
    path('home', home_view, name='home'),
    # Outras rotas da API serão adicionadas gradualmente
]


