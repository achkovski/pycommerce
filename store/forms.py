from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'you@example.com'}),
            'subject': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Subject (optional)'}),
            'message': forms.Textarea(attrs={'class': 'textarea', 'rows': 5, 'placeholder': 'How can we help?'}),
        }
