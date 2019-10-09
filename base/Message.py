import os
import copy


class Message:

    def __init__(self, uid='',
                 subject='', rec_addr='',
                 body='', date='',
                 attachs=[], folder=''):
        self.__subject = subject
        self.rec_addr = rec_addr
        self.body = body
        self.date = date
        self.attachs = attachs
        self.folder = folder
        self.uid = uid

    @property
    def subject(self):
        return f'[{self.rec_addr}] {self.__subject}'

    @subject.setter
    def subject(self, value):
        self.__subject = value

    def get_attach_path(self, attach):
        if(attach in self.attachs):
            return os.path.join(self.folder, attach)
        else:
            raise Exception('Attach not exist')


def copy_only_message(messageIn):
    cp = copy.deepcopy(messageIn)
    cp.attachs = []
    return cp
