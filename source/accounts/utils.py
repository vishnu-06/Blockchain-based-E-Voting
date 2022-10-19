from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from django.conf import settings

def mail(res, toaddr, subject):
	fromaddr = "blockchainbasedvotingvit@gmail.com"
	toaddr = toaddr
	msg = MIMEMultipart() 
	msg['From'] = fromaddr 
	msg['To'] = toaddr 
	msg['Subject'] = subject
	body = res
	msg.attach(MIMEText(body, 'html'))  
	s = smtplib.SMTP('smtp.gmail.com', 587) 
	s.starttls() 
	s.login(fromaddr, settings.EMAIL_PASSWORD)  
	text = msg.as_string() 
	s.sendmail(fromaddr, toaddr, text)  
	s.quit() 


def send_mail(to, template, context):
    html_content = render_to_string(f'accounts/emails/{template}.html', context)
    text_content = render_to_string(f'accounts/emails/{template}.txt', context)
    #msg = EmailMultiAlternatives(context['subject'], text_content, settings.DEFAULT_FROM_EMAIL, [to])
    #msg.attach_alternative(html_content, 'text/html')
    mail(html_content, to, subject = context['subject'])
    


def send_activation_email(request, email, code):
    context = {
        'subject': 'Profile activation',
        'uri': request.build_absolute_uri(reverse('accounts:activate', kwargs={'code': code})),
    }

    send_mail(email, 'activate_profile', context)


def send_activation_change_email(request, email, code):
    context = {
        'subject': 'Change email',
        'uri': request.build_absolute_uri(reverse('accounts:change_email_activation', kwargs={'code': code})),
    }

    send_mail(email, 'change_email', context)


def send_reset_password_email(request, email, token, uid):
    context = {
        'subject': 'Restore password',
        'uri': request.build_absolute_uri(
            reverse('accounts:restore_password_confirm', kwargs={'uidb64': uid, 'token': token})),
    }

    send_mail(email, 'restore_password_email', context)


def send_forgotten_username_email(email, username):
    context = {
        'subject': 'Your username',
        'username': username,
    }

    send_mail(email, 'forgotten_username', context)
