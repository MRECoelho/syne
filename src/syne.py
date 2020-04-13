""" app """
import configparser
import argparse
import os
import sys

# load syne config
config = configparser.ConfigParser()
config.read('settings.ini')
default_config = config['DEFAULT']
pwd = default_config.get('pwd', ".")
default_path = default_config.get('path', 'General')  
default_extension = default_config.get('extension', '.txt')
default_dateformat = default_config.get('dateformat', 'YYYY-MM-DD')
default_editor = default_config.get('editor', 'metapad')

#setup parser
# parsers arg
parser = argparse.ArgumentParser(description="Note making facilitator app.")
group = parser.add_mutually_exclusive_group()
group.add_argument('-l','--list', action='store_true', help='List all the notes')
group.add_argument('filename',nargs='?', metavar='file', type=str, help='Filename with or without extension')
parser.add_argument('path', nargs='?', metavar='path', type=str, help='Relative path for file')
parser.add_argument('extension', nargs='?',metavar='extension', type=str, help='Extension of the file')
# parser flags
# parser.add_argument('-d', action='store_true')
# parser.add_argument('-df', action='store_true')
# parser.add_argument('-dp', action='store_true')
# parser.add_argument('-n', action='store_true')
# parse args

args = parser.parse_args()


# helper fn
def sanitize(string, _map=False):
    allowed = "._- "
    if _map:
        allowed = "/\\"
    # Only allow letters, numbers and '._- ' in string 
    return "".join( x for x in string if (x.isalnum() or x in allowed))

def list_all_notes(pwd): 
    for root, _, files in os.walk(pwd, topdown=True):
        for name in files:
            display_text = os.path.join(os.path.relpath(root,pwd), name)
            print(display_text)

# main fn
if args.list:
    list_all_notes(pwd)

elif args.filename:
    filename = args.filename
    if args.extension:
        extension = args.extension
        filename = filename[:-1] if filename.endswith('.') else filename # disables '<f>..<e>'
    else:
        (filename, extension) = os.path.splitext(filename)
    
    # san & val
    filename = sanitize(filename)
    if len(filename) < 1:
        raise ValueError('Please enter a valid filename')
    
    # san & val
    
    extension = extension if extension else default_extension
    extension = sanitize(extension)
    extension = extension.replace('.','')
    if len(extension) < 1:
        raise ValueError('Please enter a valid extension')
    # is filename valid &  (*filename, extension) = str.split('.')
    # validate extension

    # san & val
    path = args.path if args.path and not args.path in '*./-\\' else default_path
    path = sanitize(path, True)
    while path.startswith('\\') or path.startswith('/'):
        path = path[1:]
        # disable root path stuff
    if len(path) < 1:
        raise ValueError('Please enter a valid path')

    full_path = os.path.join(os.path.relpath(pwd), path)
    
    if not os.path.exists(full_path):
        try:
            # os.path.exists(full_path)
            print('making dirs')
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
            

    full_filename = f'{filename}.{extension}'
    full_path_and_filename = os.path.join(os.path.realpath(pwd),path,full_filename)
    try:
        if not os.path.isfile(full_path_and_filename):
            # create a blank file
            os.system(f'type NUL > {full_path_and_filename}')
    except:
        print("Unexpected error:", sys.exc_info()[0])
        exit()

    cmd = f'metapad {full_path_and_filename}'
    # cmd = f'{editor} {full_path_and_filename}'

    try:
        print(f'Opening {full_path_and_filename}')
        print(f' CMD:::: {cmd}')
        os.system(cmd)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        exit()
else:
    parser.print_help()
