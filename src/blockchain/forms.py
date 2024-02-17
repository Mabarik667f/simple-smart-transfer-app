from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .contract import wallet_contract


def address_validate(address):
    val_error = ValidationError(
        ('Неправильный формат публичного ключа'),
        code='invalid_public_key')

    if len(address) != 42:
        raise val_error

    try:
        int(address, 16)
    except (ValueError, TypeError, AttributeError):
        raise val_error


class RegisterUserForm(forms.Form):
    login = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'test'}))
    address = forms.CharField(label='Открытый ключ', widget=forms.TextInput(attrs={'class': 'test'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'test'}))
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput(attrs={'class': 'test'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password != password2:
            self.add_error('password2', "Пароли не совпадают")

        try:
            validate_password(password)
        except ValidationError as e:
            self.add_error('password', e.messages)

        address = cleaned_data.get('address')
        address_validate(address)

        return cleaned_data


class LoginUserForm(forms.Form):
    address = forms.CharField(label='Открытый ключ', widget=forms.TextInput(attrs={'class': 'test'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'test'}))

    def clean_address(self):
        address = self.cleaned_data['address']
        address_validate(address)
        return address


class SendTransferForm(forms.Form):
    recipient = forms.CharField(label='Получатель', widget=forms.TextInput(attrs={'class': 'test'}))
    amount = forms.FloatField(label='Сумма', widget=forms.NumberInput(attrs={'class': 'test'}))

    def clean_recipient(self):

        recipient = self.cleaned_data['recipient']
        address_validate(recipient)
        return recipient
