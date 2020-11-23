import serial
import time
import tkinter as tk
import threading 
import queue
from tkinter import filedialog

#global variables
ser = None;
root = tk.Tk()
root.title("Wax Printer v1.0")
filter_temperature = ''
serial_data = ''
update_period =5 
filename = ''

#Importing of Gcode file:
def importGcode(fileToRead):

    def file_read(fileName):
        with open(fileName) as f:
            content_list = f.readlines()
            return content_list

    fileContents = file_read(fileToRead)

    #remove spaces and line returns from .ngf file
    fileContents = [i.replace(' ','') for i in fileContents]
    fileContents = [i.replace('\n','') for i in fileContents]

    startIndex = fileContents.index("F400")
    fileContents = fileContents[startIndex+1:]

    endIndex = fileContents.index("F0") #get the index of the F0 stop command 
    fileContents = fileContents[:endIndex+1] #remove everything after that stop command

    print(fileContents)
    #Make sure that X, Y, I and J start with + or - 

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
    port = 'COM4'
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
            serial_Data = ser.readline().decode(errors='replace')
            if(serial_Data.startswith('W') and len(serial_Data)!=0):
                tempVal.set(serial_Data[1:])
                print(tempVal.get())

            elif(serial_Data.startswith('B') and len(serial_Data)!=0):
                tempValBed.set(serial_Data[1:])
            else:
                tempVal.set("--")
                tempValBed.set("--")
        except TypeError:
            pass

def update_gui():

    global filter_temperature
    global update_period

    #put your stuff here, things that need updating
    new = time.time()

    while(1):

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

def homeZ():
    command = "homz".ljust(32,'#')
    send(format(('{}').format(command)).encode('ascii'))
    print("sent homz command")

def drawWax():
    command = "draw".ljust(32,'#')
    send(format(('{}').format(command)).encode('ascii'))
    print("sent drawWax command")

def stepZUp():
    command = "movz+".ljust(32,'#')
    send(format(('{}').format(command)).encode('ascii'))
    print("sent move Z up")

def stepZDown():
    command = "movz-".ljust(32,'#')
    send(format(('{}').format(command)).encode('ascii'))
    print("sent move Z down")

def spec1():
    command = "spec1".ljust(32,'#')
    send(format(('{}').format(command)).encode('ascii'))
    print("sent spec1")

def bed():
    command = "bed".ljust(32,'#')
    send(format(('{}').format(command)).encode('ascii'))
    print("sent bed")
       
def browseFiles():
    global filename
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select a file", filetypes=(("ngc files", "*.ngc"),("all files", "*.*")))
if __name__ == "__main__":
    #put your widget placements here
    ### WIDGETS ###

    guiThread = threading.Thread(target = update_gui)
    guiThread.daemon = True
    guiThread.start()

    startButton = tk.Button(text="Print",command=lambda: importGcode(filename))
    startButton.place(x=70, y=10)
    browseButton = tk.Button(text="Browse",command=browseFiles)
    browseButton.place(x=10, y=10)
    heatButton = tk.Button(text="Heat Wax",command=startHeating,activebackground='green').place(x=120, y=10)
    homeXButton = tk.Button(text="Home X",command=homeX).place(x=200, y=10)
    homeYButton = tk.Button(text="Home Y",command=homeY).place(x=200, y=40)
    homeZButton = tk.Button(text="Home Z",command=homeZ).place(x=200, y=70)
    drawWax = tk.Button(text="Draw Wax",command=drawWax).place(x=300, y=10)
    bedHeater = tk.Button(text="Heat bed",command=bed).place(x=10, y=70)

    # spec1Button = tk.Button(text="Specification 1",command=spec1).place(x=300, y=100)
    # spec2Button = tk.Button(text="Specification 2",command=drawWax).place(x=300, y=140)
    # spec3Button = tk.Button(text="Specification 3",command=drawWax).place(x=300, y=180)

    zDown = tk.Button(text="+1",command=stepZUp)
    zDown.place(x=380, y=10)
    zUP = tk.Button(text="-1",command=stepZDown)
    zUP.place(x=380, y=40)

    tempVal = tk.StringVar()
    temperatureLabel = tk.Label(text="Temp:        / 80").place(x=10, y=40)
    temperatureValueLabel = tk.Label(textvariable=tempVal).place(x=50, y=40)

    tempValBed = tk.StringVar()
    bedTemperatureLabel = tk.Label(text="Temp:        / 60").place(x=10, y=110)
    bedTemperatureValueLabel = tk.Label(textvariable=tempValBed).place(x=50, y=110)

    ### WIDGETS END ###

    root.geometry("480x320")
    connect()
    root.mainloop()
