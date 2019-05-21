from os import listdir, rename
from os.path import isfile, join
import subprocess
from config import files_path


# return name of file to be kept after conversion.
# we are just changing the extension. azw3 here.
def get_final_filename(f):
    f = f.split(".")
    filename = ".".join(f[0:-1])
    filename = filename.split("/")[-1]
    processed_file_name = filename + ".mobi"
    return processed_file_name


# return file extension. pdf or epub or mobi
def get_file_extension(f):
    return f.split(".")[-1]


def convert_epub(mypath, files=None):
    # list of extensions that needs to be ignored.
    ignored_extensions = ["pdf"]

    # path where converted files are stored
    mypath_converted = f"{files_path}ebooks/kindle/"

    # path where processed files will be moved to, clearing the downloaded folder
    mypath_processed = f"{files_path}ebooks/processed/"

    raw_files = files
    converted_files = [
        f for f in listdir(mypath_converted) if isfile(join(mypath_converted, f))
    ]

    just_converted = []
    for f in raw_files:
        final_file_name = get_final_filename(f)
        extension = get_file_extension(f)
        if (
            final_file_name not in converted_files
            and extension not in ignored_extensions
        ):
            print("Converting : " + f)
            final_file = mypath_converted + final_file_name
            try:
                subprocess.call(["ebook-convert", mypath + f, final_file])
                s = rename(mypath + f, mypath_processed + f.split("/")[-1])

                just_converted.append(final_file)
                print(s)
            except Exception as e:
                just_converted.append(final_file)
                print(e)
        else:
            final_file = mypath_converted + final_file_name
            just_converted.append(final_file)
            print("Already exists : " + final_file_name)

    return just_converted
