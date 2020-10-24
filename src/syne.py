import subprocess
import configparser
import argparse
import os
import sys

class Syne:
    def __init__(self, config_file='config.ini', config_type='DEFAULT'):
        ''' During initialization of the class the config from the ini file is read and the argument
            parser is setup. By default is search for 'config.ini' in the app main folder, but this 
            can be an arbitrary location. The class can be initialized with different config_types 
            in order to make the app more flexible.

            Parameters:
                config_file: string
                    Name of config file. See the readme on how to configure such file. By default it
                    is set to 'config.ini'.
                config_type: string 
                    Config file section that needs to be read. By default it is set to 'DEFAULT'
        '''
        self.config = self.config_setup(config_file, config_type)
        self.argument_parser = self.argument_parser_setup()

    def config_setup(self, config_file, config_type):
        ''' Initialize the self.defaults dictionary by reading the default settings. These default 
            settings can dictate where notes should be stored, what extension to use for the files
            and what editor should be used by reading the settings.ini file that should be place in 
            the same directory as the program. If no config_file is provided hardcoded defaults 
            are used.

            Parameters:
                config_file: string
                     Name of config file. See the readme on how to configure such file.
                config_type: string
                     Config file section that needs to be read.

            Returns:
                config_defaults: dict
                    Configuration dictionary containing basic configuration settings like the Notes
                    folder working directory (pwd), the default path for notes (path), the default 
                    extension of the note (extension) and the default text editor (editor).
        '''

        config = configparser.ConfigParser()
        config.read(config_file)
        config_defaults = config.defaults()
        if not config_defaults['editor']:
            editor = os.getenv('EDITOR')

            if editor:
                config_defaults['editor'] = editor
            else:
                print('WARNING: No default editor is specified, please specify one in the ini file')
                exit()
        if not config_defaults['extension']:
            print('WARNING: No default extension is specified, please specify one in the ini file')
            exit()
        return config_defaults

    def argument_parser_setup(self):
        ''' Function that setups the argument parser and returns a parser object. The main 
            parser logic is defined here using the parsearg library. If more options are needed
            this is the place to add them.

            Returns:
                argument_parser: ArgumentParser object
                    This object contains the setup for the parser. 
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
        ''' This app heavily revolves around three major variables, the placement of the note 
            (should it be placed in the default folder? Somehwere down a hierachy?) the filename of
            the note and the extenion of the note. Since some flexibility (short hand solution) 
            is implemented in the usage of the command line interface some additional steps are 
            needed to read the arguments properly.

            Parameters:
                args: dict
                    ...
                config: dict
                    ...
            
            Returns:
                dict
                    {'path': path, 'filename': filename, 'extension': extension}

        '''

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
        ''' This function ensures that the strings for path, filename and extension are valid given
            certain validation rules. This function provides some protection against unintended 
            command that could otherwise be a potential problem. This function is not fool proof
            and is only intended to help the user in case of mistakes/typo's.

            Parameters:
                args: dict
                    ...
                validation_rules: dict
                    ...
        '''

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
        ''' Helper function that checks if the given path where the note has to be stored already
            exists. If not, the destination is created. In case an invalid path is given, the app
            will terminate. If succesful the function returns the full path name and filename for 
            further use.

            Parameters:
                config: dict
                    ...
            
            Returns:
                dict
                    ...
        '''

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
        
        try:
            if not os.path.isfile(config['full_path_and_filename']):
                # create a blank file
                os.system(f"type NUL > {config['full_path_and_filename']}")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            exit()
    

    def create_note(self, config):
        ''' TODO: needs to be rewritten
        '''
        cmd = f"{config['editor']} {config['full_path_and_filename']}"
        try:
            subprocess.run(cmd)
            print(f"Created/Edited note in {config['pwd']}/{config['path']} with filename \
{config['filename']}.{config['extension']}")
        except:
            print(f"Unexpected error running '{cmd}'")
            exit()


    def run(self):
        args = self.argument_parser.parse_args()
        if args.default:
            self.show_default_settings()
        elif args.list:
            self.list_notes(self.config)
        else:    
            args = vars(args)
            path_filename_extension = self.setup_variables(args, self.config)
            validation_rules = {'path': 
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

            path_filename_extension = self.validation(path_filename_extension, validation_rules)
            self.config.update(path_filename_extension)
            full_path_and_filename = self.create_full_path_and_filename(self.config)
            self.config.update(full_path_and_filename)
            self.create_file_placeholder(self.config)
            self.create_note(self.config)

    def list_notes(self, config):
        ''' Print all stored notes in Notes (as specified in the ini file) folder.'''

        pwd = config['pwd']
        for root, _, files in os.walk(pwd, topdown=True):
            for name in files:
                display_text = os.path.join(os.path.relpath(root, pwd), name)
                print(display_text)

    def show_default_settings(self):
        ''' Print config from ini file. '''

        for k, v in self.config.items():
            print(f'{k:10s}: {v}')

if __name__ == "__main__":
    s = Syne()
    s.run()