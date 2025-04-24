import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# email settings
smtp_server = "smtp.qq.com"  
smtp_port = 587  
sender_email = "1247088821@qq.com"  
sender_password = "bsktpyvcdqcabaaj" 
receiver_email = "2579693602@qq.com" 

# write email
subject = "Test email"
body = """
Hello, Raspberry Pi
"""

message = MIMEMultipart()
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = subject
message.attach(MIMEText(body, 'plain'))

server = None 
try:
    # connect SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  
    server.login(sender_email, sender_password)
    
    # send email
    server.sendmail(sender_email, receiver_email, message.as_string())
    print("Send successfully!")
    
except Exception as e:
    print(f"Fail to send!: {e}")
    
finally:
    if server: 
        server.quit()
