import datetime
import time
from os import stat

import control
from base import Message, MessageProcessed



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
