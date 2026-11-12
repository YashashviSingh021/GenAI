from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
from fastmcp import FastMCP

mcp = FastMCP(
    name="send Email",
)

sender_email = "yash210singh@gmail.com"
sender_password = "jvod kgoq lyjw wxki"



def send(email: str, subject: str, body:str) ->  str:
    receiver_email = email

    # Create email object
    message = MIMEMultipart()

    # Add email headers
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    # Attach body to email
    message.attach(MIMEText(body, "plain"))
    # Connect to Gmail SMTP server
    server = smtplib.SMTP("smtp.gmail.com", 587)

    # Secure connection using TLS
    server.starttls()

    # Login
    server.login(sender_email, sender_password)

    # Send email
    server.sendmail(
        sender_email,
        receiver_email,
        message.as_string()
    )

    

    return "Email sent successfully!"
@mcp.tool
def send_email_tool(email: str, subject: str, body:str) ->  str:
    """
        This Tool can help to send email to the given email address
    """
    return send(email, subject, body)

mcp.run(transport = "streamable-http")