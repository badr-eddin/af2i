import io
import shutil
import tempfile
from datetime import datetime
import math
import mimetypes
import sys
import argparse
from colorama import Fore, Cursor
from binaryornot import check
import os.path
from PIL import Image
import numpy as np
import cv2
import re

# SETUP
__name__ = "af2i"
__file__ = "af2i"
__version__ = "0.0.1"
__author__ = "badr-eddin"


class Tools:
    def __init__(self):
        self.__spacer = 10
        self.__colors = ["b", "g", "r"]
        self.__output_colors = {
            "e": Fore.RED,
            "w": Fore.YELLOW,
            "i": Fore.BLUE,
            "s": Fore.GREEN
        }

    def inform(self, *args, _t="i"):
        _ = self.__output_colors
        tm = datetime.now().strftime("%H:%M:%S")
        print(f"{self.__output_colors.get(_t)}[{tm}] {' '.join((*args,))}", Fore.RESET)

    def prompt(self, _i):
        tm = datetime.now().strftime("%H:%M:%S")
        return input(Fore.LIGHTBLUE_EX + f"[{tm}] {_i.capitalize()} {' ' * (self.__spacer - len(_i))} : " + Fore.RESET)

    def get_image_color(self, arg):
        _color = arg.color or self.prompt("[r] red | [g] green | [b] blue", ).lower()
        if _color in self.__colors:
            return self.__colors.index(_color), _color

        self.inform("color not defined !", _t="e")
        return self.get_image_color(arg)


# Converters
class AsciiConverter(Tools):
    def initialize(self, arg):
        # prompt user to choose between (read, write)
        mode = ("w" if arg.write else "r" if arg.read else None) or self.prompt("[r] read | [w] write").lower()

        # read from an image
        if mode == "r":
            image_file = arg.filename or self.prompt("image file")
            image_file = image_file if os.path.splitext(image_file)[1] else image_file + ".png"
            if not os.path.exists(image_file):
                self.inform(f"file '{image_file}' not exists !", _t="e")
                exit(404)

            if "image" not in mimetypes.guess_type(image_file)[0]:
                self.inform("It seems that this file is not Image", _t="e")
                exit(-1)

            # 1. read image
            pil_img = Image.open(image_file)
            temp_file = os.path.join(tempfile.mkdtemp(), os.path.splitext(os.path.basename(image_file))[0] + ".png")
            pil_img.save(temp_file)

            image = cv2.imread(temp_file)

            image_color = self.get_image_color(arg)
            ords = image.reshape(-1, 3)[:, image_color[0]]

            data = ''.join([chr(int(i)) for i in ords])

            if not data.isascii():
                self.inform("cannot process non ascii letters !", _t="e")
                exit(-1)

            print_or_save = ("p" if arg.print else "s" if arg.save else 0) or self.prompt(
                "[p] print | [s] save").lower()

            fname = "-"
            if arg.write or arg.save:
                fname = arg.outfile or self.prompt("file")

            # print summary
            self.inform("--------------------------------------")
            self.inform("source file  :", image_file)
            self.inform("mode         :", "write" if mode == "w" else "read")
            self.inform("output method:", "print" if print_or_save == "p" else "save")
            self.inform("output file  :", fname)
            self.inform("main color   :", image_color[1])
            self.inform("--------------------------------------")

            self.inform("data retrieved successfully .", _t='s')

            ln = "*"
            if "@" in print_or_save:
                print_or_save, ln = print_or_save.split("@")

            ln = int(ln) if ln.isdigit() else "*"

            if print_or_save == "p":
                print((data[:ln] if ln != "*" else data) if data else
                      "empty ! probably you have selected wrong color .")

            elif print_or_save == "s":
                write_mode, first_line = ("a", "\n") if os.path.exists(fname) else ("w", "")

                with open(fname, write_mode) as file:
                    file.write(first_line + data)
            else:
                self.inform(f"unknown treating data method '{print_or_save}'")

        # write into an image
        elif mode == "w":
            # this is a percentage that this process deletes from data

            m = 0.11699961000129999

            data = (arg.filename or arg.text) or self.prompt("content | file path")

            if not os.path.exists(data) or data.endswith("@ig"):
                self.inform("will not treat 'data' inserted as file !", _t="w")
                if data.endswith("@ig"):
                    data = data[:-3]
            else:
                data = open(data, "r").read()

            if not data.isascii():
                self.inform("cannot process non ascii letters !", _t="e")
                exit(-1)

            data += " " * int((m * len(data)) / 100) ** 2

            data_array = np.array([ord(i) for i in data])

            k = len(data_array)
            r = math.ceil(math.sqrt(k))
            c = math.ceil(k / r)

            # max of ascii ord is 127
            image = np.zeros((r, c, 3), dtype=np.uint8)

            image_color = self.get_image_color(arg)

            for i, v in enumerate(data_array):
                row = i // c
                col = i % c
                color = [0, 0, 0]
                color[image_color[0]] = v
                image[row][col] = color

            fname = arg.outfile or self.prompt("output image file")

            # print summary
            self.inform("--------------------------------------")
            self.inform("mode         :", "write" if mode == "w" else "read")
            self.inform("output file  :", fname)
            self.inform("main color  :", image_color[1])
            self.inform("--------------------------------------")

            fname = os.path.splitext(fname)[0]
            fname = fname + ".png" if not fname.endswith(".png") else ""
            cv2.imwrite(fname, image)
            self.inform("data saved successfully .", _t='s')


