"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Django - deve vir PRIMEIRO
    path('admin/', admin.site.urls),
    
    # APIs específicas
    path('api/', include('api.urls')),
    path('api/auth/', include('user.urls')),
    
    # Arquivos estáticos e media
    path('static/', include('django.contrib.staticfiles.urls')),
    
    # Fallback SPA para rotas do Vue Router (deve ser o ÚLTIMO)
    # IMPORTANTE: Esta rota só captura rotas que NÃO foram capturadas pelas rotas específicas acima
    # Usando uma abordagem mais específica para evitar conflitos
    re_path(r'^(?!admin|api|static|media).*$', 
            TemplateView.as_view(template_name='index.html'), name='vue_fallback'),
]

# Servir media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
