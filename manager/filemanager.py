import subprocess
from os import path, stat, scandir
import logging as log


class FileManager(object):

    def __init__(self, gc_bin):
        self.__gc_bin__ = gc_bin

    def compress(self, input_file_path, output_file_name, power=0):
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
        if not path.isfile(input_file_path):
            raise Exception('Error: invalid path for input PDF file')

        # Check if file is a PDF by extension
        if input_file_path.split('.')[-1].lower() != 'pdf':
            raise Exception('Error: input file is not a PDF')

        log.info('Compress PDF...')

        output_file_path = path.join(path.dirname(input_file_path),
                                     output_file_name)

        initial_size = path.getsize(input_file_path)
        subprocess.call([self.__gc_bin__, '-sDEVICE=pdfwrite',
                         '-dCompatibilityLevel=1.4',
                         f'-dPDFSETTINGS={quality[power]}',
                         '-dNOPAUSE', '-dQUIET', '-dBATCH',
                         f'-sOutputFile={output_file_path}',
                         input_file_path]
                        )
        final_size = path.getsize(output_file_path)
        ratio = 1 - (final_size / initial_size)
        log.info('Compression by {0:.0%}.'.format(ratio))
        log.info('Final file size is {0:.1f}MB'.format(final_size / 1000000))
        log.info('Done.')

    def split_attach(self, input_file_path, output_file_name):
        """Function to split PDF via Ghostscript command line interface"""
        list_files_name = []
        # Check if valid path
        if not path.isfile(input_file_path):
            raise Exception('Error: invalid path for input PDF file')

        # Check if file is a PDF by extension
        # file_name = input_file_name.split('.')[0:-1]
        file_ext = input_file_path.split('.')[-1].lower()
        if file_ext != 'pdf':
            raise Exception('Error: input file is not a PDF')

        log.info('Split PDF...')
        output_file_path = path.join(path.dirname(input_file_path),
                                     f'%d{output_file_name}')
        subprocess.call([self.__gc_bin__, '-sDEVICE=pdfwrite',
                         '-dNOPAUSE', '-dQUIET', '-dBATCH',
                         f'-sOutputFile={output_file_path}',
                         input_file_path]
                        )
        with scandir(path.dirname(input_file_path)) as it:
            for entry in it:
                if(entry.is_file() and output_file_name in entry.name):
                    list_files_name.append(entry.name)

        log.info('Splitted')
        return list_files_name

    def verify_size(self, file_path):
        return stat(file_path).st_size
