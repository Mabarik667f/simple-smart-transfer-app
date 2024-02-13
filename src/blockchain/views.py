from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormMixin

from .forms import RegisterUserForm
from .contract import wallet_contract


class Main(View):

    template_name = 'blockchain/index.html'

    def get(self, request):
        return render(request, template_name=self.template_name)


class RegisterView(View, FormMixin):
    form_class = RegisterUserForm
    template_name = 'blockchain/register.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form(form_class=self.form_class)
        return render(request, template_name=self.template_name, context={'form': form})

    def post(self, request):
        form = RegisterUserForm(request.POST)
        # запрос к контракту
        address = request.POST['address']
        if form.is_valid():
            print(form.cleaned_data)
            s = wallet_contract.functions.getBalance().call()
            print(s)
            return HttpResponse(s)
        else:
            return render(request, template_name=self.template_name, context={'form': form})


class LoginView(View, FormMixin):
    pass