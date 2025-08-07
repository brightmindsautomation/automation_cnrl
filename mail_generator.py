"""
This python file used to create a html table (body), and send the same in mail using smtp
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def html_format(df, receiver):
    """
    Function used to format the html table
    :param df: dataframe
    :return: html table
    """
    html_table = df.to_html(index=False, border=1)
    html_body = f"""
    <html>
      <body>
        <p>Dear {receiver},</p>
        <p>Please find below the requested data:</p>
        {html_table}
      </body>
    </html>
    """
    return html_body

def mail_setup(html_content):
    """
    Function used to setup the email
    :return: Message as per the status
    """
    try:
        print("Inside the mail function")
        sender_email = "greenblossom2019@gmail.com"
        receiver_email = "greenblossom2019@gmail.com"
        password = "ycdc pjix jves duyt"  # Use app-specific password if using Gmail
        subject = "Dataframe Report"

        # Create the email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        # Attach the HTML body
        msg.attach(MIMEText(html_content, "html"))

        # Send the email via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Mail sent successfully")
        return True

    except Exception as e:
        print("Exception occured while calling mail setup", e)
        return False