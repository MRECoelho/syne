""" app """
import configparser
import argparse
import os
import sys

class Syne():
    def __init__(self):
        self.config_parser = configparser.ConfigParser()
        self.arg_parser = argparse.ArgumentParser(description="Note making facilitator app.")

    def _read_default_settings(self):
        ''' Helper function that reads default settings from settings.ini. The ini file shoudl be
            placed in the same location as the Syne app. If no ini file is specified, the program
            provides defaults of its own.

            TODO:
            Specify args
            & hardcoded defaults

        '''

        self.config_parser.read('settings.ini')
        self.default_config = self.config_parser['DEFAULT']
        self.pwd = self.default_config.get('pwd', ".") # cannot be changed throughout program
        self.default_path = self.default_config.get('path', 'General')  
        self.default_extension = self.default_config.get('extension', '.txt')
        # self.default_dateformat = default_config.get('dateformat', 'YYYY-MM-DD')
        self.default_editor = self.default_config.get('editor', 'metapad')
    
    def _parse_argmuments(self):
        ''' Helper function that specifies the standard for parsing arguments and returns the parsed
            results. To see all possible arguments use the -'syne -h' or 'syne --help'.
        
            Returns: Parsed arguments as ArgumentParser object. 
        '''

        self.arg_parser.add_argument('-d','--default', 
                                action = 'store_true', 
                                help = 'Show default settings')
        self.arg_parser.add_argument('-l','--list', 
                                action = 'store_true', 
                                help = 'List all notes')
        self.arg_parser.add_argument('filename',
                                nargs = '?', 
                                metavar = 'file', 
                                type = str, 
                                help = 'Filename with or without extension')
        self.arg_parser.add_argument('path', 
                                nargs = '?', 
                                metavar = 'path', 
                                type = str, 
                                help = 'Relative path for file')
        self.arg_parser.add_argument('extension', 
                                nargs = '?',
                                metavar = 'extension', 
                                type = str, 
                                help = 'Extension of the file')
        # self.args = self.arg_parser.parse_args()
        self.args = self.arg_parser.parse_args()

    def _sanitize(self, to_be_sanitized, allowed="._- ", path=False):
        '''Return a sanitized String to prevent placing notes outside of Notes folder,
        invalid filenames and invalid extensions by removing certain characters.


        Parameters:
            to_be_sanitized (str): String which is to be sanitized.
            allowed (str): Default: "._- ". String that specifies explicitly which other characters
                            are allow. The default can be overrriden by specifying this parameter in 
                            the function call.
        
        Returns:
            result (str): String without invalid characters.
        '''

        # ensure that user won't add notes to root using \ or / at the start of pathname
        if path:
            while not to_be_sanitized[0].isalnum():
                to_be_sanitized = to_be_sanitized[1:]
        
        to_be_sanitized = "".join( c for c in to_be_sanitized if (c.isalnum() or c in allowed))

    def _validate(self, arg_type, arg_value):
        ''' Helper function that validates the path, filename and extension.

            TODO:
                Is this really a seperate function? 

        '''

        if len(arg_value) < 1:
            # raise ValueError(f'hi')
            print(f"Please enter a valid {arg_type}, '{arg_value}' is not a valid one.")
            # print(Please enter a valid {arg_type}, {arg_value} is not a valid one.)
            exit()
    
    def _setup_vars(self):
        '''
            missing docs
        '''
        
        self.filename = self.args.filename
        if self.args.extension:
            self.extension = self.args.extension
            self.filename = self.filename[:-1] if self.filename.endswith('.') else self.filename # disables '<f>..<e>'
        else:
            (self.filename, self.extension) = os.path.splitext(self.filename)
            self.extension = self.extension if self.extension else self.default_extension

        self.path = self.args.path if self.args.path and not self.args.path in '*./-\\' else self.default_path
        
        # self.filename= self._sanitize(self.filename)
        # self.extension = self._sanitize(self.extension, "_- ")
        # self.path = self._sanitize(self.path, "/\\", True)
        # setting = namedtuple('setting', 'arg_value', 'validation_chars')

        settings = [['path', self.path],
                    ['filename', self.filename, "_- "],
                    ['extension', self.extension, ["/\\", True]]
        ]

        for arg_type, *remainder in settings:
            # print(f'{arg_type}, {remainder}')
            # print(f'{arg_type}, {remainder[0]}')

            self._sanitize(*remainder)
            self._validate(arg_type, remainder[0])

    def _create_path(self):
        ''' Helper funtion that creates a new path in in the Notes folder if nessecary. Program
            exits is an error is thrown. E.g. not having the rights could lead to such thing.

            Parameters:
                full_path (str): String of the full path from root.
        ''' 

        self.full_path = os.path.join(os.path.relpath(self.pwd), self.path)
    
        if not os.path.exists(self.full_path):
            try:
                os.makedirs(self.full_path)
            except OSError:
                # just in case the user tries some trickery
                print(f'The path {self.full_path} is not a valid path. Please enter a valid path.')
                print('Terminating program')
                exit()
            except:
                # Incase of rights and others errors
                print("Unexpected error:", sys.exc_info()[0])
                print('Terminating program')
                exit()

    def _create_file_placeholder(self):
        ''' Helper function to create a placeholder file that will eventually be the one the will
            be edited by the user. The purpose of this function is to prevent certain programs
            to ask the user (e.g. via a popup) wether the user wants to create a new file with 
            given name. This annoyance is circumvented by creating a empty file.
            The program will exit is if it cannot create the placeholder.
        '''
        self.full_path_and_filename = os.path.join(self.full_path, f'{self.filename}.{self.extension}')

        try:
            if not os.path.isfile(self.full_path_and_filename):
                # create a blank file
                os.system(f'type NUL > {self.full_path_and_filename}')
        except:
            print("Unexpected error:", sys.exc_info()[0])
            exit()

    def _run_app(self):
        ''' TODO:
            a little more stuff here
        '''
        cmd = f'{self.default_editor} {self.full_path_and_filename}'
        try:
            os.system(cmd)
        except:
            print(f"Unexpected error running '{cmd}': {sys.exc_info()[0]}")
            exit()


    def run(self):
        ''' TODO:
                main funtion
        '''
        self._read_default_settings()
        self._parse_argmuments()

        if self.args.default:
            self.show_default_settings()
        elif self.args.list:
            self.show_notes()
        elif self.args.filename:
            self._setup_vars()
            self._create_path()
            self._create_file_placeholder()
            self._run_app()
        else:
            self.arg_parser.print_help()
        
        # read def
        # parse args
        # setup
        # sanitze
        # validate
        # create path
        # place placeholder
        # open editor with note

    def show_notes(self):
        ''' List all stored notes in Notes folder.
        '''
        for root, _, files in os.walk(self.pwd, topdown=True):
            for name in files:
                display_text = os.path.join(os.path.relpath(root,self.pwd), name)
                print(display_text)

    def help(self):
        ''' Print help.
        '''
        self.arg_parser.print_help()

    def show_default_settings(self):
        ''' Print default settings and place of ini file
            If none specified, print hardcoded defaults
        '''

        for k, v in self.config_parser._defaults.items():
            print(f'{k:10s}: {v}')
        # for k, v in self.config_parser._defaults:

