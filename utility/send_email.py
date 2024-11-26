from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives


def send_email_to_user(subject_name, to_email, obj, template_location):
    subject, from_email, to = subject_name, 'info@ordersathi.com', to_email
    html_content = render_to_string(template_location, obj)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
