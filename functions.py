import os
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from authentication.models import Order

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



def send_welcome_email(user):
    sender_email = "noreply@sizeupp.com"
    sender_password = "Dristi@98s"
    recipient_email = user.email
    smtp_server = "smtpout.secureserver.net"
    smtp_port = 465

    # Create a MIME object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "Wlcome to SizeUpp"
    project_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(project_dir, "templates", "email", "welcome.html")

    # Read the content of otp.html
    with open(file_path, "r") as file:
        otp_html_content = file.read()

    # Add HTML content to the message
    body = otp_html_content.format(
    name=user.first_name,
    # first_name=user.first_name,
    # last_name=user.last_name,
    # phone_number=user.phone,
    # email=user.email,
    # username=user.email,  # Assuming username is the same as the email
    # help_url="https://www.sizeupp.com/help"  # Replace with your actual help URL
)    
    message.attach(MIMEText(body, "html"))

    # Connect to the SMTP server
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        # Login to the SMTP server
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())

    print("OTP sent successfully!")
# Call the function with user and OTP
# send_email_otp(user, otp)





def send_email_otp(user, otp):
    sender_email = "noreply@sizeupp.com"
    sender_password = "Dristi@98s"
    recipient_email = user.email
    smtp_server = "smtpout.secureserver.net"
    smtp_port = 465

    # Create a MIME object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "SizeUpp One Time Password (OTP)"

    # Add HTML content to the message
    body = """
    
    <!DOCTYPE html>
<html lang="en">


<div style="margin: 20px auto;
text-align: center; margin: 0 auto; width: 650px; font-family: 'Public Sans', sans-serif; background-color: #e2e2e2; display: block;
        
">
    <table align="center" border="0" cellpadding="0" cellspacing="0"
        style="background-color: white; width: 100%; box-shadow: 0px 0px 14px -4px rgba(0, 0, 0, 0.2705882353);-webkit-box-shadow: 0px 0px 14px -4px rgba(0, 0, 0, 0.2705882353);">
        <tbody>
            <tr>
                <td>
                    <table class="header-table" align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr class="header"
                            style="background-color: #f7f7f7;display: flex;align-items: center;justify-content: space-between;width: 100%;">
                            <td class="header-logo" style="padding: 10px 32px;">
                                <a href="../front-end/index.html" style="display: block; text-align: left;">
                                    <img src="http://127.0.0.1:8000/static/assets/images/logo/logo_5.png" class="main-logo" alt="logo">
                                </a>
                            </td>
                        </tr>
                    </table>

                 

                    <table class="contant-table" style="margin-top: 40px;" align="center" border="0" cellpadding="0"
                        cellspacing="0" width="100%">
                        <thead>
                            <tr style="display: block;">
                                <td style="display: block;">
                                    <h3
                                        style="font-weight: 700; font-size: 20px; margin: 0; text-transform: uppercase;">
                                        Hi {first_name} And Welcome To SizeUpp!</h3>
                                </td>

                                <td>
                                    <p
                                        style="font-size: 14px;font-weight: 600;width: 82%;margin: 8px auto 0;line-height: 1.5;color: #939393;font-family: 'Nunito Sans', sans-serif;">
                                        We hope our product will lead you, like many other before you. to a place where
                                        your ideas where your ideas can spark and grow.n a place where you’ll find all
                                        your inspiration needs. before we get started, we’ll need to verify your email.
                                    </p>
                                </td>
                            </tr>
                        </thead>
                    </table>

                    <table class="button-table" style="margin: 34px 0;" align="center" border="0" cellpadding="0"
                        cellspacing="0" width="100%">
                        <thead>
                            <tr style="display: block;">
                                <td style="display: block;">
                                    <button class="password-button">{otp}</button>
                                </td>
                            </tr>
                        </thead>
                    </table>

                    <table class="contant-table" align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
                        <thead>
                            <tr style="display: block;">
                                <td style="display: block;">
                                    <p
                                        style="font-size: 14px; font-weight: 600; width: 82%; margin: 0 auto; line-height: 1.5; color: #939393; font-family: 'Nunito Sans', sans-serif;">
                                        If you have any question, please email us at <span
                                            class="theme-color">feedback@SizeUpp.com</span> or visit our <span
                                            class="theme-color">FAQs.</span></p>
                                </td>
                            </tr>
                        </thead>
                    </table>

                    <table class="text-center footer-table" align="center" border="0" cellpadding="0" cellspacing="0"
                        width="100%"
                        style="background-color: #282834; color: white; padding: 24px; overflow: hidden; z-index: 0; margin-top: 30px;">
                        <tr>
                            <td>
                                <table border="0" cellpadding="0" cellspacing="0" class="footer-social-icon text-center"
                                    align="center" style="margin: 8px auto 11px;">
                                    <tr>
                                        <td>
                                            <h4 style="font-size: 19px; font-weight: 700; margin: 0;">Shop For <span
                                                    class="theme-color">Size Upp</span></h4>
                                        </td>
                                    </tr>
                                </table>
                               
                                
                                
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </tbody>
    </table>
</div>

</html>
    """.format(first_name=user.first_name,otp=otp)
    


    message.attach(MIMEText(body, "html"))

    # Connect to the SMTP server
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        # Login to the SMTP server
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())

    print("OTP sent successfully!")


