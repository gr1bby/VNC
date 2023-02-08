import json
import socket
import tkinter as tk
from tkinter.constants import END
from tkinter import simpledialog, messagebox


actions = (
    'system',
    'cwd',
    'ls',
    'cd',
    'mkdir',
    'rmdir',
    'mkfile',
    'rmfile',
)

def send_data(message: str):
    data = message.encode('utf-8')
    connection.sendall(data)

def receive_data() -> str:
    message = connection.recv(1024)
    return message.decode()

# system
def show_info():
    command = actions[0]
    send_data(command)

    data_str = receive_data()
    data = json.loads(data_str)
    message = ''

    for key in data:
        message += f"{key}: {data[key]}" + '\n'

    messagebox.showinfo('Client system', message)

# cwd
def get_cwd():
    command = actions[1]
    send_data(command)

    cwd = receive_data()
    entry.delete(0, END)
    entry.insert(0, cwd)

# ls
def show_files_and_dirs():
    command = actions[2]
    send_data(command)

    files_and_dirs = sorted(receive_data().split())

    if files_and_dirs:
        lbox.delete(1, END)
        for item in files_and_dirs:
            lbox.insert(END, item)

# cd
def cd_by_path():
    command = actions[3]
    send_data(command)

    next_dir = entry.get() + ' '
    send_data(next_dir)


def cd_by_click():
    selected = lbox.curselection()
    print(selected)
    name = lbox.get(selected[0])
    print(name)
    if len(name.split('.')) == 1 or name == '..':
        command = actions[3]
        send_data(command)

        next_dir = name + ' '
        send_data(next_dir)

# mkdir
def make_dir():
    command = actions[4]
    send_data(command)

    title, prompt = "Make directory", "Input name of directory"

    new_dir = dialog_window(title, prompt)
    send_data(new_dir)

# rmdir
def rm_dir():
    selected = lbox.curselection()
    if selected:
        name = lbox.get(selected[0])
        if len(name.split('.')) == 1:
            command = actions[5]
            send_data(command)
            send_data(name) 

# mkfile
def create_file():
    command = actions[6]
    send_data(command)

    title, prompt = "Create file", "Input name of file"

    file_name = dialog_window(title, prompt)
    send_data(file_name)

# rmfile
def rm_file():
    selected = lbox.curselection()
    if selected:
        name = lbox.get(selected[0])
        if len(name.split('.')) == 2:
            command = actions[7]
            send_data(command)
            send_data(name)


def dialog_window(title: str, prompt: str):
    return simpledialog.askstring(title=title, prompt=prompt)


def handler():
    get_cwd()
    show_files_and_dirs()


root = tk.Tk()
root.title("VNCServer")
root.geometry("1280x720")
root.resizable(False, False)

main_menu = tk.Menu()
main_menu.add_command(label='mkdir', command=make_dir)
main_menu.add_command(label='mkfile', command=create_file)
main_menu.add_command(label='rmdir', command=rm_dir)
main_menu.add_command(label='rmfile', command=rm_file)
main_menu.add_command(label='system', command=show_info)
main_menu.add_command(label='open', command=cd_by_click)
main_menu.add_command(label='update', command=handler)


entry = tk.Entry()
entry.place(height=40, width=1120)

btn = tk.Button(
    text="Go to",
    command=cd_by_path,
)
btn.place(x=1120, height=40, width=160)

scrollbar = tk.Scrollbar(root)
scrollbar.place(x=1250, y=40, width=30, height=680)

lbox = tk.Listbox(yscrollcommand=scrollbar.set, width=30)
lbox.insert(0, '..')
lbox.place(y=40, height=680, width=1250)
scrollbar.config(command=lbox.yview)

root.config(menu=main_menu)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('192.168.43.22', 6009))
server.listen(0)
print('Waiting connection...')


if __name__ == '__main__':
    try:
        while True:
            connection, client_address = server.accept()
            print(f"Connected to {client_address}")

            handler()

            root.mainloop()
            
    finally:
        print('Connection closed')
        server.close()
