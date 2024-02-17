import datetime

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import FormMixin
from web3 import Web3
from web3.exceptions import ContractLogicError
from .blockchain_auth_backend import BlockchainAuthBackend
from django.contrib.auth.models import User

from .forms import RegisterUserForm, LoginUserForm, SendTransferForm
from .contract import wallet_contract


class Main(View):

    template_name = 'blockchain/index.html'

    def get(self, request):
        return render(request, template_name=self.template_name)


class RegisterView(FormMixin, View):
    form_class = RegisterUserForm
    template_name = 'blockchain/register.html'
    success_url = 'login'

    @staticmethod
    def blockchain_register(form):
        args = [
            form.cleaned_data.get('address'),
            form.cleaned_data.get('login'),
            form.cleaned_data.get('password')
        ]
        try:
            wallet_contract.functions.register(*args).transact({'from': args[0]})
            return args[0]
        except ContractLogicError as e:
            form.add_error(field='address', error='Адрес занят')
            return False

    def get(self, request):
        form = RegisterUserForm()
        return render(request, template_name=self.template_name, context={'form': form})

    def post(self, request):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            address = self.blockchain_register(form)
            if address is not False:
                User.objects.create_user(username=address)
                return redirect(self.success_url)
        return render(request, template_name=self.template_name, context={'form': form})


class LoginUserView(FormMixin, View):
    form_class = LoginUserForm
    template_name = 'blockchain/login.html'
    success_url = 'profile'

    @staticmethod
    def blockchain_login(form):
        args = [
            form.cleaned_data.get('address'),
            form.cleaned_data.get('password')
        ]
        try:
            wallet_contract.functions.login(*args).transact()
            return args[0]
        except ContractLogicError:
            form.add_error(field='password', error='Пароли не совпадают')
            return False

    def get(self, request):
        form = LoginUserForm()
        return render(request, template_name=self.template_name, context={'form': form})

    def post(self, request):
        form = LoginUserForm(request.POST)
        if form.is_valid():
            address = self.blockchain_login(form)
            if address is not False:
                user = BlockchainAuthBackend().authenticate(request, address=address)
                if user is not None:
                    login(request, user, backend='blockchain.blockchain_auth_backend.BlockchainAuthBackend')

                return redirect(self.success_url)

        return render(request, template_name=self.template_name, context={'form': form})


class ProfileView(LoginRequiredMixin, View):
    template_name = 'blockchain/profile.html'

    def get_balance(self, request):
        balance = wallet_contract.functions.getBalance().call({'from': request.user.username})
        balance_ether = Web3.from_wei(balance, 'ether')
        return f"{balance_ether:.2f}ETH"

    def get_context_data(self, request):
        address = request.user.username
        name = wallet_contract.functions.getData(address).call()
        transactions_counter = wallet_contract.functions.getTransferHistory().call({'from': request.user.username})
        balance = self.get_balance(request)

        context = {
            'address': address,
            'name': name,
            'transactions_counter': transactions_counter,
            'balance': balance,
        }

        return context

    def get(self, request):
        context = self.get_context_data(request)
        return render(request, template_name=self.template_name, context=context)


class SendTransferView(LoginRequiredMixin, FormMixin, View):

    template_name = 'blockchain/send_transfer.html'
    form_class = SendTransferForm
    success_url = 'profile'

    @staticmethod
    def send_transfer(request, form):
        try:
            recipient = form.cleaned_data['recipient']
            amount = form.cleaned_data['amount']
            amount_eth = Web3.to_wei(amount, 'ether')
            wallet_contract.functions.sendTransferTo(recipient).transact(
                {'from': request.user.username, 'value': amount_eth})
            return True
        except ContractLogicError as error:
            if 'Not money' in error:
                form.add_error('amount', 'Недостаточно средств')
            if "Can't send to yourself" in error:
                form.add_error('recipient', 'Вы не можете отправить деньги самому себе')
            return False

    def get(self, request):
        form = SendTransferForm()
        return render(request, template_name=self.template_name, context={'form': form})

    def post(self, request):
        form = SendTransferForm(request.POST)
        if form.is_valid():
            if self.send_transfer(request, form):
                return redirect(self.success_url)
        return render(request, template_name=self.template_name, context={'form': form})


class GetLastTransactionsView(LoginRequiredMixin, View):

    def get(self, request):
        try:
            data = wallet_contract.functions.getAllTransfersBySender(). \
                call({'from': request.user.username})
            struct_data = []
            i = 0
            while i != 4:
                if data[0][i] != '0x0000000000000000000000000000000000000000':
                    time_obj = datetime.datetime.fromtimestamp(data[2][i])
                    formatted_time = time_obj.strftime('%Y-%m-%d-%H:%M:%S')

                    amount_ether = Web3.from_wei(data[1][i], 'ether')
                    formatted_value = f"{amount_ether:.2f}ETH"

                    cur_string = f"Получатель:|{data[0][i]} " \
                                 f"Сумма:|{formatted_value} " \
                                 f"Дата:|{formatted_time}"
                    struct_data.append(cur_string)

                i += 1

        except (ValueError, ContractLogicError):
            struct_data = 'Нет транзакций...'

        return JsonResponse(struct_data, safe=False)
