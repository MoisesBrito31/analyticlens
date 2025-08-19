from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
@login_required
def home_view(request):
    """Página inicial protegida - só acessível após login"""
    return JsonResponse({
        "message": "Bem-vindo ao analyticLens!",
        "user": {
            "username": request.user.username,
            "id": request.user.id
        },
        "status": "authenticated"
    })


def health_check(request):
    """Verificação de saúde da API - não requer autenticação"""
    return JsonResponse({
        "status": "healthy",
        "message": "API funcionando corretamente",
        "timestamp": "2024-01-01T00:00:00Z"
    })
