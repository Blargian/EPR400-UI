import serial
import time
import tkinter as tk
import threading 
import queue

#global variables
ser = None;
root = tk.Tk()
root.title("Wax Printer V1")
filter_data = ''
serial_data = ''
update_period =5 

#Importing of Gcode file:
def importGcode():

    def file_read(fileName):
        with open(fileName) as f:
            content_list = f.readlines()
            return content_list

    fileContents = file_read("SpecificationDesign.ngc")
    fileContents = fileContents[18:] #remove the fluff generated by dxf2gcode

    #remove spaces and line returns from .ngf file
    fileContents = [i.replace(' ','') for i in fileContents]
    fileContents = [i.replace('\n','') for i in fileContents]

    endIndex = fileContents.index("F0") #get the index of the F0 stop command 
    fileContents = fileContents[:endIndex+1] #remove everything after that stop command

    #Format each command to a 32 bit string
    for i, s in enumerate(fileContents):
        fileContents[i] =s.ljust(32,'\0')

    print("got to Gcode")
    for i in fileContents:
        print(i)
        send(format(('{}\n').format(i)).encode('ascii'))

#Makes a serial connection, stars it in a new thread so as not to hang the GUI
def connect():

    global ser
    port = 'COM8'
    baud = 115200
    bytes =8
    time=2

    ser = serial.Serial(port=port,baudrate =baud,bytesize=bytes,timeout=time,stopbits=serial.STOPBITS_ONE,parity=serial.PARITY_NONE)

    serialThread = threading.Thread(target=get_data)
    serialThread.daemon = True
    serialThread.start()

def get_data():

    global ser
    global filter_data

    while True:
        try:
            serial_Data = ser.readline().strip('\n').strip('\r')
            filter_data = serial_Data
        except TypeError:
            pass

def update_gui():

    global filter_data
    global update_period

    #put your stuff here, things that need updating

def send(send_data):

    if not send_data:
        print("Sent nothing")

    ser.write(send_data)

def disconnect():

    try:
        ser.close()
    except AttributeError:
        print("closed without using")

    root.quit()

def startHeating():
    send(format(('{}\n').format("heat")).encode('ascii'))
    print("reached heating")
       
if __name__ == "__main__":
    #put your widget placements here
    ### WIDGETS ###

    startButton = tk.Button(text="Start",command=importGcode).place(x=10, y=10)
    heatButton = tk.Button(text="Heat",command=startHeating).place(x=50, y=10)

    temperature = tk.Label(text="Temp:").place(x=50,y=35)

    ### WIDGETS END ###

    guiThread = threading.Thread(target = update_gui)
    guiThread.daemon = True
    guiThread.start()

    root.geometry("480x320")
    connect()
    root.mainloop()
