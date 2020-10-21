import configparser
import argparse
import os
import sys

class Syne_Config:
    def __init__(self, config_file='config.ini', config_type='DEFAULT'):
        ''' ... '''
        self.config = self.config_setup(config_file, config_type)
        print(self.config)
        self.argument_parser = self.argument_parser_setup()

    def config_setup(self, config_file, config_type):
        ''' Initialize the self.defaults dictionary by reading the default settings. These default 
            settings can dictate where notes should be stored, what extension to use for the files
            and what editor should be used by reading the settings.ini file that should be place in 
            the same directory as the program. If no settings file is provided hardcoded defaults 
            are used.

            Parameters:
                TODO
            
            Returns:
                Configuration dictionary
        '''
        config = configparser.ConfigParser()
        config.read(config_file)
        config_defaults = config.defaults()
        hardcoded_defaults = {  'pwd':'.', 
                                'path': 'General', 
                                'extension' : '.txt', 
                                'editor': 'notepad'
        }
        for key, val in hardcoded_defaults.items():
            if key not in config_defaults or config_defaults[key] == '':
                config_defaults[key] = val
        return config_defaults

    def argument_parser_setup(self):
        ''' Helper function that setups the argument parser and returns a parser object. The main 
            parser logic is defined here. TODO

            Parameters:
                TODO
        
            Returns: 
                ArgumentParser object. 
        '''

        argument_parser = argparse.ArgumentParser(description="Note making facilitator app.")
        argument_parser.add_argument('-d','--default', 
                                action = 'store_true', 
                                help = 'Show default settings')
        argument_parser.add_argument('-l','--list', 
                                action = 'store_true', 
                                help = 'List all notes')
        argument_parser.add_argument('filename',
                                nargs = '?', 
                                metavar = 'file', 
                                type = str, 
                                help = 'Filename with or without extension')
        argument_parser.add_argument('path', 
                                nargs = '?', 
                                metavar = 'path', 
                                type = str, 
                                help = 'Relative path for file')
        argument_parser.add_argument('extension', 
                                nargs = '?',
                                metavar = 'extension', 
                                type = str, 
                                help = 'Extension of the file')
        return argument_parser
    
    def setup_variables(self, args, config):
        ''' '''

        if not args['extension']:
            (filename, extension) = os.path.splitext(args['filename'])
            if not extension:
                extension = config['extension']
        else:
            filename = args['filename']
            extension = args['extension']
        if extension.startswith('.'):
            extension = extension[1:]
        if not args['path']:
            path = config['path']
        else:
            if 'path_alias' in config:
                path = args['path'][0].replace(config['path_alias'], config['path'], 1) + args['path'][1:]
            else:
                path = args['path']
        return {'path': path, 'filename': filename, 'extension': extension}
    
    def validation(self, args, validation_rules):
        for variable, rules_dict in validation_rules.items():
            if args[variable]:
                rules = ['blacklisted_words', 'blacklisted_chars', 'max_chars', 'min_chars']
                for rule in rules:
                    if rule in rules_dict:
                        if rule == 'blacklisted_words':
                            for word in rules_dict[rule]:
                                if args[variable] == word:
                                    print(f"'{args[variable]}' is invalid as '{variable}'. Exiting now.")
                                    exit()
                        elif rule == 'blacklisted_chars':
                            args[variable] = "".join( c for c in args[variable] if (c not in rules_dict[rule]))
                        elif rule == 'max_chars':
                            args[variable] = args[variable][0: rules_dict[rule]]
                        elif rule == 'min_chars':
                            if len(args[variable]) < rules_dict[rule]:
                                print(f"'{args[variable]}' is too short as '{variable}'. Exiting now.")
                                exit()
        return args
    
    def create_full_path_and_filename(self, config):
        full_path = os.path.join(os.path.relpath(config['pwd']), config['path'])
    
        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path)
            except OSError:
                # just in case the user tries some trickery
                print(f'The path {full_path} is not a valid path. Please enter a valid path.')
                print('Terminating program')
                exit()
            except:
                # Incase of rights and others errors
                print("Unexpected error:", sys.exc_info()[0])
                print('Terminating program')
                exit()
        full_path_and_filename = os.path.join(full_path, f"{config['filename']}.{config['extension']}")

        return {'full_path_and_filename': full_path_and_filename}
    
    def create_file_placeholder(self, config):
        ''' Helper function to create a placeholder file that will eventually be the one the will
            be edited by the user. The purpose of this function is to prevent certain programs
            to ask the user (e.g. via a popup) wether the user wants to create a new file with 
            given name. This annoyance is circumvented by creating a empty file.
            The program will exit if it cannot create the placeholder.
        '''
        
        print(config['full_path_and_filename'])
        try:
            if not os.path.isfile(config['full_path_and_filename']):
                # create a blank file
                os.system(f"type NUL > {config['full_path_and_filename']}")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            exit()
    

    def create_note(self, config):
        ''' TODO:
            a little more stuff here
        '''
        # print(self.settings['default_editor'])
        cmd = f"{config['editor']} {config['full_path_and_filename']}"
        try:
            os.system(cmd)
        except:
            print(f"Unexpected error running '{cmd}': {sys.exc_info()[0]}")
            exit()


    def run(self):
        args = self.argument_parser.parse_args()
        args = vars(args)
        path_filename_extension = self.setup_variables(args, self.config)

        settings = {'path': 
                        {
                            'blacklisted_chars': ' `><',
                            'min_chars': 1
                        },
                    'filename':
                        {
                            'blacklisted_chars': '/\\.`><',
                            'min_chars': 1
                        },
                    'extension':
                        {
                            'blacklisted_words': ['exe', 'msi'],
                            'min_chars': 1
                        }
                    }

        self.validation(path_filename_extension, settings)
        self.config.update(path_filename_extension)
        full_path_and_filename = self.create_full_path_and_filename(self.config)
        self.config.update(full_path_and_filename)
        self.create_file_placeholder(self.config)
        self.create_note(self.config)

    def show_notes(self):
        ''' List all stored notes in Notes folder.
        '''
        pwd = self.config['pwd']
        for root, _, files in os.walk(pwd, topdown=True):
            for name in files:
                display_text = os.path.join(os.path.relpath(root, pwd), name)
                print(display_text)

    def help(self):
        ''' Print help.
        '''
        self.argument_parser.print_help()

    def show_default_settings(self):
        ''' Print default settings and place of ini file
            If none specified, print hardcoded defaults
        '''

        for k, v in self.config:
            print(f'{k:10s}: {v}')

s = Syne_Config()
s.run()