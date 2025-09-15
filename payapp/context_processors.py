from .models import CurrencyRequest


def currency_requests_context(request):
    if request.user.is_authenticated:
        has_requests = CurrencyRequest.objects.filter(enter_the_username_you_want_to_request_from=request.user).exists()
        return {'show_requests_page': has_requests}
    return {'show_requests_page': False}
