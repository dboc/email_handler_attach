import smtplib
import imaplib
import email
import time
import datetime
import os
import base64
import subprocess
import sys
from shutil import copyfile

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# region GLOBAL Variables

GC_BIN = os.getenv('GC_BIN', r'C:\Program Files\gs\gs9.27\bin\gswin64c.exe')
PATH = os.getenv('PATH', os.path.dirname(os.path.realpath(__file__)))
HOST_SMTP = os.getenv('HOST_SMTP', 'smtp.gmail.com')
HOST_IMAP = os.getenv('HOST_IMAP', 'imap.gmail.com')
USER = os.getenv('USER', '')
PSS = os.getenv('PSS', '')
FROM_ADDR = os.getenv('FROM_ADDR', '')
TO_ADDR = os.getenv('TO_ADDR', '')

# endregion GLOBAL Variables

# region Class definition


class Message:
    from_addr = FROM_ADDR
    to_addr = TO_ADDR

    def __init__(self):
        self._subject = ''
        self.rec_addr = ''
        self.body = ''
        self.date = ''
        self.attachs = []
        self.folder = ''

    @property
    def subject(self):
        return f'[{self.to_addr}] {self._subject}'

    @subject.setter
    def subject(self, value):
        self._subject = value

    def get_attach_path(self, attach):
        if(attach in self.attachs):
            return os.path.join(PATH, self.folder, attach)
        else:
            raise Exception('Attach not exist')


class MessageProcessed:
    from_addr = FROM_ADDR
    to_addr = TO_ADDR

    def __init__(self, msgParent, attach):
        self._subject = msgParent._subject
        self.rec_addr = msgParent.rec_addr
        self.body = msgParent.body
        self.date = msgParent.date
        self.attachs = attach
        self.folder = msgParent.folder
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

    def get_attach_path(self):
            return os.path.join(PATH, self.folder, self.attachs)
# endregion Class definition


# region Function definition
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
        part.add_header('Content-Disposition',
                        f'attachment; filename= {message.attachs}')
        msg_mime.attach(part)
        attachment.close()
    elif(len(message.attachs) != 0):
        for attach in message.attachs:
            filepath = f'./{attach}'
            attachment = open(filepath, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            f'attachment; filename= {attach}')
            msg_mime.attach(part)
            attachment.close()
    smtp = smtplib.SMTP_SSL(HOST_SMTP)
    smtp.login(USER, PSS)
    text = msg_mime.as_string()
    smtp.sendmail(message.from_addr, message.to_addr, text)
    print(f'msg sent {message.subject}')
    smtp.quit()


