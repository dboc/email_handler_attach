import smtplib
import imaplib
import email
import os
import os.path
import base64
import subprocess
import sys
from shutil import copyfile

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

HOST_SMTP = "smtp.gmail.com"
HOST_IMAP = "imap.gmail.com"
USER = "hmcamila.caixa"
PSS = ""
FROM_ADDR = 'hmcamila.caixa@gmail.com'
# TO_ADDR = 'camila.martins@caixa.gov.br'
TO_ADDR = 'danielcobd@gmail.com'


class Message:
    from_addr = FROM_ADDR
    to_addr = TO_ADDR

    def __init__(self):
        self._subject = ''
        self.rec_addr = ''
        self.body = ''
        self.date = ''
        self.attachs = []

    @property
    def subject(self):
        return f'[{self.to_addr}] {self._subject}'

    @subject.setter
    def subject(self, value):
        self._subject = value


class MessageProcessed:
    from_addr = FROM_ADDR
    to_addr = TO_ADDR

    def __init__(self, msgParent, attach):
        self._subject = msgParent._subject
        self.rec_addr = msgParent.rec_addr
        self.body = msgParent.body
        self.date = msgParent.date
        self.attachs = attach
        self.partnum = 0

    @property
    def subject(self):
        if(self.partnum > 0):
            return f'[{self.to_addr}] {self._subject} {self.attachs}'
        else:
            return f'[{self.to_addr}] {self._subject} {self.attachs}[{self.partnum}]'

    @subject.setter
    def subject(self, value):
        self._subject = value


def send_email(message):
    msg_mime = MIMEMultipart()

    msg_mime['From'] = message.from_addr
    msg_mime['To'] = message.to_addr
    msg_mime['Subject'] = message.subject

    msg_mime.attach(MIMEText(message.body, 'plain'))

    if(len(message.attachs) != 0 and isinstance(message, MessageProcessed)):
        filepath = f'./{message.attachs}'
        attachment = open(filepath, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition",
                        f"attachment; filename= {message.attachs}")
        msg_mime.attach(part)
        attachment.close()
    elif(len(message.attachs) != 0):
        for attach in message.attachs:
            filepath = f'./{attach}'
            attachment = open(filepath, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition",
                            f"attachment; filename= {attach}")
            msg_mime.attach(part)
            attachment.close()
    smtp = smtplib.SMTP_SSL(HOST_SMTP)
    smtp.login(USER, PSS)
    text = msg_mime.as_string()
    smtp.sendmail(message.from_addr, message.to_addr, text)
    print(f"msg sent {message.subject}")
    smtp.quit()


def verify_email():

    list_message = []

    imap = imaplib.IMAP4_SSL(HOST_IMAP)
    imap.login(USER, PSS)
    imap.select()
    res, data = imap.search(None, "X-GM-RAW in:PROCESSAR")
    mail_ids = data[0]
    id_list = mail_ids.split()

    for num in id_list:

        res, data = imap.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        # converts byte literal to string removing b''
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        r_message = Message()
        r_message.rec_addr = email_message.get('From')
        r_message.subject = email_message.get('Subject')
        r_message.date = email_message.get('Date')

        # downloading attachments and body
        for part in email_message.walk():
            # this part comes from the snipped I don't understand yet...
            if part.get_content_type() == 'text/plain':
                r_message.body = part.get_payload()
                continue
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            fileName = part.get_filename()
            if bool(fileName):
                filePath = "./" + fileName
                if not os.path.isfile(filePath):
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                print(f'Downloaded "{fileName}"')
                r_message.attachs.append(fileName)
        imap.store(num, '+X-GM-LABELS', 'PROCESSADO')
        imap.store(num, '-X-GM-LABELS', 'PROCESSAR')
        list_message.append(r_message)
    imap.close()
    imap.logout()
    return list_message


def compress(input_file_path, output_file_path, power=0):
    """Function to compress PDF via Ghostscript command line interface"""
    quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }

    # Basic controls
    # Check if valid path
    if not os.path.isfile(input_file_path):
        print("Error: invalid path for input PDF file")
        sys.exit(1)

    # Check if file is a PDF by extension
    if input_file_path.split('.')[-1].lower() != 'pdf':
        print("Error: input file is not a PDF")
        sys.exit(1)

    print("Compress PDF...")
    initial_size = os.path.getsize(input_file_path)
    subprocess.call([r'C:\Program Files\gs\gs9.27\bin\gswin64c.exe', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                     '-dPDFSETTINGS={}'.format(quality[power]),
                     '-dNOPAUSE', '-dQUIET', '-dBATCH',
                     '-sOutputFile={}'.format(output_file_path),
                     input_file_path]
                    )
    final_size = os.path.getsize(output_file_path)
    ratio = 1 - (final_size / initial_size)
    print("Compression by {0:.0%}.".format(ratio))
    print("Final file size is {0:.1f}MB".format(final_size / 1000000))
    print("Done.")


def split_attach(input_file_path):
    """Function to compress PDF via Ghostscript command line interface"""

    # Basic controls
    # Check if valid path
    if not os.path.isfile(input_file_path):
        print("Error: invalid path for input PDF file")
        sys.exit(1)

    # Check if file is a PDF by extension
    if input_file_path.split('.')[-1].lower() != 'pdf':
        print("Error: input file is not a PDF")
        sys.exit(1)

    print("Compress PDF...")
    initial_size = os.path.getsize(input_file_path)
    subprocess.call([r'C:\Program Files\gs\gs9.27\bin\gswin64c.exe', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                     '-dPDFSETTINGS={}'.format(quality[power]),
                     '-dNOPAUSE', '-dQUIET', '-dBATCH',
                     '-sOutputFile={}'.format(output_file_path),
                     input_file_path]
                    )
    final_size = os.path.getsize(output_file_path)
    ratio = 1 - (final_size / initial_size)
    print("Compression by {0:.0%}.".format(ratio))
    print("Final file size is {0:.1f}MB".format(final_size / 1000000))
    print("Done.")
    # . $GS -sDEVICE=PDFwrite -q -dNOPAUSE -dBATCH -sOutputFile=$2 -dFirstPage=$3 -dLastPage=$3 $1
    pass

# compress('./Documentos Escaneados.pdf', './t1.pdf', power=4)

# Logic
# Verify email
list_message = verify_email()

# Loop in list of message
for msg in list_message:
    print(f" processar {msg.subject}")
    # Msg without attach
    if(len(msg.attachs) == 0):
        msg.subject = 'ERRO: Não foi enviado o anexo'
        send_email(msg)
        continue

    # Each attach per message
    for attach in msg.attachs:

        filepath = f'./{attach}'
        size = os.stat(filepath).st_size

        if(size > 3000000):

            attach_process = f"c_{attach}"
            filepath_compress = f'./{attach_process}'

            compress(filepath, filepath_compress, power=4)

            size_compress = os.stat(filepath_compress).st_size

            msg_compress = MessageProcessed(msg, attach_process)
            if(size_compress > 3000000):
                msg_compress.subject = f'ERRO: arquivo({attach}) ainda é grande'
                msg_compress = MessageProcessed(msg, "")
                send_email(msg_compress)
            else:
                send_email(msg_compress)
        else:
            msg_compress = MessageProcessed(msg, attach)
            send_email(msg)
