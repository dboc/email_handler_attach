from os import stat
from os.path import path
import logging as log

from manager.filemanager import FileManager
from manager.imapmanager import IMAPManager
from manager.smtpmanager import SMTPManager

from base.message import Message, copy_only_message


class EmailManager:

    def __init__(self, host_imap, host_smtp, gc_bin,
                 user, password, attachs_path):

        if('@' in user):
            self.user = user.split('@')[0]
        else:
            raise Exception('User invalid')

        self.__FileManager__ = FileManager(gc_bin)
        self.__IMAPManager__ = IMAPManager(host_imap,
                                           user,
                                           password,
                                           attachs_path)
        self.__SMTPManager__ = SMTPManager(host_smtp,
                                           user,
                                           password)
        self.__from_addr__ = self.user
        self.__attachs_path__ = attachs_path

    def redirect_attached_msg(self, to_addr,
                              from_addr=None,
                              folder='',
                              search_str='X-GM-RAW in:PROCESSAR',
                              size_limit=3):
        # simplify
        imap_mngr = self.__IMAPManager__
        smtp_mngr = self.__SMTPManager__
        file_mngr = self.__FileManager__
        atch_path = self.__attachs_path__

        if(from_addr is None):
            from_addr = self.__from_addr__

        # Login Imap
        imap_mngr.login()
        # Search message
        list_message = imap_mngr.search_message(search_str=search_str)
        # Loop in list of message
        for msg in list_message:

            log.info(f' Processing {msg.subject}')

            # Msg without attach
            if(len(msg.attachs) == 0):
                msg.subject = f'[ERRO: sem anexo]{msg.subject}'
                smtp_mngr.send_email(msg, from_addr)
                continue

            # Each attach per message
            for atch_name in msg.attachs:
                # Get attach path
                atch_path = msg.get_attach_path(atch_name)
                extension = atch_name.split('.')[-1].lower()
                size = stat(atch_path).st_size

                if(size < 3000000):
                    msg_child = copy_only_message(msg)
                    msg_child.attachs.append(atch_name)
                    smtp_mngr.send_email(msg_child, from_addr)
                else:
                    # switch case with if
                    if(extension == 'pdf'):
                        # compress file
                        fl_compressed = f'c_{atch_name}'
                        file_mngr.compress(atch_path,
                                           fl_compressed,
                                           power=4)
                        msg_child = copy_only_message(msg)
                        msg_child.attachs.append(fl_compressed)
                        # msg_child.attachs.append(fl_compressed)
                        sz_compress = stat(msg_child.get_attach_path()).st_size

                        if(sz_compress > 3000000):
                            # Lets split into n Message
                            msg_child = Message()
                            msg_child.subject = f'ERRO: arquivo({atch_name})' \
                                                'ainda é grande'
                            smtp_mngr.send_email(msg_child, from_addr)
                        else:
                            smtp_mngr.send_email(msg_child, from_addr)
                    elif(extension == 'other'):
                        pass
                    else:
                        msg_err = copy_only_message(msg)
                        msg_err.subject = f'ERRO: arquivo({atch_name})' \
                                          'é grande e não é .pdf'
                        smtp_mngr.send_email(msg_err, from_addr)