syn = Syne()
syn.run()

# # load syne config
# config = configparser.ConfigParser()
# config.read('settings.ini')
# default_config = config['DEFAULT']
# pwd = default_config.get('pwd', ".")
# default_path = default_config.get('path', 'General')  
# default_extension = default_config.get('extension', '.txt')
# default_dateformat = default_config.get('dateformat', 'YYYY-MM-DD')
# default_editor = default_config.get('editor', 'metapad')

# #setup parser
# # parsers arg
# parser = argparse.ArgumentParser(description="Note making facilitator app.")
# group = parser.add_mutually_exclusive_group()
# group.add_argument('-l','--list', action='store_true', help='List all the notes')
# group.add_argument('filename',nargs='?', metavar='file', type=str, help='Filename with or without extension')
# parser.add_argument('path', nargs='?', metavar='path', type=str, help='Relative path for file')
# parser.add_argument('extension', nargs='?',metavar='extension', type=str, help='Extension of the file')
# # parser flags
# # parser.add_argument('-d', action='store_true')
# # parser.add_argument('-df', action='store_true')
# # parser.add_argument('-dp', action='store_true')
# # parser.add_argument('-n', action='store_true')
# # parse args

# args = parser.parse_args()


# # helper fn
# def sanitize(string, _map=False):
#     '''
#     Return a sanitized String to prevent placing notes outside of Notes folder,
#     invalid filenames and invalid extensions by removing certain characters.