def send_email_receipt(request,order_id,user):
    sender_email = "noreply@sizeupp.com"
    sender_password = "Dristi@98s"
    recipient_email = user.email
    smtp_server = "smtpout.secureserver.net"
    smtp_port = 465

    # Create a MIME object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message['subject'] = "Receipt of Purchase Order "
    body = """


            <!DOCTYPE html>
        <html lang="en">


        <div style="margin: 20px auto;
        text-align: center; margin: 0 auto; width: 650px; font-family: 'Public Sans', sans-serif; background-color: #e2e2e2; display: block;
                
        ">
            <table align="center" border="0" cellpadding="0" cellspacing="0"
                style="background-color: white; width: 100%; box-shadow: 0px 0px 14px -4px rgba(0, 0, 0, 0.2705882353);-webkit-box-shadow: 0px 0px 14px -4px rgba(0, 0, 0, 0.2705882353);">
                <tbody>
                    <tr>
                        <td>
                            <table class="header-table" align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr class="header"
                                    style="background-color: #f7f7f7;display: flex;align-items: center;justify-content: space-between;width: 100%;">
                                    <td class="header-logo" style="padding: 10px 32px;">
                                        <a href="https://sizeupp.com/" style="display: block; text-align: left;">
                                            <img src="https://www.sizeupp.com/assets/logo-DJXYCXpX.png" class="main-logo" style="width:50%" alt="logo">
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <table class="contant-table" style="margin-bottom: -6px;" align="center" border="0" cellpadding="0"
                                cellspacing="0" width="100%">
                                <thead>
                                    <tr>
                                        <td>
                                            <img src="https://themes.himani'cc.com.com/Size Upp/email-templete/images/welcome-poster.jpg" alt="">
                                        </td>
                                    </tr>
                                </thead>
                            </table>

                            <table class="contant-table" style="margin-top: 40px;" align="center" border="0" cellpadding="0"
                                cellspacing="0" width="100%">
                                <thead>
                                    <tr style="display: block;">
                                        <td style="display: block;">
                                            <h3
                                                style="font-weight: 700; font-size: 20px; margin: 0; text-transform: uppercase;">
                                                Hi {first_name} And Thank You For purchesing Products From your Website!</h3>
                                        </td>

                                        <td>
                                            <p
                                                style="font-size: 14px;font-weight: 600;width: 82%;margin: 8px auto 0;line-height: 1.5;color: #939393;font-family: 'Nunito Sans', sans-serif;">
                                                We hope our product will lead you, like many other before you. to a place where
                                                your ideas  can spark and grow.n a place where you’ll find all
                                                your inspiration needs.
                                            </p>
                                        </td>
                                    </tr>
                                </thead>
                            </table>

                            <table class="button-table" style="margin: 34px 0;" align="center" border="0" cellpadding="0"
                                cellspacing="0" width="100%">
                                <thead>
                                    <tr style="display: block;">
                                        <a href="https://dashboard.sizeupp.com/invoice/{order_id}" class="btn btn-primary">View Receipt<a>  
                                    </tr>
                                </thead>
                            </table>

                            <table class="contant-table" align="center" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <thead>
                                    <tr style="display: block;">
                                        <td style="display: block;">
                                            <p
                                                style="font-size: 14px; font-weight: 600; width: 82%; margin: 0 auto; line-height: 1.5; color: #939393; font-family: 'Nunito Sans', sans-serif;">
                                                If you have any question, please email us at <a href="mailto:feedback@sizeupp.com"
                                                    class="theme-color">feedback@sizeupp.com</a> or visit our <span
                                                    class="theme-color">FAQs.</span> You can also chat with a real live human
                                                during our operating hours. they can answer questions about account or help you
                                                with your meditation practice.</p>
                                        </td>
                                    </tr>
                                </thead>
                            </table>

                            <table class="text-center footer-table" align="center" border="0" cellpadding="0" cellspacing="0"
                                width="100%"
                                style="background-color: #282834; color: white; padding: 24px; overflow: hidden; z-index: 0; margin-top: 30px;">
                                <tr>
                                    <td>
                                        <table border="0" cellpadding="0" cellspacing="0" class="footer-social-icon text-center"
                                            align="center" style="margin: 8px auto 11px;">
                                            <tr>
                                                <td>
                                                    <h4 style="font-size: 19px; font-weight: 700; margin: 0;">Shop For <span
                                                            class="theme-color">Size Upp</span></h4>
                                                </td>
                                            </tr>
                                        </table>
                                    
                                        
                                        
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        </html>



            """.format(first_name=user.first_name,order_id=order_id)
    message.attach(MIMEText(body, "html"))

    # Connect to the SMTP server
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        # Login to the SMTP server
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())
