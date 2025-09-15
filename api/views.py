from rest_framework.views import APIView
from rest_framework import status
from .serializers import CurrencySerializer
from payapp.models import Currency
from django.http import JsonResponse
from rest_framework import generics, permissions
from payapp.models import Currency


class CurrencyConversion(APIView):
    EXCHANGE_RATES = [

        ('USD', 'EUR', 0.94), ('USD', 'GBP', 0.81),
        ('EUR', 'USD', 1.07), ('EUR', 'GBP', 0.86),
        ('GBP', 'USD', 1.24), ('GBP', 'EUR', 1.16),
    ]

    def get_exchange_rate(self, currency1, currency2):
        for rate in self.EXCHANGE_RATES:
            if rate[0] == currency1 and rate[1] == currency2:
                return rate[2]
            elif rate[0] == currency2 and rate[1] == currency1:
                return 1 / rate[2]
        return None

    def get(self, request, currency1, currency2, amount):
        try:
            amount = float(amount)
            rate = self.get_exchange_rate(currency1, currency2)
            if rate is None:
                return JsonResponse({'error': 'One or both currencies are not supported.'},
                                    status=status.HTTP_404_NOT_FOUND)
            converted_amount = amount * rate
            return JsonResponse({'converted_amount': converted_amount, 'rate': rate}, status=status.HTTP_200_OK)
        except ValueError:
            return JsonResponse({'error': 'Error'}, status=status.HTTP_400_BAD_REQUEST)


class CurrencyList(generics.ListAPIView):
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = Currency.objects.all()
        username = self.request.query_params.get('user')
        if username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset


class CurrencyDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Currency.objects.all()
