<<<<<<< HEAD
import socket
import pygame
import  math

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Настраиваем сокет
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Отключаем пакетирование
sock.connect(("localhost", 10000))

pygame.init()

WIDTH = 800
HEIGHT = 600
CC = (WIDTH // 2, HEIGHT // 2)
old = (0, 0)
radius = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BCT")


run = True
while run:
    for e in pygame.event.get():
        if e == pygame.QUIT:
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
        msg = f"<{vector[0]}, {vector[1]}>"
        sock.send(msg.encode())
    screen.fill("gray")
    pygame.draw.circle(screen, (0, 0, 0), CC, radius)
    pygame.display.update()

    data = sock.recv(1024).decode()
    print("получил: ", data)

pygame.quit()

=======
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Настраиваем сокет
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Отключаем пакетирование
sock.connect(("localhost", 10000))

while True:
    sock.send("Приыет".encode())


>>>>>>> 05698eabbe4c22635f5f902214805d9995933345