#     allowed characters: "._- "
#     allowed characters when _map is True: "/\\"

#     Paramaters:
#         string (str): String which is to be sanitized.
#         _map (bool): Optional boolean to indicate whether the string is folder.

#     Returns:
#         result (str): String without invalid characters.
#     '''
#     allowed = "._- "
#     if _map:
#         allowed = "/\\"
#     # Only allow letters, numbers and '._- ' in string 
#     return "".join( x for x in string if (x.isalnum() or x in allowed))

# def list_all_notes(pwd): 
#     '''
#     Prints a list of the current notes in the Notes folder.
    
#     Parameters:
#         pwd (str): Path of the current Notes folder.
#     '''
#     for root, _, files in os.walk(pwd, topdown=True):
#         for name in files:
#             display_text = os.path.join(os.path.relpath(root,pwd), name)
#             print(display_text)

# # main fn
# if args.list:
#     list_all_notes(pwd)

# elif args.filename:
#     filename = args.filename
#     if args.extension:
#         extension = args.extension
#         filename = filename[:-1] if filename.endswith('.') else filename # disables '<f>..<e>'
#     else:
#         (filename, extension) = os.path.splitext(filename)
    
#     # san & val
#     filename = sanitize(filename)
#     if len(filename) < 1:
#         raise ValueError('Please enter a valid filename')
    
#     # san & val
    
#     extension = extension if extension else default_extension
#     extension = sanitize(extension)
#     extension = extension.replace('.','')
#     if len(extension) < 1:
#         raise ValueError('Please enter a valid extension')
#     # is filename valid &  (*filename, extension) = str.split('.')
#     # validate extension

#     # san & val
#     path = args.path if args.path and not args.path in '*./-\\' else default_path
#     path = sanitize(path, True)
#     while path[0] not path.isalnum():
#         path = path[1:]
#         # disable root path stuff
#     if len(path) < 1:
#         raise ValueError('Please enter a valid path')

#     full_path = os.path.join(os.path.relpath(pwd), path)
    
#     if not os.path.exists(full_path):
#         try:
#             # os.path.exists(full_path)
#             print('making dirs')
#             os.makedirs(full_path)
#         except OSError:
#             # just in case the user tries some trickery
#             print(f'The path {full_path} is not a valid path. Please enter a valid path.')
#             print('Terminating program')
#             exit()
#         except:
#             # Incase of rights and others errors
#             print("Unexpected error:", sys.exc_info()[0])
#             print('Terminating program')
#             exit()
            
#     full_path_and_filename = os.path.join(os.path.realpath(pwd),
#                                             path,
#                                             f'{filename}.{extension}')
#     try:
#         if not os.path.isfile(full_path_and_filename):
#             # create a blank file
#             os.system(f'type NUL > {full_path_and_filename}')
#     except:
#         print("Unexpected error:", sys.exc_info()[0])
#         exit()

#     cmd = f'metapad {full_path_and_filename}'
#     # cmd = f'{editor} {full_path_and_filename}'

#     try:
#         print(f'Opening {full_path_and_filename}')
#         print(f' CMD:::: {cmd}')
#         os.system(cmd)
#     except:
#         print("Unexpected error:", sys.exc_info()[0])
#         exit()
# else:
#     parser.print_help()
