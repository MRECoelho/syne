Syne is a command line app that uses a text editor to make notes. Syne stores the notes in the default folder. Configre defaults in syne_defaults in the Syne folder.

Use
Syne <filename> [ <folder> [ <extension> ]]

Filename may or may not be provided with an extension. If filename already provided with extension <extension> will be used as actual extension. E.g. Syne mynote.txt Notes .md will result in the file mynote.txt.md in the folder Notes.

Flags
-fd           add date to filename (default: prepend)
-fda          add date to filename prepend
-fdp          add date to filename append
-d            add date to note
-de           add extended date to note
-df <Format>  set date format (default YYYY/MM/DD)
-md           add date to folder (default: prepend)
-mda          add date to folder append
-mdp          add date to folder prepend
-n            create new file, if <filename> exist, append date
-sa           strictly add file to folder, do not create a new folder nor a new file.
