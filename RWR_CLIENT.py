import socket
import threading
import pygame
import time

#IP,PORT and screen width/height
IP = "127.0.0.1"
PORT = 9999
WIDTH = 800
HEIGHT = 600
RWR_POSITION = []
#converting into Lat lng
ref_pi_x = 400
ref_pi_y = 500
ref_lat = 0
ref_lng = 0
lat_scale = (90-(-20))/600
lng_scale = (90-(-90))/800
#pygame initialization
pygame.init()
space = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Craft Simulation")

class Aircraft:#Aircraft Class
    def __init__(self, aircraft_name, IP, PORT):
        self.aircraft_name = aircraft_name
        self.radius = 10
        self.color = "blue"
        self.position = [WIDTH // 2, HEIGHT // 2]
        self.step_size = 2
        self.IP = IP
        self.PORT = PORT
        self.rwr_client = socket.socket()
        self.message = ""
    def draw_aircraft(self):
        pygame.draw.circle(space, self.color, self.position, self.radius)
    def move_up(self):
        self.position[1] -= self.step_size
    def move_down(self):
        self.position[1] += self.step_size
    def move_left(self):
        self.position[0] -= self.step_size
    def move_right(self):
        self.position[0] += self.step_size
    def send_data(self, MSG):
        self.message = MSG 
        self.rwr_client.send(str(MSG).encode("utf-8"))
    def connect_to_server(self):
        self.rwr_client.connect((self.IP, self.PORT))
        print(f"connection success")
#for coverting the x,y coordinates to lat,lng coordinates
def convert_to_latlng(coordinates):#conversion to lattitude and longitutde
    lat = ref_lat+(coordinates[-1]-ref_pi_y)*lat_scale
    lng = ref_lng+(coordinates[0]-ref_pi_x)*lng_scale
    return [lat,lng]

def client_main(this_aircraft):
    this_aircraft.connect_to_server()
    this_aircraft.send_data(str(this_aircraft.aircraft_name))#sending the username
    while True:
        fnl_msg_rwr = convert_to_latlng(this_aircraft.position)
        data = RWR_POSITION.append(fnl_msg_rwr)
        this_aircraft.send_data(fnl_msg_rwr)#sending the position
        time.sleep(1)  # Add some delay to avoid flooding the server

def showdata_rwr():
    while 1:
        INPUT = input("Eneter rwr_showdata to view the data: ").lower
        if INPUT == "rwr_showdata_d":
            print(RWR_POSITION)

def Draw_line():
    screen = space
    color = (150, 250, 80)
    start_pt = (0, 500)
    end_pt = (800, 500)
    pygame.draw.line(screen, color, start_pt, end_pt)

def start_game(aircraft_instance):
    window_open = True
    while window_open:
        space.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                window_open = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    aircraft_instance.move_down()
                if event.key == pygame.K_UP:
                    aircraft_instance.move_up()
                if event.key == pygame.K_LEFT:
                    aircraft_instance.move_left()
                if event.key == pygame.K_RIGHT:
                    aircraft_instance.move_right()

        if aircraft_instance.position[1] <= 10:
            aircraft_instance.position[1] = 10
        elif aircraft_instance.position[1] >= 580:
            aircraft_instance.position[1] = 580
        elif aircraft_instance.position[0] <= 20:
            aircraft_instance.position[0] = 20
        elif aircraft_instance.position[0] >= 780:
            aircraft_instance.position[0] = 780
        Draw_line()
        aircraft_instance.draw_aircraft()
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    my_aircraft = Aircraft("aircraft_MI17", IP, PORT)
    data_sharing = threading.Thread(target=client_main, args=(my_aircraft,))
    data_sharing.start()
    threading.Thread(target=showdata_rwr).start()
    start_game(my_aircraft)