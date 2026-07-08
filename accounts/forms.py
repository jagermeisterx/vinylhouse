from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta(UserCreationForm.Meta):
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Obligatorio. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_."
        self.fields["password1"].help_text = (
            "Tu contraseña no puede ser similar a tu información personal.<br>"
            "Tu contraseña debe contener al menos 8 caracteres.<br>"
            "Tu contraseña no puede ser una clave utilizada comúnmente.<br>"
            "Tu contraseña no puede ser completamente numérica."
        )
        self.fields["password2"].help_text = "Repite la misma contraseña para verificar."
