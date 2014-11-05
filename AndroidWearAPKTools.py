from Tkinter import *
from tkFileDialog import *
import tkMessageBox
import os
import subprocess
from threading import Thread

def queue(event_queue):
    for i in event_queue:
        i()
    if len(event_queue):
        fileLabel.set(" ")
        event_queue = []
    root.after(1000,queue,event_queue)

def run(command):
    return subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.readlines()

def data():
    for i in range(50):
       Button(frame, text=i, command = None).grid(row=i, column=0)

def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),width=250,height=200)

def showErrorMessage():
    tkMessageBox.showerror("ERROR","Could not install / uninstall app!")

def showSuccessMessage():
    addScrollFrame()
    tkMessageBox.showinfo("Success!","Success!")

def connectToWatchCallback():
    global connected
    result = run('adb devices')
    if len(result[1]) < 5:
        tkMessageBox.showerror("ADB ERROR","ADB was unable to connect to your watch. Please ensure that the watch is attached and ADB Debugging is enabled.")
    elif "offline" in result[1]:
        tkMessageBox.showerror("ADB ERROR","The device is offline. Try unplugging and replugging.")
    else:
        tkMessageBox.showinfo("Success!","ADB successfully connected to your watch.")
        addScrollFrame()
        connected = True

def install(filename):
    fileLabel.set("Installing app, please wait...")
    output = run('adb install "%s"'%filename)
    if "Success" in output[1]:
        print "Success!"
        event_queue.append(showSuccessMessage)
    else:
        event_queue.append(showErrorMessage)

def uninstallInBackground(package):
    fileLabel.set("Uninstalling app, please wait...")
    output = run("adb uninstall " + package)
    if "Success" in output[0]:
        event_queue.append(showSuccessMessage)
    else:
        event_queue.append(showErrorMessage)

def openfileCallback():
    if connected:
        filename = askopenfilename(parent=root,filetypes=[('APK Files', '.apk')])
        if filename:
            #thread.start_new_thread(install,(filename,))
            basename = os.path.basename(filename)
            print filename
            if tkMessageBox.askokcancel("Install App?","Are you sure you want to install %s?\nNote: This will take a few seconds."%basename):
                t = Thread(target=install, args=[filename])
                t.start()
    else:
        tkMessageBox.showerror("Error","You must connect to the watch first!")

def uninstall(package):
    if tkMessageBox.askokcancel("Uninstall App?","Are you sure you want to uninstall %s?\nNote: This will take a few seconds."%package):
        t = Thread(target=uninstallInBackground, args=[package])
        t.start()

def addUninstallButtons():
    getAppsCommand = "adb shell pm list packages"
    appsList = run(getAppsCommand)
    print appsList
    appsList = [i[8:-3] for i in appsList if ("com.example" not in i and "com.google" not in i and "com.android" not in i)]
    print appsList
    for x,i in enumerate(appsList):
        Button(frame, text=i, command = lambda j=i: uninstall(j)).grid(row=x, sticky=W)

def uninstallButtonCallback():
    if not connected:
        tkMessageBox.showerror("Error","You must connect to the watch first!")
    else:
        addScrollFrame()

def addScrollFrame():
    global frame,myframe,canvas,myscrollbar
    root.wm_geometry("%dx%d+%d+%d" % (sizex, 325, posx, posy))
    myframe=Frame(root,relief=GROOVE,width=50,height=100,bd=1)
    myframe.place(x=60,y=85)
    canvas=Canvas(myframe)
    frame=Frame(canvas)
    myscrollbar=Scrollbar(myframe,orient="vertical",command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)

    myscrollbar.pack(side="right",fill="y")
    canvas.pack(side="left")
    canvas.create_window((0,0),window=frame,anchor='nw')
    frame.bind("<Configure>",myfunction)
    addUninstallButtons()

connected = False
root=Tk()

sizex = 400
sizey = 100 #350
posx  = 400
posy  = 200
root.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))
root.wm_title("Android Wear APK Tools")

event_queue = []

fileLabel = StringVar()
Label(root, textvariable=fileLabel).pack()
fileLabel.set(" ")

connectToWatch = Button(root,text="Connect To Watch", command = connectToWatchCallback)
openfile = Button(root, text ="Install an app", command = openfileCallback)
uninstallButton = Button(root, text ="Uninstall an app", command = uninstallButtonCallback)

connectToWatch.pack()
openfile.pack()
#uninstallButton.pack()

queue(event_queue)
root.mainloop()