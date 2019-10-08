import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import header, utils, encoders
from email import message_from_string

from base import Message


class SMTPManager(object):

    def __init__(self, host, user, password):
        self.__host = host
        self.__user = user
        self.__password = password

    def send_email(self, message):
        msg_mime = MIMEMultipart()

        msg_mime['From'] = message.from_addr
        msg_mime['To'] = message.to_addr
        msg_mime['Subject'] = message.subject

        msg_mime.attach(MIMEText(message.body, 'plain'))

        for attach in message.attachs:
            filepath = message.get_attach_path(attach)
            attachment = open(filepath, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            f'attachment; filename= {attach}')
            msg_mime.attach(part)
            attachment.close()

        smtp = smtplib.SMTP_SSL(self.__host)
        smtp.login(self.__user, self.__password)
        text = msg_mime.as_string()
        smtp.sendmail(message.from_addr, message.to_addr, text)
        print(f'msg sent {message.subject}')

        smtp.quit()
