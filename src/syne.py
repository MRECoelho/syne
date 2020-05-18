""" app """
import configparser
import argparse
import os
import sys

class Syne():
    def __init__(self):
        self.config_parser = configparser.ConfigParser()
        self.settings = dict()
        self.settings.update(self._read_default_settings(self.config_parser))
       
        self.arg_parser = argparse.ArgumentParser(description="Note making facilitator app.")
        self.arguments = argparse.Namespace()

        self.path, self.filename, self.extension = '', '', ''

    def _read_default_settings(self, config_parser, _file='settings.ini', _type='DEFAULT'):
        ''' Helper function that reads default settings from settings.ini. The ini file shoudl be
            placed in the same location as the Syne app. If no ini file is specified, the program
            provides defaults of its own.

            TODO:
            Specify args
            & hardcoded defaults

        '''
        settings = dict()
        config_parser.read(_file)
        default_config = config_parser[_type]

        settings['default_settings_file'] = _file
        settings['config_type'] = _type
        settings['pwd'] = default_config.get('pwd', ".") # cannot be changed throughout program
        settings['default_path']  = default_config.get('path', 'General')  
        settings['default_extension'] = default_config.get('extension', '.txt')
        settings['default_editor'] = default_config.get('editor', 'notepad')
        return settings        
    
    def _parse_argmuments(self, arg_parser, namespace):
        # should return parser and the function should be setting up the parser

        ''' Helper function that specifies the standard for parsing arguments and returns the parsed
            results. To see all possible arguments use the -'syne -h' or 'syne --help'.

            Parameters:
                TODO
        
            Returns: 
                Parsed arguments as ArgumentParser object. 
        '''

        arg_parser.add_argument('-d','--default', 
                                action = 'store_true', 
                                help = 'Show default settings')
        arg_parser.add_argument('-l','--list', 
                                action = 'store_true', 
                                help = 'List all notes')
        arg_parser.add_argument('filename',
                                nargs = '?', 
                                metavar = 'file', 
                                type = str, 
                                help = 'Filename with or without extension')
        arg_parser.add_argument('path', 
                                nargs = '?', 
                                metavar = 'path', 
                                type = str, 
                                help = 'Relative path for file')
        arg_parser.add_argument('extension', 
                                nargs = '?',
                                metavar = 'extension', 
                                type = str, 
                                help = 'Extension of the file')
        
        # self.args = self.arg_parser.parse_args()
        arg_parser.parse_args(namespace=namespace)

    def _sanitize(self, to_be_sanitized, allowed="._- ", _path=False):
        '''Return a sanitized String to prevent placing notes outside of Notes folder,
        invalid filenames and invalid extensions by removing certain characters.


        Parameters:
            to_be_sanitized (str): String which is to be sanitized.
            allowed (str):  Default: "._- ". String that specifies explicitly which other characters
                            are allow. The default can be overrriden by specifying this parameter in 
                            the function call.
            _path (bool):   TODO
        
        Returns:
            result (str): String without invalid characters.
            '''

        # ensure that user won't add notes to root using \ or / at the start of pathname
        if _path:
            while not to_be_sanitized[0].isalnum():
                to_be_sanitized = to_be_sanitized[1:]

        return "".join( c for c in to_be_sanitized if (c.isalnum() or c in allowed))
        # print(to_be_sanitized)

    def _validate(self, arg_type, arg_value, minimal_chars=1):
        ''' Helper function that validates string for further use. Here a string must be of atleast
        1 character by default defined as the minimal_chars parameter. Changing this parameter 
        allows the user to create files without an extension or enforce more descriptive strings by 
        using a larger number. 

        Parameters:
            TODO

        Returns:
            TODO

        '''

        if len(arg_value) < minimal_chars:
            # raise ValueError(f'hi')
            print(f"Please enter a valid {arg_type}, '{arg_value}' is not a valid one.")
            # print(Please enter a valid {arg_type}, {arg_value} is not a valid one.)
            exit()
    
    def _setup_vars(self):
        '''
            TODO
        '''
        
        filename = self.arguments.filename
        if self.arguments.extension:
            extension = self.arguments.extension
            filename = filename[:-1] if filename.endswith('.') else filename # disables '<f>..<e>'
        else:
            (filename, extension) = os.path.splitext(filename)
            extension = extension if extension else self.settings['default_extension']
        path = self.arguments.path if self.arguments.path and not self.arguments.path in '*./-\\' else self.settings['default_path']

        path = self._sanitize(path, "/\\", True)
        filename = self._sanitize(filename)
        extension = self._sanitize(extension, "_- ")
        # using a dict the following can be a lot nicer -> _validate(K: V)
        

        for validation_type, value in {'path': path, 'filename': filename, 'extension': extension}.items():
            self._validate(validation_type, value)
        # self._validate('path', path)
        # self._validate('filename', filename)
        # self._validate('extension', extension)
        return path, filename, extension


    def _create_path(self):
        ''' Helper funtion that creates a new path in in the Notes folder if nessecary. Program
            exits is an error is thrown. E.g. not having the rights could lead to such thing.

            Parameters:
                full_path (str): String of the full path from root.
        ''' 

        self.full_path = os.path.join(os.path.relpath(self.settings['pwd']), self.path)
    
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
            The program will exit if it cannot create the placeholder.
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
        # print(self.settings['default_editor'])
        cmd = f'{self.settings["default_editor"]} {self.full_path_and_filename}'
        try:
            os.system(cmd)
        except:
            print(f"Unexpected error running '{cmd}': {sys.exc_info()[0]}")
            exit()


    def run(self):
        ''' 
        TODO
            
        '''
        self._parse_argmuments(self.arg_parser, self.arguments)

        if self.arguments.default:
            self.show_default_settings()
        elif self.arguments.list:
            self.show_notes()
        elif self.arguments.filename:
            self.path, self.filename, self.extension = self._setup_vars()
            self._create_path()
            self._create_file_placeholder()
            self._run_app()
        else:
            self.arg_parser.print_help()

    def show_notes(self):
        ''' List all stored notes in Notes folder.
        '''
        pwd = self.settings['pwd']
        for root, _, files in os.walk(pwd, topdown=True):
            for name in files:
                display_text = os.path.join(os.path.relpath(root, pwd), name)
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

syn = Syne()
syn.run()