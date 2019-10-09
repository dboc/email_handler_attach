import imaplib
import time
from os.path import path
from os import mkdir
import logging as log

from email import utils
from email import message_from_string
from email import header

from base.message import Message


class IMAPManager(object):

    def __init__(self, host, user, password, path):
        self.__host = host
        self.__user = user
        self.__password = password
        self.__path = path
        self.__imapsrv = None

    def login(self):
        self.__imapsrv = imaplib.IMAP4_SSL(self.__host)
        res_ok, data = self.__imapsrv.login(self.__user, self.__password)
        if not res_ok:
            raise Exception(data)

    def logout(self):
        res_ok, data = self.__imapsrv.close()
        if not res_ok:
            raise Exception(data)
        res_ok, data = self.__imapsrv.logout()
        if not res_ok:
            raise Exception(data)

    def search_message(self, folder='', search_str=''):
        # simplify
        imapsrv = self.__imapsrv
        # search in Folder 'INBOX'
        imapsrv.select()
        res_ok, data = imapsrv.search(None, search_str)
        if not res_ok:
            raise Exception(data)
        else:
            mail_ids = data[0]
            id_list = mail_ids.split()
        # Loop id_list
        list_message = []
        for num_id in id_list:

            log.info(f'Fetching msg={num_id}...')
            res_ok, data = imapsrv.fetch(num_id, '(RFC822)')
            if not res_ok:
                raise Exception(data)
            raw_email = data[0][1]
            # create msg
            received_msg = self.__create_msg__(raw_email, num_id)
            # append msg
            list_message.append(received_msg)

            log.info(f'msg={num_id} [{received_msg.subject}] , DONE')

        return list_message

    def mark_message(self, message):
        # simplify
        imapsrv = self.__imapsrv
        res_ok, data = imapsrv.store(message.id,
                                     '-X-GM-LABELS', 'PROCESSAR')
        if not res_ok:
            raise Exception(data)
        res_ok, data = imapsrv.store(message.id,
                                     '+X-GM-LABELS', 'PROCESSADO')
        if not res_ok:
            raise Exception(data)

    def __create_msg__(self, mime_data, uid):
        # create object
        message = Message(uid=uid)

        # converts byte literal to string removing b''
        raw_email_string = mime_data.decode('utf-8')
        imap_msg = message_from_string(raw_email_string)

        # set From addr
        message.rec_addr = imap_msg.get('From')

        # set subject
        tmp_sbj, tmp_charset = header.decode_header(
                                imap_msg.get('Subject'))[0]
        if(tmp_charset is None):
            message.subject = tmp_sbj
        else:
            message.subject = tmp_sbj.decode(tmp_charset)

        # set date
        message.date = imap_msg.get('Date')

        # set folder - folder name is epochdate
        epoch = time.mktime(utils.parsedate(message.date))
        folder_name = f'{int(epoch)}'
        message.folder = folder_name

        # set attachs and body
        # downloading attachments and body
        message = self.__include_attachs__(message, imap_msg)

        return message

    def __include_attachs__(self, message, srv_msg):
        log.info(f'Downloading Body and Attachs from MSG {message.subject}')
        for part in srv_msg.walk():
            # this part comes from the snipped I don't understand yet...
            if part.get_content_type() == 'text/plain':
                message.body = part.get_payload()
                continue
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            if bool(part.get_filename()):
                tmp_fn, tmp_charset = header.decode_header(
                                        part.get_filename())[0]
                if(tmp_charset is None):
                    file_name = tmp_fn
                else:
                    file_name = tmp_fn.decode(tmp_charset)

                # mkdir
                if not path.isdir(path.join(self.__path, message.folder)):
                    mkdir(path.join(self.__path, message.folder))

                filePath = message.get_attach_path(file_name)
                fp = open(filePath, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

                log.info(f'Downloaded "{file_name}"')
                message.attachs.append(file_name)

        return message
