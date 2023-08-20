# -*- coding: cp1251 -*-


import math
import random
import socket
import time
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import pygame
from russian_names import RussianNames

engine = create_engine("postgresql+psycopg2://postgres:12345@localhost/zzzzz")
Session = sessionmaker(bind=engine)
Base = declarative_base()
s = Session()

# ��������� �������� ��� pygame
pygame.init()
WIDHT_ROOM, HEIGHT_ROOM = 4000, 4000
WIDHT_SERVER, HEIGHT_SERVER = 300, 300
FPS = 100
colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
          'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
          'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
          'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DeepSkyBlue',
          'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']
MOBS_QUANTITY = 25
FOOD_SIZE = 15
FOOD_QUANTITY = WIDHT_ROOM * HEIGHT_ROOM // 40000

# �������� ���� �������
screen = pygame.display.set_mode((WIDHT_SERVER, HEIGHT_SERVER))
pygame.display.set_caption("������")
clock = pygame.time.Clock()


def find(vector: str):
    first = None
    for num, sign in enumerate(vector):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            result = list(map(float, vector[first + 1:second].split(",")))
            return result
    return ""


def find_color(info: str):
    first = None
    for num, sign in enumerate(info):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            result = info[first + 1:second].split(",")
            return result
    return ""


# ������������� ����� ������� �������
class Player(Base):
    __tablename__ = "gamers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250))
    address = Column(String)
    x = Column(Integer, default=500)
    y = Column(Integer, default=500)
    size = Column(Integer, default=50)
    errors = Column(Integer, default=0)
    abs_speed = Column(Integer, default=1)
    speed_x = Column(Integer, default=0)
    speed_y = Column(Integer, default=0)
    color = Column(String(250), default="red")  # �������� ����
    w_vision = Column(Integer, default=800)
    h_vision = Column(Integer, default=600)  # �������� ������ �������

    def __init__(self, name, address):
        self.name = name
        self.address = address


# ��������� ����� ������� �������
class LocalPlayer:
    def __init__(self, id, name, sock, addr):
        self.id = id
        self.db: Player = s.get(Player, self.id)
        self.sock = sock
        self.name = name
        self.address = addr
        self.x = 500
        self.y = 500
        self.size = 50
        self.errors = 0
        self.abs_speed = 1
        self.speed_x = 0
        self.speed_y = 0
        self.color = "red"
        self.w_vision = 800
        self.h_vision = 600
        self.L = 1

    def update(self):
        # � ����������
        if self.x - self.size <= 0:  # ���� ����� ������� �� ����� ������
            if self.speed_x >= 0:  # �� ��� ���� ��������� �����
                self.x += self.speed_x  # �� ������� ���
        elif self.x + self.size >= WIDHT_ROOM:  # ���� ����� ������� �� ������ ������
            if self.speed_x <= 0:  # �� ��� ���� ��������� �����
                self.x += self.speed_x  # �� ������� ���
        else:  # ���� ����� ��������� � ������� �������
            self.x += self.speed_x

        # y ����������
        if self.y - self.size <= 0:  # ���� ����� ������� �� ����� ������
            if self.speed_y >= 0:  # �� ��� ���� ��������� �����
                self.y += self.speed_y  # �� ������� ���
        elif self.y + self.size >= HEIGHT_ROOM:  # ���� ����� ������� �� ������ ������
            if self.speed_y <= 0:  # �� ��� ���� ��������� �����
                self.y += self.speed_y  # �� ������� ���
        else:  # ���� ����� ��������� � ������� �������
            self.y += self.speed_y

        if self.size >= 100:
            self.size -= self.size / 18000

        if self.size >= self.w_vision / 4:
            if self.w_vision <= WIDHT_ROOM or self.h_vision <= HEIGHT_ROOM:
                self.L *= 2
                self.w_vision = 800 * self.L
                self.h_vision = 600 * self.L

        if self.size < self.w_vision / 8 and self.size < self.h_vision / 8:
            if self.L > 1:
                self.L //= 2
                self.w_vision = 800 * self.L
                self.h_vision = 600 * self.L

    def new_speed(self):
        self.abs_speed = 10 / math.sqrt(self.size)

    def change_speed(self, vector):
        vector = find(vector)
        if vector[0] == 0 and vector[1] == 0:
            self.speed_x = self.speed_y = 0
        else:
            vector = vector[0] * self.abs_speed, vector[1] * self.abs_speed
            self.speed_x = vector[0]
            self.speed_y = vector[1]

    def load(self):
        self.size = self.db.size
        self.abs_speed = self.db.abs_speed
        self.speed_x = self.db.speed_x
        self.speed_y = self.db.speed_y
        self.errors = self.db.errors
        self.x = self.db.x
        self.y = self.db.y
        self.color = self.db.color
        self.w_vision = self.db.w_vision
        self.h_vision = self.db.h_vision
        return self

    def sync(self):
        self.db.size = self.size
        self.db.abs_speed = self.abs_speed
        self.db.speed_x = self.speed_x
        self.db.speed_y = self.speed_y
        self.db.errors = self.errors
        self.db.x = self.x
        self.db.y = self.y
        self.db.color = self.color
        self.db.w_vision = self.w_vision
        self.db.h_vision = self.h_vision
        s.merge(self.db)
        s.commit()


