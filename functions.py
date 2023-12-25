import os
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from authentication.models import Order
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_otp(email, otp):
    sender_email = "noreply@sizeupp.com"
    sender_password = "Dristi@98s"
    recipient_email = email
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
        <!-- Your HTML content here -->
    </html>
    """.format(first_name=email, otp=otp)

    message.attach(MIMEText(body, "html"))

    # Connect to the SMTP server
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        # Login to the SMTP server
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())

    print("OTP sent successfully!")

# Call the function with user and OTP
send_email_otp(user, otp)


def send_email_reset_link( user, link,user_email):
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = os.environ.get("EMAIL_PORT")

    email_backend = EmailBackend(
        host=EMAIL_HOST,
        port=EMAIL_PORT,
        username=EMAIL_HOST_USER,
        password=EMAIL_HOST_PASSWORD,
        use_tls=True,
    )
    subject = "SizeUpp One Time Password (OTP)"
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
                                        Hi {first_name} And Welcome To SizeUpp!</h3>
                                </td>

                                <td>
                                    <p
                                        style="font-size: 14px;font-weight: 600;width: 82%;margin: 8px auto 0;line-height: 1.5;color: #939393;font-family: 'Nunito Sans', sans-serif;">
                                        We hope our product will lead you, like many other before you. to a place where
                                        yourideas where your ideas can spark and grow.n a place where you’ll find all
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
                                    <a href="{link}" class="password-button">{link}</button>
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
                                            class="theme-color">Size Upp@example.com</span> or vixit our <span
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
    """.format(first_name=user.first_name,link=link)
    recipients = [user_email]

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=EMAIL_HOST_USER,
        to=recipients,
        connection=email_backend,
    )
    email.content_subtype = "html"
    email.send(fail_silently=False,
)















def send_email_receipt(request,order_id,user):
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = os.environ.get("EMAIL_PORT")

    invoice_url =f'http://127.0.0.1:8000/invoice/{order_id}'

    email_backend = EmailBackend(
        host=EMAIL_HOST,
        port=EMAIL_PORT,
        username=EMAIL_HOST_USER,
        password=EMAIL_HOST_PASSWORD,
        use_tls=True,
    )
    subject = "Receipt of Purchase Order "
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
                                                yourideas where your ideas can spark and grow.n a place where you’ll find all
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
                                        button  
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
                                                    class="theme-color">Size Upp@example.com</span> or vixit our <span
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



            """.format(first_name=user.first_name)
    recipients = [user.email]
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=EMAIL_HOST_USER,
        to=recipients,
        connection=email_backend,
    )
    email.content_subtype = "html"
    email.send()
