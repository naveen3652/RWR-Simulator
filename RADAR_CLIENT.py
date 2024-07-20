import socket
import threading
import pygame
import time

#IP,PORT and Screen width and height
IP = "127.0.0.1"
PORT = 9999
WIDTH = 800
HEIGHT = 600

#converting into Lat lng
ref_pi_x = 400
ref_pi_y = 500
ref_lat = 0
ref_lng = 0
lat_scale = (90-(-20))/600
lng_scale = (90-(-90))/800
#Pygame initializations
pygame.init()
space = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Craft Simulation")

# Creating a radar class
class RADAR:
    def __init__(self, radar_radius, radar_name, IP, PORT, Pt, wavelength,Gt,Gr,RCS):
        self.radar_radius = radar_radius
        self.Pt = Pt
        self.wavelength = wavelength
        self.Gt = Gt
        self.Gr = Gr
        self.RCS = RCS
        self.radar_name = radar_name
        self.radar_position = [200,500]
        self.radar_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = IP
        self.PORT = PORT
    def draw_RADAR(self):
        radar_color = (255, 255, 255)
        pygame.draw.circle(space, radar_color,self.radar_position,self.radar_radius, 1)
    def threshold_range(self):
        threshold_radius = (self.radar_radius * 1.5)
        threshold_color = (255, 6, 0)
        pygame.draw.circle(space, threshold_color, self.radar_position, int(threshold_radius), 2)
        pygame.draw.circle(space, threshold_color, self.radar_position, 5)
    def right_move(self):
        foot_size = 2
        self.radar_position[0]+=foot_size
    def left_move(self):
        foot_size = 2
        self.radar_position[0]-=foot_size
    def send_data(self, MSG):
        self.message = MSG
        self.radar_client.sendall(MSG.encode("utf-8"))
    def connect_to_server(self):
        self.radar_client.connect((self.IP, self.PORT))
        print("Connection success")

def convert_to_latlng(coordinates):#conversion to lattitude and longitutde
    lat = ref_lat+(coordinates[-1]-ref_pi_y)*lat_scale
    lng = ref_lng+(coordinates[0]-ref_pi_x)*lng_scale
    return [lat,lng]

def Draw_line():#draw the ground line
    screen = space
    color = (150, 250, 80)
    start_pt = (0, 500)
    end_pt = (800, 500)
    pygame.draw.line(screen, color, start_pt, end_pt)

def client_main(this_Radar):
    this_Radar.connect_to_server()
    this_Radar.send_data(str(this_Radar.radar_name))  # Initial sending of user name seperately
    Radar_Data = {'Radar type':radar_name, 'wavelength':wavelength, 'Gt':t_antenna_gain, 'Gr':r_antenna_gain,'Pt':Pt, 'RCS':RCS,'Radar Range [lat,lng] Km':[LAT, LNG]}
    this_Radar.send_data(str(Radar_Data))
    while True:
        fnl_msg_radar = convert_to_latlng(this_Radar.radar_position)
        this_Radar.send_data(str(fnl_msg_radar))
        time.sleep(1)  # Add some delay to avoid flooding the server

def start_game(radar_instance):#main pygame loop
    window_open = True
    while window_open:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                window_open = False
            # setting movement keys for the RADAR
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    radar_instance.left_move()
                if event.key == pygame.K_d:
                    radar_instance.right_move()

        space.fill((0, 0, 0))
        Draw_line()

        radar_instance.draw_RADAR()
        radar_instance.threshold_range()
        pygame.display.update()

        # Add a way to exit the loop, for example, when the 'q' key is pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            window_open = False

    pygame.quit()

radar_name = str(input("Enter the RADAR name : "))
Pt = float(input("enter the Transmitting power (Pt) of the RADAR in Watts: "))
wavelength = float(input("Enter the Wavelength of the RADAR signal in meters: "))
t_antenna_gain = float(input("Enter the Transmitting Antenna Gain (Gt) in dBi: "))
r_antenna_gain = float(input("Enter the Receiving Antenna Gain (Gr) in dBi: "))
RCS = float(input("Enter the RADAR Cross-section area (RCS) in dBm: "))
print("1 pixel in y-axis = 0.959931088595 deg in latituse")
print("1 pixel in x-axis = 1.1780972 deg in longitude")
radar_radius = int(input("enter the RADAR range in pixels: "))
LAT = radar_radius*(0.959931088595)
LNG = radar_radius*(1.1780972)
print(f"The total range is {LAT} Km in latitude and {LNG} Km in longitude")



if __name__ == "__main__":
    radar1 = RADAR(radar_radius, radar_name, "127.0.0.1", 9999,Pt,wavelength, t_antenna_gain,r_antenna_gain,RCS)
    data_sharing = threading.Thread(target=client_main, args=(radar1,))
    data_sharing.start()
    start_game(radar1)
