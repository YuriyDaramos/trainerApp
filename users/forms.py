from django import forms
from django.contrib.auth.models import User

from users.models import Rating


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    is_trainer = forms.BooleanField(required=False, label="Check if you a trainer:")
    username = forms.CharField(help_text="")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords doesn't match!")

        return cleaned_data


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class RatingAndCommentForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["rate", "text"]

    rate = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)],
                             widget=forms.RadioSelect,
                             required=True)
    text = forms.CharField(widget=forms.Textarea, required=False)