def verify_email():

    list_message = []

    imap = imaplib.IMAP4_SSL(HOST_IMAP)
    print('Imap Login...')
    res, data = imap.login(USER, PSS)
    print(f'Imap Login {res}')
    imap.select()
    print('Imap Search...')
    res, data = imap.search(None, 'X-GM-RAW in:PROCESSAR')
    mail_ids = data[0]
    print(f'Imap Search {res}, total={len(mail_ids)}')
    id_list = mail_ids.split()

    for num in id_list:
        print(f'Fetching msg={num}...')
        res, data = imap.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        # converts byte literal to string removing b''
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        r_message = Message()
        r_message.rec_addr = email_message.get('From')
        r_message.subject = email_message.get('Subject')
        r_message.date = email_message.get('Date')

        # Creating folder by from and date
        epoch = time.mktime(email.utils.parsedate(r_message.date))
        folder_name = f'{int(epoch)}'

        print(f'Downloading attachs from MSG {r_message.subject}')
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

            file_name = part.get_filename()
            if bool(file_name):
                # mkdir
                if not os.path.isdir(os.path.join(PATH, folder_name)):
                    os.mkdir(os.path.join(PATH, folder_name))
                r_message.folder = folder_name

                r_message.attachs.append(file_name)
                filePath = r_message.get_attach_path(file_name)
                # if not os.path.isfile(filePath):
                fp = open(filePath, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
                print(f'Downloaded "{file_name}"')
        imap.store(num, '-X-GM-LABELS', 'PROCESSAR')
        imap.store(num, '+X-GM-LABELS', 'PROCESSADO')
        list_message.append(r_message)
        print(f'msg={num} [{r_message.subject}] , DONE')
    imap.close()
    imap.logout()
    print('Imap Logout')
    return list_message


def compress(input_file_path, output_file_name, power=0):
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
        raise Exception('Error: invalid path for input PDF file')

    # Check if file is a PDF by extension
    if input_file_path.split('.')[-1].lower() != 'pdf':
        raise Exception('Error: input file is not a PDF')

    print('Compress PDF...')

    output_file_path = os.path.join(os.path.dirname(input_file_path),
                                    output_file_name)

    initial_size = os.path.getsize(input_file_path)
    subprocess.call([GC_BIN, '-sDEVICE=pdfwrite',
                     '-dCompatibilityLevel=1.4',
                     f'-dPDFSETTINGS={quality[power]}',
                     '-dNOPAUSE', '-dQUIET', '-dBATCH',
                     f'-sOutputFile={output_file_path}',
                     input_file_path]
                    )
    final_size = os.path.getsize(output_file_path)
    ratio = 1 - (final_size / initial_size)
    print('Compression by {0:.0%}.'.format(ratio))
    print('Final file size is {0:.1f}MB'.format(final_size / 1000000))
    print('Done.')


def split_attach(input_file_path, output_file_name):
    """Function to split PDF via Ghostscript command line interface"""

    # Check if valid path
    if not os.path.isfile(input_file_path):
        raise Exception('Error: invalid path for input PDF file')

    # Check if file is a PDF by extension
    # file_name = input_file_name.split('.')[0:-1]
    file_ext = input_file_path.split('.')[-1].lower()
    if file_ext != 'pdf':
        raise Exception('Error: input file is not a PDF')

    print('Split PDF...')
    output_file_path = os.path.join(os.path.dirname(input_file_path),
                                    output_file_name)
    subprocess.call([GC_BIN, '-sDEVICE=pdfwrite',
                     '-dNOPAUSE', '-dQUIET', '-dBATCH',
                     f'-sOutputFile={output_file_path}',
                     input_file_path]
                    )
    os.listdir()
    print('Splitted')
    pass
# endregion


# region Run
def run():

    # Verify email
    list_message = verify_email()

    # Loop in list of message
    for msg in list_message:
        print(f' processar {msg.subject}')
        # Msg without attach
        if(len(msg.attachs) == 0):
            msg.subject = f'[ERRO: sem anexo]{msg.subject}'
            send_email(msg)
            continue

        # Each attach per message
        for attach in msg.attachs:

            filepath = msg.get_attach_path(attach)
            extension = attach.split('.')[-1].lower()
            size = os.stat(filepath).st_size

            if(size > 3000000):
                # switch case with if
                if(extension == 'pdf'):
                    attach_compress = f'c_{attach}'
                    compress(filepath, attach_compress, power=4)
                    msg_compress = MessageProcessed(msg, attach_compress)
                    size_compress = os.stat(msg_compress.get_attach_path()).st_size

                    if(size_compress > 3000000):
                        # Lets split
                        msg_compress = MessageProcessed(msg, '')
                        msg_compress.subject = f'ERRO: arquivo({attach}) ainda é grande'
                        send_email(msg_compress)
                    else:
                        send_email(msg_compress)
                elif(extension == 'other'):
                    pass
                else:
                    msg_compress = MessageProcessed(msg, '')
                    msg_compress.subject = f'ERRO: arquivo({attach}) é grande e não é .pdf'
                    send_email(msg_compress)
            else:
                msg_compress = MessageProcessed(msg, attach)
                send_email(msg_compress)

# endregion Run

while True:
    time_now = datetime.datetime.now()
    if(time_now.hour > 18):
        print(f'Next execution:{time_now + datetime.timedelta(hours=12)}')
        time.sleep(3600*12)
    else:
        try:
            run()
        except Exception as e:
            print(e)
        finally:
            print(f'Next execution:{time_now + datetime.timedelta(hours=1)}')
            time.sleep(3600)
