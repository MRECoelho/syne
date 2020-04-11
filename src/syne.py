""" app """
# get command line args
# flags dict
# check folder exists
# check file exists
# create file? Or just ship to Atom.
# docs, help doc thingies

# flow:
# check flags
    # create config obj
# get args
    # extend config obj
# run()

# fpe
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

#setup parser
# parsers arg
parser = argparse.ArgumentParser(description="Note making facilitator app")
group = parser.add_mutually_exclusive_group()
group.add_argument('-l','--list', action='store_true')
group.add_argument('filename',nargs='?', metavar='file', type=str, help='Filename with or without extension.')
parser.add_argument('path', nargs='?', metavar='path', type=str, help='Relative path for file.')
parser.add_argument('extension', nargs='?',metavar='extension', type=str, help='Extension of the file.')
# parser flags
parser.add_argument('-d', action='store_true')
parser.add_argument('-df', action='store_true')
parser.add_argument('-dp', action='store_true')
parser.add_argument('-n', action='store_true')
# parse args


args = parser.parse_args()



# helper fn
def sanitize(string, _map=False):
    allowed = "._- "
    if _map:
        allowed = "/\\"
    # Only allow letters, numbers and '._- ' in string 
    return "".join( x for x in string if (x.isalnum() or x in allowed))

if args.list:
    for root, dirs, files in os.walk(pwd, topdown=True):
        for name in files:
            display_text = os.path.join(os.path.relpath(root,pwd), name)
            if display_text == '.\\desktop.ini':
                continue
            else:   
                print(display_text)
#    for name in dirs:
#       print(os.path.join(root, name))

elif args.filename:
    extension = args.extension
    filename = args.filename
    filename = filename[:-1] if filename.endswith('.') else filename # disables '<f>..<e>'

    if not extension:
        (filename, extension) = os.path.splitext(filename)
        extension = extension if extension and len(extension)>1 else default_extension
    extension = sanitize(extension)
    extension = extension if extension.startswith('.') else f'.{extension}'
    # is filename valid &  (*filename, extension) = str.split('.')
    # validate extension

    # valid path stuff
    path = args.path if args.path and not args.path in '*./-' else default_path
    path = sanitize(path, True)
    while path.startswith('\\') or path.startswith('/'):
        path = path[1:]
    print(f'path = {path},  pwd = {pwd}')

    # # flags 
    # # update filename if nesseceary
    # add_date_in_note = args.d
    # add_date_to_filename = args.df
    # add_date_to_path = args.dp
    # create_new_file = args.n

    full_path = os.path.join(os.path.relpath(pwd), path)
    print(f'full_path: {full_path}')
    # exit()
    # try:
    #     os.path.exists(full_path)
    #     print(os.path.exists(full_path))
    # finally:
    if not os.path.exists(full_path):
        try:
            # os.path.exists(full_path)
            print('making dirs')
            os.makedirs(full_path)
        except OSError:
            print(f'The path {full_path} is not a valid path. Please enter a valid path.')
            print('Terminating program')
            exit()
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print('Terminating program')
            exit()
            

    full_filename = f'{filename}{extension}'
    full_path_and_filename = os.path.join(os.path.realpath(pwd),path,full_filename)
    try:
        if not os.path.isfile(full_path_and_filename):
            os.system(f'type NUL > {full_path_and_filename}')
    except:
        print("Unexpected error:", sys.exc_info()[0])
        exit()

    cmd = f'metapad {full_path_and_filename}'

    try:
        print(f'Opening {full_path_and_filename}')
        print(f' CMD:::: {cmd}')
        os.system(cmd)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        exit()
else:
    print('Please enter a valid filename.')
    # LOOP
# Todo
# Config class (load defaults)
# Parser class (update config)
# Prep
# Run
