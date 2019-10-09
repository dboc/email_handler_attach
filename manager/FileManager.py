import subprocess
from os.path import path


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

        print('Compress PDF...')

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
        print('Compression by {0:.0%}.'.format(ratio))
        print('Final file size is {0:.1f}MB'.format(final_size / 1000000))
        print('Done.')

    def split_attach(self, input_file_path, output_file_name):
        """Function to split PDF via Ghostscript command line interface"""

        # Check if valid path
        if not path.isfile(input_file_path):
            raise Exception('Error: invalid path for input PDF file')

        # Check if file is a PDF by extension
        # file_name = input_file_name.split('.')[0:-1]
        file_ext = input_file_path.split('.')[-1].lower()
        if file_ext != 'pdf':
            raise Exception('Error: input file is not a PDF')

        print('Split PDF...')
        output_file_path = path.join(path.dirname(input_file_path),
                                     output_file_name)
        subprocess.call([self.__gc_bin__, '-sDEVICE=pdfwrite',
                         '-dNOPAUSE', '-dQUIET', '-dBATCH',
                         f'-sOutputFile={output_file_path}',
                         input_file_path]
                        )
        # listdir()
        print('Splitted')
