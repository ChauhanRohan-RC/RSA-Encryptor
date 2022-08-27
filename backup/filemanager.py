import os
import sys
import os.path
import pickle
import shutil
import random
from stat import S_IREAD, S_IWUSR


# copying ,renaming and scanning can be done without specifying any main_cli file
class FileManager:
    def __init__(self, fpath=None):
        self.fpath = fpath

    def log(self, x):
        with open(self.fpath, "w+") as file:
            file.write(x)
            file.close()

    def wb(self, data):
        with open(self.fpath, "wb+") as file:
            file.write(data)
            file.close()

    def append(self, y):
        with open(self.fpath, "a+") as file:
            file.write(y)
            file.close()

    def read(self):
        try:
            with open(self.fpath, "r+") as file:
                return file.read()
        except FileNotFoundError:
            return None

    def rl(self):
        try:
            with open(self.fpath, "r+") as file:
                return file.readlines()
        except FileNotFoundError:
            return None

    def rb(self):
        try:
            with open(self.fpath, "rb+") as file:
                return file.read()
        except FileNotFoundError:
            return None

    def create(self):
        try:
            with open(self.fpath, "x"):
                return True
        except FileExistsError:
            return False

    def delete(self):
        try:
            os.remove(self.fpath)
            return True
        except FileNotFoundError:
            return False

    def dir_name(self, filepath):
        dir_, name = os.path.split(filepath)
        return dir_, name

    def name_ex(self, filename):
        name, ex = os.path.splitext(filename)
        return name, ex

    def scan(self, fileformat_list, start, mode='path'):
        filename = []
        filepath = []
        for path, subdir, files in os.walk(start):
            for file in files:
                if self.name_ex(file)[1].lower() in fileformat_list:
                    filename.append(file)
                    filepath.append(os.path.join(path, file))
        if mode == "name":
            return filename
        elif mode == "path":
            return filepath
        return filepath, filename

    def write_bytes(self, data):
        try:
            with open(self.fpath, 'wb+') as file:
                pickle.dump(data, file)
                return True
        except Exception as e:
            print(f'could not log bytes : {e}')
            return False

    def read_bytes(self):
        try:
            with open(self.fpath, 'rb+') as file:
                data = pickle.load(file)
                return data
        except Exception as e:
            print(f'could not read bytes : {e}')
            return None

    def rename(self, opath, nname):
        try:
            head, tail = os.path.split(opath)
            npath = os.path.join(head, nname)
            os.renames(opath, npath)
            return True
        except FileNotFoundError:
            print("file does not exist")
            return False

    def copy(self, opath, npath):
        try:
            shutil.copy(opath, npath)
            return True
        except Exception as e:
            print(f"could not copy : {e}")
            return False

    def cleartext(self):
        try:
            with open(self.fpath, "w+") as file:
                file.write("")
                return True
        except FileNotFoundError:
            print("file not found")
            return False

    def readonly(self):
        try:
            os.chmod(self.fpath, S_IREAD)
            return True
        except FileNotFoundError:
            print("file not found")
            return False

    def clearreadonly(self):
        try:
            os.chmod(self.fpath, S_IWUSR)
            return True
        except FileNotFoundError:
            print('File not found')
            return False

    def shuffle(self, list1, list2=None):
        if list2:
            c = list(zip(list1, list2))
            random.shuffle(c)
            list1, list2 = zip(*c)
            return list(list1), list(list2)
        return random.shuffle(list1)

    def image_from_song(self, song_path, resizetouple=None, save_path=None):
        from mutagen.id3 import ID3
        from io import BytesIO
        from PIL import Image
        try:
            tags = ID3(song_path)
            keys = tags.keys()

            def get_image_key(keylist):
                for key_ in keylist:
                    if 'APIC' in key_:
                        return key_
                return None

            key = get_image_key(keys)
            if key is not None:
                pic = tags[key].data
                image = Image.open(BytesIO(pic))
                if save_path:
                    image.save(save_path)
                if resizetouple:
                    image2 = image.resize((resizetouple[0], resizetouple[1]), Image.ANTIALIAS)
                    if save_path:
                        image2.save(save_path)
                    return image2
                return image
            return None
        except Exception as e:
            print(e)
            return None

    def exists(self):
        if os.path.exists(self.fpath):
            return True
        return False

    def platform(self):
        if sys.platform.startswith('win'):
            return "win"
        elif sys.platform.startswith('darwin'):
            return 'darwin'
        else:
            return 'linux'

    def mills_to_time(self, mills):
        secs = mills//1000
        if secs < 60:
            min_ = 0
            sec = secs
        else:
            min_ = secs//60
            sec = secs % 60
        return min_, sec

    def mkdir(self, dir_):
        try:
            if not os.path.isdir(dir_):
                os.mkdir(dir_)
                return True
            return True
        except Exception as e:
            print(f'exception in mkdir : {e}')
            return False


if __name__ == "__main__":
    fm = FileManager("B:\RC\PycharmProjects\media\ee.txt")
    print()

