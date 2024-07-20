import socket
import threading
import math
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#IP, port and creating the necessary arrays to store data
IP = "127.0.0.1"
PORT = 9999
RWR_coordinates_list = []
RADAR_coordinates_list = []
time_list = []
distance_list_moniter = []
RECEIVED_POWER_FOR_RWR = []
#Haversine formula to claculate distance from lat,lng
def haversine(lat1, lon1, lat2, lon2):
    R = 353.42916  # Radius of the screen in kilometers (300 pixels X 1.1780972)
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Calculate distance using Haversine formula
    a = math.sin(dlat/2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance 
# Listens for data from the RWR client
def listen_for_data_rwr(rwr_client):
    while True:
        message_from_rwr = rwr_client.recv(2048).decode()#decode the data
        try:
            rwr_data_list = eval(message_from_rwr.replace("(", "[").replace(")", "]"))
            if isinstance(rwr_data_list, list):#check if the evaluated data is a list or not
                RWR_coordinates_list.append(rwr_data_list)# appends the data to the respective array
            else:
                print("Invalid data format received from RWR client.")
        except Exception as e:
            pass
# Listens for data from the RADAR client
def listen_for_data_radar(radar_client):
    while True:
        message_from_radar = radar_client.recv(2048).decode()#decodes the data
        try:
            radar_data_list = eval(message_from_radar.replace("(", "[").replace(")", "]"))
            if isinstance(radar_data_list, list):#check if the data is a list or not
                RADAR_coordinates_list.append(radar_data_list)# appends it to the respective array
            else:
                print("Invalid data format received from RADAR client.")
        except Exception as e:
            pass

# Method to view the data in the file
def showdata():
    file = "data.xlsx"
    while True:
        command = input("Enter 'showdata' to view data: ").lower()
        if command == "showdata_rwr":# To view the RWR coordinates
            index_rwr = np.arange(1,len(RWR_coordinates_list)+1)
            df_rwr_pos = pd.Series(RWR_coordinates_list,index_rwr)
            print(df_rwr_pos)
        if command == "showdata_radar":# To view the RADAR coordinates
            index_radar = np.arange(1,len(RADAR_coordinates_list)+1)
            df_radar_pos = pd.Series(RADAR_coordinates_list,index_radar)
            print(df_radar_pos)
        if command =="showdata_dmoniter":#To view the Distance between RWR and RADRAR calculated by the moniter
            index_d_moninter = np.arange(1,len(distance_list_moniter)+1)
            df_d_moniter = pd.Series(distance_list_moniter,index_d_moninter)
            print(df_d_moniter)
        if command == "save_data":
            frame = {'radar Pos':df_radar_pos,'rwr Pos':df_rwr_pos,'moniter_calculated_distance':df_d_moniter}
            df = pd.DataFrame(frame)
            df.to_excel(file,index=False)
            print(f"saved the data in {file}")

# function to plot and continuesly update the plot on receiving data
def update_plot():
    while True:
        if len(RWR_coordinates_list) > 0 and len(RADAR_coordinates_list) > 0:
            rwr_lat, rwr_lon = RWR_coordinates_list[-1]  # Latest RWR coordinates
            radar_lat, radar_lon = RADAR_coordinates_list[-1]  # Latest radar coordinates
            distance_moniter = haversine(rwr_lat, rwr_lon, radar_lat, radar_lon)
            distance_list_moniter.append(distance_moniter)#appends the distance list
            time_list.append(len(distance_list_moniter)+1)# creating a artificial time for 1 second
            plt.plot(time_list, distance_list_moniter, color='g', label="Calculated by moniter")# ploting the graph
            plt.xlabel('Time')
            plt.ylabel('Distance (km)')
            plt.title('Distance between RWR and RADAR over time')
            plt.draw()
            plt.pause(0.1)
        time.sleep(1)
# main server funtion that handles the connection with the clients and data transmission process
def server_main():
    server = socket.socket()
    server.bind((IP, PORT)) #binds the IP and PORT
    print("[SERVER] Ready to make connections")
    # seperate thread for running the update_plot function parallely
    update_plot_thread = threading.Thread(target=update_plot)
    update_plot_thread.start()
    # Start the showdata thread earlier
    showdata_thread = threading.Thread(target=showdata)
    showdata_thread.start()
    

    while True:
        server.listen(5) # listening for clients
        rwr_client, rwr_addr = server.accept()
        print(rwr_client, rwr_addr)
        username = rwr_client.recv(1024).decode() #recv the username from the RWR client
        print(f"connected with {username}")

        radar_client, radar_addr = server.accept()
        print(radar_client, radar_addr)
        username = radar_client.recv(1024).decode() #recv the username from the RADAR client
        print(f"connected with {username}")
        Radar_Data = radar_client.recv(2048).decode() #recv the basic RADAR data from the RADAR client 
        print(Radar_Data)
        #seperate thread for the listening the data from RWR and RADAR clients
        rwr_data = threading.Thread(target=listen_for_data_rwr, args=(rwr_client,))
        radar_data = threading.Thread(target=listen_for_data_radar, args=(radar_client,))
        rwr_data.start()
        radar_data.start()

if __name__== "__main__":
    plt.ion()  # Turn on interactive mode for matplotlib
    server_main()# calling the main server function