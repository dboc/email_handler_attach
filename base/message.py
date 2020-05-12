import os
import copy


class Message:

    def __init__(self, uid='',
                 subject='', rec_addr='',
                 body='', date='',
                 attachs=None, folder='',
                 to_addr='', from_addr=''):
        self.__subject = subject
        self.rec_addr = rec_addr
        self.body = body
        self.date = date
        self.folder = folder
        self.uid = uid
        self.to_addr = to_addr
        self.from_addr = from_addr
        if(attachs is None):
            self.attachs = []
        else:
            self.attachs = attachs

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
