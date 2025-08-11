from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpRequest
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required


@require_http_methods(["GET"])  # garante cookie de CSRF
@ensure_csrf_cookie
def csrf_token_view(request: HttpRequest):
    token = get_token(request)
    return JsonResponse({"csrfToken": token})


@require_http_methods(["POST"])
def login_view(request: HttpRequest):
    try:
        import json
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    username = data.get("username")
    password = data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"detail": "Invalid credentials"}, status=401)
    login(request, user)
    return JsonResponse({"ok": True})


@require_http_methods(["POST"])
def logout_view(request: HttpRequest):
    logout(request)
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def me_view(request: HttpRequest):
    if request.user.is_authenticated:
        user = request.user
        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "role": getattr(user, 'role', ''),
        })
    return JsonResponse({"detail": "Unauthorized"}, status=401)


