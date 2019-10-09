import datetime
import time
import logging as log

from manager.emailmanager import EmailManager

from os import getenv, path
# region ENV Variables
GC_BIN = getenv('GC_BIN', r'C:\Program Files\gs\gs9.27\bin\gswin64c.exe')
PATH_ATTACHS = getenv('PATH_ATTACHS', path.dirname(path.realpath(__file__)))
HOST_SMTP = getenv('HOST_SMTP', 'smtp.gmail.com')
HOST_IMAP = getenv('HOST_IMAP', 'imap.gmail.com')
USER = getenv('USER', 'hmcamila.caixa@gmail.com')
PSS = getenv('PSS', 'lpljixgslgoaipiz')
FROM_ADDR = getenv('FROM_ADDR', 'hmcamila.caixa@gmail.com')
TO_ADDR = getenv('TO_ADDR', 'daniel.carvalho@prodest.es.gov.br')
SRCH_STRING = getenv('SRCH_STRING', 'X-GM-RAW in:PROCESSAR')
# endregion ENV Variables
log.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=log.INFO)

email_handler = EmailManager(host_smtp=HOST_SMTP,
                             host_imap=HOST_IMAP,
                             user=USER,
                             password=PSS,
                             attachs_path=PATH_ATTACHS,
                             gc_bin=GC_BIN)

while True:
    time_now = datetime.datetime.now()
    if(time_now.hour > 19):
        log.info(f'Next execution:{time_now + datetime.timedelta(hours=12)}')
        time.sleep(3600*12)
    else:
        try:
            email_handler.redirect_attached_msg(TO_ADDR,
                                                FROM_ADDR,
                                                PATH_ATTACHS,
                                                SRCH_STRING)
        except Exception as e:
            log.error(e)
            email_handler.send_error_email(e, TO_ADDR, FROM_ADDR)
        finally:
            log.info('Next execution:' +
                     f'{time_now + datetime.timedelta(hours=1)}')
            time.sleep(3600)
