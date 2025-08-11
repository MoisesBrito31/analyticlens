from django.http import JsonResponse


def ping(_request):
    return JsonResponse({"status": "ok"})
