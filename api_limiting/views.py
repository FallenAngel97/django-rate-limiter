from django.http import HttpResponse


def api_rate_limited(request):
    return HttpResponse(status=201)
