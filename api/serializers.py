from rest_framework import serializers
from payapp.models import Currency, CurrencyTransfer, CurrencyRequest
from register.views import SignUpForm
from rest_framework import serializers


class CurrencySerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = ['username', 'currency_type', 'currency', 'email', ]

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email


class CurrencyTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyTransfer
        fields = '__all__'


class CurrencyRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyRequest
        fields = '__all__'
