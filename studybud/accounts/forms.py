from allauth.socialaccount.forms import SignupForm
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.template import loader

from .models import User
from .tasks import send_email_reset_pass


class MyUserCreationForm(SignupForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        return username.lower()

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        username = self.cleaned_data['username']
        username = first_name
        return username.lower




class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio', 'lnkdn']

    def clean_lnkdn(self):
        lnkdn = self.cleaned_data['lnkdn']
        if lnkdn is not None and 'linkedin' not in lnkdn:
            raise ValidationError('Not a LinkedIn link', code='invalid')
        return lnkdn

    def clean_username(self):
        username = self.cleaned_data['username']
        return username.lower()


class MyPasswordResetForm(PasswordResetForm):

    def send_mail(self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        context['user'] = context['user'].id
        subject = loader.render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        send_email_reset_pass.delay(subject, body, from_email, to_email, html_email_template_name, context)
