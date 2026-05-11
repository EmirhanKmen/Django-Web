from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Adınız Soyadınız', 'id': 'contact-name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'E-posta adresiniz', 'id': 'contact-email'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Konu', 'id': 'contact-subject'}),
            'message': forms.Textarea(attrs={'class': 'form-input form-textarea', 'placeholder': 'Mesajınız...', 'rows': 5, 'id': 'contact-message'}),
        }