class Food:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color


Base.metadata.create_all(engine)
players = {}

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ����������� �����
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # ��������� �������������
main_socket.bind(("localhost", 10000))  # IP � ���� ����������� � �����
main_socket.setblocking(False)  # �������������, �� ��� ������
main_socket.listen(5)  # ��������� �������� ����������, 5 ������������� �����������
print("����� ��������")

# �������� �����
names = RussianNames(count=MOBS_QUANTITY * 2)
names = list(set(names))  # ������ ��������������� ���

for x in range(MOBS_QUANTITY):
    server_mob = Player(names[x], None)
    server_mob.color = random.choice(colors)
    server_mob.x, server_mob.y = random.randint(0, WIDHT_ROOM), random.randint(0, HEIGHT_ROOM)
    server_mob.speed_x, server_mob.speed_y = random.randint(-1, 1), random.randint(-1, 1)
    server_mob.size = random.randint(10, 100)
    s.add(server_mob)
    s.commit()
    local_mob = LocalPlayer(server_mob.id, server_mob.name, None, None).load()
    players[server_mob.id] = local_mob  # ���������� ���� ����� � �������

foods = []
need = FOOD_QUANTITY - len(foods)
for i in range(need):
    foods.append(Food(
        x=random.randint(0, WIDHT_ROOM),
        y=random.randint(0, HEIGHT_ROOM),
        size=FOOD_SIZE,
        color=random.choice(colors)
    ))

