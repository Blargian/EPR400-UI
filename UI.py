import serial
import time
import tkinter as tk
import threading 
import queue

#global variables
ser = None;
root = tk.Tk()
root.title("Wax Printer v1.0")
filter_temperature = ''
serial_data = ''
update_period =5 

#Importing of Gcode file:
def importGcode():

    def file_read(fileName):
        with open(fileName) as f:
            content_list = f.readlines()
            return content_list

    fileContents = file_read("SpecificationDesign.ngc")

    #remove spaces and line returns from .ngf file
    fileContents = [i.replace(' ','') for i in fileContents]
    fileContents = [i.replace('\n','') for i in fileContents]

    startIndex = fileContents.index("F400")
    fileContents = fileContents[startIndex+1:]

    endIndex = fileContents.index("F0") #get the index of the F0 stop command 
    fileContents = fileContents[:endIndex+1] #remove everything after that stop command

    print(fileContents)
    #Make sure that X, Y, I and J start with + or - 

    def addPositiveSign(item):
        for char in 'XYIJ':
            item = item.replace(char,f'{char}+')
        return item.replace('+-','-')

    fileContents = [addPositiveSign(item) for item in fileContents]

    print(fileContents)
    #Format each command to a 32 byte string
    for i, s in enumerate(fileContents):
        fileContents[i] =s.ljust(32,'#')

    print("got to Gcode")
    for i in fileContents:
        print(i)
        send(format(('{}').format(i)).encode('ascii'))

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
            serial_Data = ser.readline().decode()

            if(serial_Data.startswith('T') and len(serial_Data)!=0):
                filter_temperature = serial_Data
                filter_temperature = filter_temperature[1:]
                print(filter_temperature)
        except TypeError:
            pass

def update_gui():

    global filter_temperature
    global update_period

    #put your stuff here, things that need updating
    new = time.time()

    while(1):
        
        temperatureLabel.configure(text=filter_temperature).place(x=50,y=30)

        if time.time() - new >= update_period:
            new = time.time()

def send(send_data):

    if not send_data:
        print("Sent nothing")

    sent = ser.write(send_data)
    print(sent)

def disconnect():

    try:
        ser.close()
    except AttributeError:
        print("closed without using")

    root.quit()

def startHeating():
    command = "heat".ljust(32,'#')
    send(format(('{}').format(command)).encode('ascii'))
    print("reached heating")


def homeX():
    command = "homx".ljust(32,'#')
    send(format(('{}').format(command)).encode('ascii'))
    print("sent homx command")


def homeY():
    command = "homy".ljust(32,'#')
    send(format(('{}').format(command)).encode('ascii'))
    print("sent homy command")
       
if __name__ == "__main__":
    #put your widget placements here
    ### WIDGETS ###

    startButton = tk.Button(text="Start",command=importGcode).place(x=10, y=10)
    heatButton = tk.Button(text="Heat",command=startHeating).place(x=50, y=10)
    homeXButton = tk.Button(text="Home X",command=homeX).place(x=200, y=10)
    homeYButton = tk.Button(text="Home Y",command=homeY).place(x=200, y=40)

    tempVal = tk.StringVar()
    temperatureLabel = tk.Label(text="Temp(degC):",textvariable = tempVal).place(x=50,y=30)

    ### WIDGETS END ###

    guiThread = threading.Thread(target = update_gui)
    guiThread.daemon = True
    guiThread.start()

    root.geometry("480x320")
    connect()
    root.mainloop()
