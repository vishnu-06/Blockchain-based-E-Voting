# import smtplib
# from email.mime.multipart import MIMEMultipart 
# from email.mime.text import MIMEText 
# from email.mime.base import MIMEBase 
# from email import encoders

# fromaddr = "mailtestq6@gmail.com"
# toaddr = "vsrivatsa25@gmail.com"
# msg = MIMEMultipart() 
# msg['From'] = fromaddr 
# msg['To'] = toaddr 
# msg['Subject'] = "ID"
# body = 'Test Email'
# msg.attach(MIMEText(body, 'plain'))  
# s = smtplib.SMTP('smtp.gmail.com', 587) 
# s.starttls() 
# s.login(fromaddr,"testpassword123@")  
# text = msg.as_string() 
# s.sendmail(fromaddr, toaddr, text)  
# s.quit() 