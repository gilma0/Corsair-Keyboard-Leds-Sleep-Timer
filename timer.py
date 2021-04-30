#Created by Gil Matsliah a.k.a gilma0
from ctypes import Structure, windll, c_uint, sizeof, byref
from cuesdk import CueSdk
import threading
import time
from tkinter import *

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]

flag = True

def start_click():
    global button_text
    entered_minutes = float(textEntry.get())*60
    timer = threading.Thread(target=main, args=(entered_minutes, ))
    timer.start()

def stop_click():
    global flag
    global button_text
    flag = False
    button_text = "Start"

def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0

def get_available_leds():
    leds = list()
    device_count = sdk.get_device_count()
    for device_index in range(device_count):
        led_positions = sdk.get_led_positions_by_device_index(device_index)
        leds.append(led_positions)
    return leds


def turnOnLeds(all_leds):
    print("turn on")
    cnt = len(all_leds)
    for di in range(cnt):
        device_leds = all_leds[di]
        for led in device_leds:
            device_leds[led] = (255, 0, 0)
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()

def turnOffLeds(all_leds):
    print("turn off")
    cnt = len(all_leds)
    for di in range(cnt):
        device_leds = all_leds[di]
        for led in device_leds:
            device_leds[led] = (0, 0, 0)
        sdk.set_led_colors_buffer_by_device_index(di, device_leds)
    sdk.set_led_colors_flush_buffer()

def main(secs):
    global sdk
    global flag
    sdk = CueSdk()
    connected = sdk.connect()
    print(sdk.protocol_details)
    print(sdk.get_devices())
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

    colors = get_available_leds()
    if not colors:
        print("Leds not available")
        return
    print("keyboard lights will shutdown after: " + str(secs/60) + " minutes")
    print("Checking idle")
    turnOnLeds(colors)
    while True and flag == True:
        idle = get_idle_duration()
        #print(idle)
        if idle > secs:
            #checking current led color to prevent keyboard spamming
            if colors[0][14] == (255, 0, 0):
                turnOffLeds(colors)
        elif colors[0][14] == (0, 0, 0):
                turnOnLeds(colors)
        time.sleep(0.1)
    print("stopped by click")
    flag = True


if __name__ == "__main__":
    #main(300) #change to how many seconds until leds shuts off
    window = Tk()
    window.title("Corsair Led Sleep Timer")
    window.configure(background="black")
    Label(window, text="  ", bg="black").grid(row=0, column=0)
    Label(window, text="  ", bg="black").grid(row=0, column=3)
    Label(window, text="\nCorsair Sleep Timer\nCreated by Gil Matsliah\n\nAlso Known as gilma0\n", bg="black", fg="white", font="none 18 bold").grid(row=0,column = 1, columnspan = 2, sticky=E)
    Label(window, text="Minutes to shut off:", bg="black", fg="white", font="none 12 bold").grid(row=1, column=1, sticky=W)
    textEntry = Entry(window, width=15, bg="white", text="5")
    textEntry.grid(row=1, column=2, sticky=W)
    textEntry.insert(END, "5")
    Label(window, text="", bg="black").grid(row=2)
    Button(window, text="Start", width=5, command=start_click).grid(row=3, column=1, sticky=N)
    Button(window, text="Stop", width=5, command=stop_click).grid(row=3, column=2, sticky=W)
    Label(window, text="\n", bg="black").grid(row=4)
    window.mainloop()