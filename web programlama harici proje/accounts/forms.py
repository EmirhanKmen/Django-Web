"""
Sahaflar Platformu — Accounts Forms
User registration, login, and profile forms.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()


class PulseLoginForm(AuthenticationForm):
    """Custom styled login form."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Kullanıcı adı',
            'autocomplete': 'username',
            'id': 'login-username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Şifre',
            'autocomplete': 'current-password',
            'id': 'login-password',
        })
    )


class PulseRegistrationForm(UserCreationForm):
    """Custom styled registration form."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'E-posta adresi',
            'id': 'register-email',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Kullanıcı adı',
                'id': 'register-username',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ad',
                'id': 'register-firstname',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Soyad',
                'id': 'register-lastname',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Şifre',
            'id': 'register-password1',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Şifre (tekrar)',
            'id': 'register-password2',
        })


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number',
                  'organization', 'location', 'bio', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-firstname'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-lastname'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'id': 'profile-email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-phone'}),
            'organization': forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-org'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'id': 'profile-location'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 4,
                'id': 'profile-bio',
            }),
            'avatar': forms.FileInput(attrs={'class': 'form-file-input', 'id': 'profile-avatar'}),
        }
