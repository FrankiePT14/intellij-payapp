from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from payapp.forms import CurrencyTransferForm, CurrencyRequestForm
from .models import Currency, CurrencyRequest, TransferAmount
from django.contrib.auth.decorators import login_required
from api.views import CurrencyConversion
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@login_required
@transaction.atomic
def currency_transfer(request):
    form = CurrencyTransferForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        src_user = request.user
        dst_username = form.cleaned_data['enter_your_destination_username']
        currency_to_transfer = form.cleaned_data['enter_amount_to_transfer']

        try:
            src_currency = Currency.objects.get(user=src_user)
            dst_user = User.objects.get(username=dst_username)
            dst_currency, created = Currency.objects.get_or_create(user=dst_user)
        except User.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect('transfer')
        except Currency.DoesNotExist:
            messages.error(request, "Source currency record does not exist.")
            return redirect('transfer')

        if src_currency.currency < currency_to_transfer:
            messages.error(request, "Insufficient funds for the transfer.")
            return redirect('transfer')

        print(f"Initial balances - Sender: {src_currency.currency}, Receiver: {dst_currency.currency}")

        currency_from = src_currency.currency_type
        currency_to = dst_currency.currency_type
        converted_amount = currency_to_transfer

        if currency_from != currency_to:
            conversion_rate = CurrencyConversion().get_exchange_rate(currency_from, currency_to)
            if conversion_rate is None:
                messages.error(request, "Currency conversion rate not found.")
                return redirect('transfer')
            converted_amount *= conversion_rate
        else:

            src_currency.currency -= currency_to_transfer
            dst_currency.currency += converted_amount

            src_currency.save()
            dst_currency.save()

        history = TransferAmount(sender=src_user, recipient=dst_user, transfer_amount=converted_amount)
        history.save()

        messages.success(request, "Currency has been successfully transferred!")
        return redirect('transfer')
    else:
        form = CurrencyTransferForm()

    return render(request, "transfer.html", {"form": form})


@login_required
def transfer_history(request):
    user = request.user
    sent_transfers = TransferAmount.objects.filter(sender=user)
    received_transfers = TransferAmount.objects.filter(recipient=user)
    if not sent_transfers and not received_transfers:
        messages.info(request, "No transactions found.")
    return render(request, 'transfer_history.html', {
        'sent_transfers': sent_transfers,
        'received_transfers': received_transfers
    })


@login_required
@transaction.atomic
def currency_request(request):
    if request.method == 'POST':
        form = CurrencyRequestForm(request.POST)
        if form.is_valid():
            user = request.user
            requested_username = form.cleaned_data['enter_the_username_you_want_to_request_from']
            amount_to_request = form.cleaned_data['enter_amount_to_request']

            try:
                requested_username = User.objects.get(username=requested_username)
                CurrencyRequest.objects.create(
                    enter_your_username=user.username,
                    enter_the_username_you_want_to_request_from=requested_username,
                    enter_amount_to_request=amount_to_request
                )
                messages.success(request, "Request has been sent.")
                return redirect('home')
            except User.DoesNotExist:
                messages.error(request, "Requested user does not exist.")
        else:
            messages.error(request, "Error when submitting your request.")
    else:
        form = CurrencyRequestForm()

    return render(request, 'request.html', {'form': form})


@login_required
@transaction.atomic
def currency_request_view(request):
    requests = CurrencyRequest.objects.filter(enter_the_username_you_want_to_request_from=request.user.username)

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        response = request.POST.get('response')

        try:
            currency_request = CurrencyRequest.objects.get(pk=request_id)
            requester = User.objects.get(username=currency_request.enter_your_username)
            requestor = request.user

            if response == 'accept':
                requester_currency = Currency.objects.get(user=requester)
                requestor_currency = Currency.objects.get(user=requestor)

                if requester_currency.currency_type != requestor_currency.currency_type:
                    conversion_rate = CurrencyConversion().get_exchange_rate(requestor_currency.currency_type,
                                                                             requester_currency.currency_type)
                    if conversion_rate is None:
                        messages.error(request, "Currency conversion rate not found.")
                        return redirect('requests_page')

                    converted_amount = currency_request.enter_amount_to_request * conversion_rate
                else:
                    converted_amount = currency_request.enter_amount_to_request

                if requestor_currency.currency >= converted_amount:
                    requestor_currency.currency -= converted_amount
                    requester_currency.currency += currency_request.enter_amount_to_request
                    requestor_currency.save()
                    requester_currency.save()

                    TransferAmount.objects.create(
                        sender=requestor,
                        recipient=requester,
                        transfer_amount=currency_request.enter_amount_to_request)
                    messages.success(request, "Request accepted and funds transferred.")
                else:
                    messages.error(request, "Insufficient funds to fulfill request.")

            elif response == 'deny':
                messages.success(request, "Request denied.")
            else:
                messages.error(request, "Invalid response.")

            currency_request.delete()

        except User.DoesNotExist:
            messages.error(request, "User not found.")
        except Currency.DoesNotExist:
            messages.error(request, "Currency not found.")
        except CurrencyRequest.DoesNotExist:
            messages.error(request, "Currency request not found.")

    return render(request, 'requests_page.html', {'requests': requests})


@login_required
def profile(request):
    user = request.user
    user_currency, created = Currency.objects.get_or_create(user=user)
    currency_type = user_currency.currency_type

    sent_transfers = TransferAmount.objects.filter(sender=user)
    received_transfers = TransferAmount.objects.filter(recipient=user)

    sent_requests = CurrencyRequest.objects.filter(enter_your_username=user.username)
    received_requests = CurrencyRequest.objects.filter(enter_the_username_you_want_to_request_from=user.username)

    context = {
        'user_currency': user_currency,
        'currency_type': currency_type,
        'sent_transfers': sent_transfers,
        'received_transfers': received_transfers,
        'sent_requests': sent_requests,
        'received_requests': received_requests,

    }
    print("Sent Transfers:", sent_transfers.count())
    print("Received Transfers:", received_transfers.count())
    return render(request, "profile.html", context)


@staff_member_required
def admin_view(request):
    return render(request, 'admin-dashboard.html')


def all_transactions(request):
    all_sent_transfers = TransferAmount.objects.all().order_by('-date')
    context = {
        'all_sent_transfers': all_sent_transfers,
    }
    return render(request, 'admin_transactions.html', context)


@staff_member_required
def add_admins(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.get(pk=user_id)
        user.is_staff = not user.is_staff
        user.save()
        messages.success(request, f"Updated admin status for {user.username}.")
        return redirect('add_admins')

    users = User.objects.exclude(pk=request.user.pk)
    return render(request, 'add_admins.html', {'users': users})
