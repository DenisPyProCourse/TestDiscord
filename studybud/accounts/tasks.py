from django.core.mail import EmailMessage, EmailMultiAlternatives
from studybud.celery import app
from django.template import loader

from .models import User


@app.task
def send_email_verif(mail_subject, message, to_email):
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()


@app.task
def send_email_reset_pass(subject, body, from_email, to_email, html_email_template_name, context):
    context['user'] = User.objects.get(pk=context['user'])
    email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, "text/html")
    email_message.send()