class BytesConverter(Tools):
    def initialize(self, arg):
        # prompt user to choose between (read, write)
        mode = ("w" if arg.write else "r" if arg.read else None) or self.prompt("[r] read | [w] write").lower()

        if mode == "r":
            image_file = arg.filename or self.prompt("image file")
            image_file = image_file if os.path.splitext(image_file)[1] else image_file + ".png"
            image = cv2.imread(image_file)
            image_color = self.get_image_color(arg)
            ords = image.reshape(-1, 3)[:, image_color[0]]
            ords = np.where(ords == 255, 1, 0)
            fname = arg.outfile or self.prompt("output file")

            self.inform("--------------------------------------")
            self.inform("mode         :", "read")
            self.inform("source file  :", image_file)
            self.inform("output file  :", fname)
            self.inform("main color  :", image_color[1])
            self.inform("--------------------------------------")

            bin_str = ''.join(ords.astype(str))
            k = len(bin_str) // 8
            data = np.array([int(bin_str[i:i + 8], 2) for i in range(0, k * 8, 8)], dtype=np.uint8)

            with open(fname, "wb") as file:
                file.write(data.tobytes())

            self.inform("data retrieved successfully .", _t='s')

        elif mode == "w":
            file_path = arg.filename or self.prompt("file path")
            if not os.path.exists(file_path):
                self.inform("source file not found !", _t="e")
                exit(404)

            fname = arg.outfile or self.prompt("output file")
            fname = os.path.splitext(fname)[0]
            fname = fname + ".png" if not fname.endswith(".png") else ""
            image_color = self.get_image_color(arg)

            self.inform("--------------------------------------")
            self.inform("mode         :", "read")
            self.inform("source file  :", file_path)
            self.inform("output file  :", fname)
            self.inform("main color   :", image_color[1])
            self.inform("--------------------------------------")

            bytes_ = open(file_path, "rb").read()
            byte_array = np.frombuffer(bytes_, dtype=np.uint8)
            bin_array = np.unpackbits(byte_array)
            bin_str = ''.join(bin_array.astype(str))
            data_array = re.split("", bin_str)
            data_array = data_array[1:]
            data_array = data_array[:-1]
            data_array = np.array(data_array, dtype='int16')

            k = len(data_array)
            r = math.ceil(math.sqrt(k))
            c = math.ceil(k / r)

            # max of ascii ord is 127
            image = np.zeros((r, c, 3), dtype=np.uint8)

            for i, v in enumerate(data_array):
                row = i // c
                col = i % c
                color = [0, 0, 0]
                color[image_color[0]] = 255 if v == 1 else 0
                image[row][col] = color

            cv2.imwrite(fname, image)
            self.inform("data saved successfully .", _t='s')


# Utils
def exceptions_handler(_t, _k, _b):
    print(_t, _k)
    if type(_t) is PermissionError:
        print(Fore.RED + f'[{datetime.now().strftime("%H:%M:%S")}] ' +
              "permission error !", Fore.RESET)
    else:
        print(Fore.RED + f'[{datetime.now().strftime("%H:%M:%S")}] ' +
              "unexpected error occur !", Fore.RESET)


def __uninstall_af2i():
    path = os.path.join("/", "bin", __name__)
    if os.path.exists(path):
        os.remove(path)


def __install_af2i():
    path = os.path.abspath(sys.argv[0])

    if not os.access(path, os.X_OK):
        print(Fore.RED + f'[{datetime.now().strftime("%H:%M:%S")}] ' +
              "required permissions not granted ! try 'chmod +x ...'", Fore.RESET)
        return
    shutil.move(path, os.path.join("/", "bin", os.path.basename(path)))


def print_help():
    help_ = "Convert text file content or text into png image !\n"
    help_ += "This version does not contain converting non ascii letters !\n"
    help_ += "add '@ig' flag in case you want to obfuscate a file path, because (content | file path, -t, " \
             "--text) reads from a file path if it is exists\n "
    help_ += "when you read from an Image, you can get specific characters by adding '@n' flag to (-p --print -s " \
             "--save), where n represents printed or saved content length\n"

    return help_


# Handle all exceptions at once
sys.excepthook = exceptions_handler

# Parse arguments
parser = argparse.ArgumentParser(
    prog="AF2I",
    description=print_help(),
    epilog="check ou my new pentesting tool at https://predatorc.netlify.app"
)

parser.add_argument('-f', '--filename')

parser.add_argument('-t', '--text',
                    help="content to be converted, set only one filename or text, filename is preferred !",
                    default="There is no such thing as a coincidence, but rather an explanation the herd "
                            "found for an event they did not understand !")

parser.add_argument('-p', '--print',
                    help="print retrieved data, preferred .", action="store_true")

parser.add_argument('-s', '--save',
                    help="save retrieved data, not preferred .", action="store_true")

parser.add_argument('-o', '--outfile',
                    help="output file. PNG in case of writing, otherwise any text-file !")

parser.add_argument('-w', '--write',
                    action='store_true')

parser.add_argument('-r', '--read',
                    action='store_true')

parser.add_argument('-i', '--install',
                    action='store_true')

parser.add_argument('-u', '--uninstall',
                    action='store_true')

parser.add_argument('-v', '--version',
                    action='store_true')

parser.add_argument('-a', '--author',
                    action='store_true')

parser.add_argument('-b', '--bin',
                    action='store_true', help="bin for binary-file")

parser.add_argument('-c', '--color',
                    choices=['r', 'g', 'b'], help="main color of generated image .")

args_ = parser.parse_args()

# Initialize
if args_.install:
    __install_af2i()

elif args_.version:
    print(f"af2i, v{__version__}, non-stable")

elif args_.author:
    print(f"| badr-eddin | badr.eddin.py@instagram.com |")

elif args_.uninstall:
    __uninstall_af2i()

else:
    if not args_.bin:
        converter = AsciiConverter()
    else:
        converter = BytesConverter()

    converter.initialize(args_)
