# -- coding: cp1251 --

import math
import socket
import pygame
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox

name = ""
color = ""
buffer = 1024


def login():
    global name
    name = row.get()
    if name and color:
        root.destroy()
        root.quit()
    else:
        tk.messagebox.showerror("������", "�� �� ������ ���� ��� �� ��� ���!")


def scroll(event):
    global color
    color = combo.get()
    style.configure("TCombobox", fieldbackground=color, background="white")


root = tk.Tk()
root.title("�����")
root.geometry("300x200")

style = ttk.Style()
style.theme_use('clam')

name_label = tk.Label(root, text="����� ���� �������:")
name_label.pack()
row = tk.Entry(root, width=30, justify="center")
row.pack()
color_label = tk.Label(root, text="������ ����:")
color_label.pack()
colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
          'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
          'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
          'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DeepSkyBlue',
          'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']

combo = ttk.Combobox(root, values=colors, textvariable=color)
combo.bind("<<ComboboxSelected>>", scroll)
combo.pack()
name_btn = tk.Button(root, text="����� � ����", command=login)
name_btn.pack()
root.mainloop()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ����������� �����
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # ��������� �������������
sock.connect(("localhost", 10000))
# ���������� ���� � ���
sock.send(("color:<" + name + "," + color + ">").encode())

pygame.init()
WIDTH = 800
HEIGHT = 600
CC = (WIDTH // 2, HEIGHT // 2)
old = (0, 0)
radius = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("��������")


def find(vector: str):
    global buffer
    first = None
    for num, sign in enumerate(vector):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            result = vector[first + 1:second]  # ��������
            return result
    buffer = int(buffer * 1.5)
    return ""


def draw_bacteries(data: list[str]):
    for num, bact in enumerate(data):
        data = bact.split(" ")  # ��������� �� �������� ��������� ����� ��������
        x = CC[0] + int(data[0])
        y = CC[1] + int(data[1])
        size = int(data[2])
        color = data[3]
        pygame.draw.circle(screen, color, (x, y), size)


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if pygame.mouse.get_focused():
            pos = pygame.mouse.get_pos()
            vector = pos[0] - CC[0], pos[1] - CC[1]
            lenv = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
            vector = vector[0] / lenv, vector[1] / lenv
            if lenv <= radius:
                vector = 0, 0
            if vector != old:
                old = vector
                msg = f"<{vector[0]},{vector[1]}>"
                sock.send(msg.encode())

    # ��������
    data = sock.recv(buffer).decode()
    print("�������:", data)
    # print(data)
    data = find(data).split(",")  # ��������� �� ����
    print(data)

    # ������ ����� ����
    screen.fill('gray')
    # pygame.draw.circle(screen, (255, 0, 0), CC, radius)
    if data != ['']:
        radius = int(data[0])
        draw_bacteries(data[1:])
    pygame.draw.circle(screen, color, CC, radius)
    pygame.display.update()

pygame.quit()