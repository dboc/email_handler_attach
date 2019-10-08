
import os


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

# class MessageProcessed(Message):
#     def __init__(self, msgParent, attach):
#         super().__init__(self)
#         self._subject = msgParent._subject
#         self.rec_addr = msgParent.rec_addr
#         self.body = msgParent.body
#         self.date = msgParent.date
#         self.attachs = attach
#         self.folder = msgParent.folder
#         self.partnum = 0
#     @property
#     def subject(self):
#         if(self.partnum >= 0):
#             return f'[{self.rec_addr}] {self._subject} {self.attachs}'
#         else:
#             return f'[{self.rec_addr}] {self._subject} {self.attachs}' \
#                    '[{self.partnum}]'
#     def get_attach_path(self):
#         return os.path.join(PATH_ATTACHS, self.folder, self.attachs)
# # endregion Class definition