tick = -1
server_works = True
while server_works:
    clock.tick(FPS)
    tick += 1
    if tick % 200 == 0:
        try:
            # ��������� �������� ����� � ����
            new_socket, addr = main_socket.accept()  # ��������� ��������
            print('�����������', addr)
            new_socket.setblocking(False)
            login = new_socket.recv(1024).decode()
            player = Player("���", addr)

            if login.startswith("color"):
                data = find_color(login[6:])
                player.name, player.color = data

            s.merge(player)
            s.commit()

            addr = f'({addr[0]},{addr[1]})'
            data = s.query(Player).filter(Player.address == addr)
            for user in data:
                player = LocalPlayer(user.id, "���", new_socket, addr).load()
                players[user.id] = player

        except BlockingIOError:
            pass

    # ��������� ������� �������
    for id in list(players):
        if players[id].sock is not None:
            try:
                data = players[id].sock.recv(1024).decode()
                players[id].change_speed(data)
            except:
                pass
        else:
            if tick % 400 == 0:
                vector = f"<{random.randint(-1, 1)},{random.randint(-1, 1)}>"
                players[id].change_speed(vector)  # ��������� ������ ��� �����

    need = MOBS_QUANTITY - len(players)
    if need > 0:
        names = RussianNames(count=need * 2, patronymic=False, surname=False, rare=True)
        names = list(set(names))
        for i in range(need):
            server_mob = Player(names[i], None)
            server_mob.color = random.choice(colors)
            spawn: LocalPlayer = random.choice(foods)
            foods.remove(spawn)
            server_mob.x, server_mob.y = spawn.x, spawn.y
            server_mob.size = random.randint(10, 100)
            s.add(server_mob)
            s.commit()
            local_mob = LocalPlayer(server_mob.id, server_mob.name, None, None).load()
            local_mob.new_speed()
            players[server_mob.id] = local_mob

    # ���������, ��� ����� ������ �����
    # + �������� ���� �����
    # bacteries = {}
    visible_bacteries = {}
    for id in list(players):
        # bacteries[id] = s.get(Player, id)  # ��������� �������
        visible_bacteries[id] = []

    pairs = list(players.items())
    for i in range(0, len(pairs)):
        for food in foods:
            hero: LocalPlayer = pairs[i][1]
            dist_x = food.x - hero.x
            dist_y = food.y - hero.y
            if abs(dist_x) <= hero.w_vision // 2 + food.size and abs(dist_y) <= hero.h_vision // 2 + food.size:
                distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
                if distance < hero.size:
                    hero.size = math.sqrt(hero.size ** 2 + food.size ** 2)
                    hero.new_speed()
                    food.size = 0
                    foods.remove(food)
                if hero.address is not None and food.size != 0:
                    x_ = str(round(dist_x / hero.L))
                    y_ = str(round(dist_y / hero.L))
                    size_ = str(round(food.size / hero.L))
                    color_ = food.color


                    data = x_ + " " + y_ + " " + size_ + " " + color_
                    visible_bacteries[hero.id].append(data)
        for j in range(i + 1, len(pairs)):
            # ������������� ���� �������
            hero_1: Player = pairs[i][1]
            hero_2: Player = pairs[j][1]
            dist_x = hero_2.x - hero_1.x
            dist_y = hero_2.y - hero_1.y

            # i-� ����� ����� j-����
            if abs(dist_x) <= hero_1.w_vision // 2 + hero_2.size and abs(dist_y) <= hero_1.h_vision // 2 + hero_2.size:
                # �������� ����� �� 1-� ������ 2-�� ������
                distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
                if distance <= hero_1.size and hero_1.size > 1.1 * hero_2.size:
                    hero_1.size = math.sqrt(hero.size ** 2 + food.size ** 2)
                    hero_1.new_speed()
                    hero_2.size, hero_2.speed_x, hero_2.speed_y = 0, 0, 0

                if hero_1.address is not None:
                    # ���������� ������ � ���������� � ������
                    x_ = str(round(dist_x / hero_1.L))
                    y_ = str(round(dist_y / hero_1.L))  # ���������
                    size_ = str(round(hero_2.size / hero_1.L))
                    color_ = hero_2.color

                    data = x_ + " " + y_ + " " + size_ + " " + color_
                    visible_bacteries[hero_1.id].append(data)

            # j-� ����� ����� i-����
            if abs(dist_x) <= hero_2.w_vision // 2 + hero_1.size and abs(dist_y) <= hero_2.h_vision // 2 + hero_1.size:
                # �������� ����� �� 2-� ������ 1-�� ������
                distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
                if distance <= hero_2.size and hero_2.size > 1.1 * hero_1.size:
                    hero_2.size = math.sqrt(hero_2.size ** 2 + hero_1.size ** 2)
                    hero_2.new_speed()
                    hero_1.size, hero_1.speed_x, hero_1.speed_y = 0, 0, 0

                if hero_2.address is not None:
                    # ���������� ������ � ���������� � ������
                    x_ = str(round(-dist_x / hero_2.L))
                    y_ = str(round(-dist_y / hero_2.L))  # ���������
                    size_ = str(round(hero_1.size / hero_2.L))
                    color_ = hero_1.color

                    data = x_ + " " + y_ + " " + size_ + " " + color_
                    visible_bacteries[hero_2.id].append(data)

    # ��������� ����� ������ ��������
    for id in list(players):
        r_ = str(round(players[id].size / players[id].L))
        visible_bacteries[id] = [r_] + visible_bacteries[id]
        visible_bacteries[id] = "<" + ",".join(visible_bacteries[id]) + ">"

    # ���������� ������ �������� ����
    for id in list(players):
        if players[id].sock is not None:
            try:
                players[id].sock.send(visible_bacteries[id].encode())
            except:
                players[id].sock.close()
                del players[id]
                # ��� �� ������� ������� �� ��
                s.query(Player).filter(Player.id == id).delete()
                s.commit()
                print("����� ������")

    # ������ ������ �� ������������ �������
    for id in list(players):
        if players[id].errors >= 500 or players[id].size == 0:
            if players[id].sock is not None:
                players[id].sock.close()
            del players[id]
            s.query(Player).filter(Player.id == id).delete()
            s.commit()

    # ������������ ��������� ����
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server_works = False

    screen.fill('black')
    for id in list(players):
        player = players[id]
        x = player.x * WIDHT_SERVER // WIDHT_ROOM
        y = player.y * HEIGHT_SERVER // HEIGHT_ROOM
        size = player.size * WIDHT_SERVER // WIDHT_ROOM
        pygame.draw.circle(screen, player.color, (x, y), size)  # ����

    for id in list(players):
        player = players[id]
        players[id].update()
        if tick % 300 == 0:
            players[id].sync()

    pygame.display.update()

pygame.quit()
main_socket.close()
s.query(Player).delete()
s.commit()
