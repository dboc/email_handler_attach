from os import stat

from manager.FileManager import FileManager
from manager.IMAPManager import IMAPManager
from manager.SMTPManager import SMTPManager

from base import Message, constant


class EmailHandler:

    def __init__(self,
                 host_imap,
                 host_smtp,
                 user,
                 password,
                 path):

        self.__FileManager = FileManager()
        self.__IMAPManager = IMAPManager(
            host_imap,
            user,
            password,
            path
        )
        self.__SMTPManager = SMTPManager(
            host_smtp,
            user,
            password
        )

    def redirect_attached_msg(self, folder='',
                              search_str='X-GM-RAW in:PROCESSAR',
                              size_limit=3):
        # Verify email
        res = self.__IMAPManager.login()
        list_message = self.__IMAPManager.search_message(
            search_str=search_str
        )
        # Loop in list of message
        for msg in list_message:
            print(f' processar {msg.subject}')
            # Msg without attach
            if(len(msg.attachs) == 0):
                msg.subject = f'[ERRO: sem anexo]{msg.subject}'
                self.__SMTPManager.send_email(msg)
                continue

            # Each attach per message
            for attach in msg.attachs:

                filepath = msg.get_attach_path(attach)
                extension = attach.split('.')[-1].lower()
                size = stat(filepath).st_size

                if(size > 3000000):
                    # switch case with if
                    if(extension == 'pdf'):
                        attach_compress = f'c_{attach}'
                        control.compress(filepath, attach_compress, power=4)
                        msg_compress = MessageProcessed(msg, attach_compress)
                        sz_compress = stat(msg_compress.get_attach_path()).st_size

                        if(sz_compress > 3000000):
                            # Lets split
                            msg_compress = MessageProcessed(msg, '')
                            msg_compress.subject = f'ERRO: arquivo({attach})' \
                                                'ainda é grande'
                            control.send_email(msg_compress)
                        else:
                            control.send_email(msg_compress)
                    elif(extension == 'other'):
                        pass
                    else:
                        msg_compress = MessageProcessed(msg, '')
                        msg_compress.subject = f'ERRO: arquivo({attach})' \
                                            'é grande e não é .pdf'
                        control.send_email(msg_compress)
                else:
                    msg_compress = MessageProcessed(msg, attach)
                    control.send_email(msg_compress)