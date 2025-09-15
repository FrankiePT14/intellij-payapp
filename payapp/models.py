from django.db import models
from django.contrib.auth.models import User
from django.db import transaction


class Currency(models.Model):
    CURRENCY_CHOICES = [
        ('GBP', 'Great British Pounds'),
        ('USD', 'US Dollars'),
        ('EUR', 'Euros'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='currencies')
    currency_type = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')
    currency = models.IntegerField(default=1000)

    def flag(self):
        flags = {
            'GBP': 'media/flags/gdp.png',
            'USD': 'media/flags/usd.png',
            'EUR': 'media/flags/eur.png',
        }
        return flags.get(self.currency_type, 'media/flags/default.png')

    EXCHANGE_RATES_SIGNUP = {
        ('GBP', 'USD'): 1.24,
        ('GBP', 'EUR'): 1.16,
    }

    def save(self, *args, **kwargs):
        if not self.pk and self.currency_type != 'GBP':
            exchange_rate = self.EXCHANGE_RATES_SIGNUP.get(('GBP', self.currency_type))
            if exchange_rate is None:
                raise ValueError("Currency conversion rate not found.")
            self.currency = int(self.currency * exchange_rate)
        super().save(*args, **kwargs)

    def __str__(self):
        details = ''
        details += f'Username     : {self.user}\n'
        details += f'Currency       : {self.currency}\n'
        details += f'Currency Type    :{self.currency_type}\n'
        return details


class CurrencyTransfer(models.Model):
    enter_your_username = models.CharField(max_length=50)
    enter_your_destination_username = models.CharField(max_length=50)
    enter_amount_to_transfer = models.IntegerField()

    def __str__(self):
        details = ''
        details += f'Your username            : {self.enter_your_username}\n'
        details += f'Destination username     : {self.enter_your_destination_username}\n'
        details += f'Amount To Transfer         : {self.enter_amount_to_transfer}\n'
        return details


class CurrencyRequest(models.Model):
    enter_your_username = models.CharField(max_length=50)
    enter_the_username_you_want_to_request_from = models.CharField(max_length=50)
    enter_amount_to_request = models.IntegerField()

    def __str__(self):
        details = ''
        details += f'Your username             : {self.enter_your_username}\n'
        details += f'User to Request from      : {self.enter_the_username_you_want_to_request_from}\n'
        details += f'Amount to Request         : {self.enter_amount_to_request}\n'
        return details


class TransferAmount(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transfers')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transfers')
    transfer_amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        details = ''
        details += f'Your Username              : {self.sender.username}\n'
        details += f'Recipient Username         : {self.recipient.username}\n'
        details += f'Transfer Amount            : {self.transfer_amount}\n'
        return details
