import RPi.GPIO as GPIO
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# GPIOsettings
channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

# emailsettings
smtp_server = "smtp.qq.com"
smtp_port = 587
sender_email = "1247088821@qq.com"
sender_password = "bsktpyvcdqcabaaj"
receiver_email = "2579693602@qq.com"

# 
last_status = None
status_messages = {
    True: "[Real-time status] Dry! ✖ (GPIO HIGH)",
    False: "[Real-time status] Damp ✓ (GPIO LOW)"
}

def create_email_html(status, message):
    """Email HTML UI"""
    status_icon = "❌" if status == "Dry" else "✅"
    status_color = "#FF5252" if status == "Dry" else "#4CAF50"
    action_text = "Need Water!" if status == "Dry" else "Dosen't Need Water!"
    
    return f"""
<html>
    <head>
        <style>
            body {{ font-family: 'Arial', sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 20px auto; padding: 20px; border-radius: 10px; background: #f9f9f9; }}
            .header {{ color: #333; text-align: center; border-bottom: 2px solid {status_color}; padding-bottom: 10px; }}
            .status-box {{ background: white; padding: 15px; border-radius: 5px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .status {{ font-size: 24px; color: {status_color}; text-align: center; }}
            .footer {{ text-align: center; font-size: 12px; color: #777; margin-top: 20px; }}
            .action {{ background: {status_color}; color: white; padding: 10px 15px; border-radius: 5px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🌱 Soil Sensor Report</h2>
                <p>Automatic Report • {datetime.now().strftime('%Y/%m/%d %H:%M')}</p>
            </div>
            
            <div class="status-box">
                <div class="status">
                    {status_icon} Current Status: {message}
                </div>
                <p style="text-align: center; margin-top: 15px;">
                    <span class="action">{action_text}</span>
                </p>
            </div>
            
            <div>
                <h3>📊 Detals</h3>
                <ul>
                    <li><strong>Detection Time: </strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                    <li><strong>Sendor Value: </strong> {"HIGH (Dry)" if status == "Dry" else "LOW (Damp)"}</li>
                    <li><strong>Next Detection Time: </strong> {get_next_check_time()}</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>This Email Wat Automatically Sent by Raspberry Pi</p>
                <p>© 2025 Soil Sensor System</p>
            </div>
        </div>
    </body>
</html>
"""

def get_next_check_time():
    """Get Next Time for Inspection"""
    now = datetime.now()
    check_times = [(8, 0), (12, 0), (14, 30), (16, 0), (20, 0)]
    current_time = (now.hour, now.minute)
    
    for time in check_times:
        if time > current_time or (time == current_time and now.second < 59):
            return f"Today {time[0]}:{str(time[1]).zfill(2)}"
    
    return "Tomorrow 8:00"

def check_moisture():
    """Monitor Soil Moisture"""
    current_state = GPIO.input(channel)
    return current_state, "Dry" if current_state else "Damp"

def display_status(state):
    """Real-time Display of Status"""
    global last_status
    if state != last_status:
        print("\n" + "="*40)
        print(status_messages[state])
        print(f"Detection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*40 + "\n")
        last_status = state

def send_email(status, message):
    """sendHtmlEamil"""
    subject = f"🌱 Plant{'Needs Water!' if status == 'Dry' else 'Damp'} - {datetime.now().strftime('%H:%M')}"
    
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    # HTML
    html_content = create_email_html(status, message)
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"{datetime.now().strftime('%H:%M')} - Email was Sent Sucessfully: {status}")
    except Exception as e:
        print(f"Fail to Send Email: {e}")
    finally:
        if 'server' in locals():
            server.quit()

def run_daily_check():
    """"""
    check_times = [(8, 0), (10,0), (12,30), (16, 0), (20, 0)]
    
    current_state, status = check_moisture()
    display_status(current_state)
    
    while True:
        now = datetime.now()
        current_time = (now.hour, now.minute)
        
        if current_time in check_times and now.second == 0: 
            current_state, status = check_moisture()
            send_email(status, "Dry" if current_state else "Damp")
            time.sleep(1) 
        
        current_state, _ = check_moisture()
        display_status(current_state)
        time.sleep(5)

if __name__ == "__main__":
    try:
        print("\n" + "="*50)
        print("The Detection System Has been Activated.".center(40))
        print(f"Detection Time: 8:00, 10:00, 12:30, 16:00, 20:00".center(40)) 
        print("="*50 + "\n")
        
        GPIO.add_event_detect(
            channel, 
            GPIO.BOTH, 
            bouncetime=300, 
            callback=lambda x: display_status(GPIO.input(channel)))
        
        run_daily_check()
        
    except KeyboardInterrupt:
        print("\nSystem Has been Stopped.")
    finally:
        GPIO.cleanup()
