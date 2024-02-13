from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .contract import wallet_contract

class RegisterUserForm(forms.Form):
    login = forms.CharField(label='Логин')
    address = forms.CharField(label='Открытый ключ')
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput())

    def clean_password1(self):
        cleaned_data = self.cleaned_data
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        validate_password(password=password1)

        if password1 != password2:
            raise ValidationError("Пароли не совпадают")

        return password1

    def clean_address(self):

        address = self.cleaned_data['address']

        val_error = ValidationError(
            ('Неправильный формат публичного ключа'),
            code='invalid_public_key')

        if len(address) != 42:
            raise val_error

        try:
            int(address, 16)
        except (ValueError, TypeError, AttributeError):
            raise val_error

        return address


