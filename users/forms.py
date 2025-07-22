from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
        
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "from_city",
            "phone_number",
            "adress",
        )
        widgets = {
            'adress': forms.Textarea(attrs={'rows': 3, 'cols': 30,'placeholder': 'Adresinizi buraya yazınız...',}),
          
        }
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "from_city",
            "phone_number",
            "adress",  
        ) 
        widgets = {
            'adress': forms.Textarea(attrs={'rows': 3, 'cols': 30,}),
          
        }