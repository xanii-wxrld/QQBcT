import socket
import time
import psycopg2
import random
import faker
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


engine = create_engine("postgresql+psycopg2://postgres:12345@localhost/zzzzz")
Base = declarative_base()

Session = sessionmaker(bind=engine)
s = Session()

class Players(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(250), nullable=False)
    address = Column(String)
    x = Column(Integer, default=500)
    y = Column(Integer, default=500)
    size = Column(Integer, default=50)
    errors = Column(Integer, default=0)
    abs_speed = Column(Integer, default=1)
    speed_x = Column(Integer, default=0)
    speed_y = Column(Integer, default=0)

    def __init__(self, name, address):
        self.name = name
        self.address = address

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(("localhost", 10000))

main_socket.setblocking(False)
main_socket.listen(5)
print("Сокет создался")

us = []

while True:
    try:
        new_socket, addr = main_socket.accept()
        print("Подключился", addr)
        new_socket.setblocking(False)
        us.append(new_socket)
    except BlockingIOError:
        pass

    for sock in us:
        try:
            data = sock.recv(1024).decode()
            sock.send("life has no meaning and that's ok.".encode())
        except:
            us.remove(sock)
            sock.close()
            print("Сокет закрыт")
    time.sleep(1)

"""import socket
import time

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(("localhost", 10000))

main_socket.setblocking(False)
main_socket.listen(5)
print("Сокет создался")

us = []

while True:
    try:
        new_socket, addr = main_socket.accept()
        print("Подключился", addr)
        new_socket.setblocking(False)
        us.append(new_socket)
    except BlockingIOError:
        pass

    for sock in us:
        try:
            data = sock.recv(1024).decode()
            print("Получил", data)
        except:
            pass"""

