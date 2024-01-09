import os
import glob
import re
import concurrent.futures
from PIL import Image
from pillow_heif import register_heif_opener
import tkinter as tk
from tkinter import filedialog
import customtkinter
import time
import ttkbootstrap as ttk

# Registering Extra File Formats 
register_heif_opener()
unsupportedSaveTypes = ["heic"]
unsupportedOpenTypes = []
supportedFileTypes = ["heic","jpeg", "png", "gif"]
file_extensions_to_delete = ["MOV", "plist", "mov", "aae"]

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_selected)

def on_slider_change(t):
    result_label.configure(text=f"Quality Retention Rate: {slider_var.get()}")     

filesSaved = 0
totalFiles = 0

def SaveFile(files, to, cwd, inPlace, retainStructure, isJpeg, quality, ext, toDel, webOp):
    replace = re.compile(re.escape(ext), re.IGNORECASE)
    print(cwd+"\\" + files + " being Converted")
    image_file = Image.open(cwd +"\\" + files)    
    newFileName = replace.sub(to, files.replace("*\\",""))
    filePath = cwd[0:cwd.__len__()]
    if(not inPlace):
        pathAddition = "\\ConvertedPhotos\\"
        if(newFileName.find('\\')>-1):
            if(retainStructure):
                pathAddition = pathAddition + newFileName[0:newFileName.rfind('\\')]

            newFileName = newFileName.removeprefix(newFileName[0:newFileName.rfind('\\')])        
        filePath = filePath + pathAddition
    else:
        if(not filePath.endswith('\\')):
            filePath = filePath + "\\" 


    if(cwd != filePath):
        os.makedirs(filePath, exist_ok=True)        
        print(filePath + " - Directory Already Exists")

    if(isJpeg):
        image_file.save(filePath + newFileName, quality=95,format=to)
        if(webOp):
            # TODO: Add Way of Saving Web Optimized Photos to Mirror Directory
            image_file.save(replace.sub('', (filePath + newFileName.replace("."+to, "_Web."+to)).replace("*\\", ""))+'.'+to, quality=quality, format=to, dpi=(72, 72))
    else:
        image_file.save(newFileName, format=to)

    if(toDel):
        DeleteFile(cwd, files)

    
def DeleteFile(cwd, file):
    os.remove(cwd +"\\"+ file.replace("*\\", ""))


def StartConsole():
    # Get Directory to work from
    cwd = input("Please Enter the path of the directory you would like to start from (blank for current): ")
    if(cwd.strip() == ""):
        cwd = os.getcwd()
        print("Using: ", cwd)

    # Get MIME Type to Convert From
    ext = input("Please Enter Your Image Extension Type to convert from (ex - gif, png, heic, jpeg): ")
    while ext in unsupportedOpenTypes:
        ext = input("Please Enter a supported Extension Type to convert From (ex - gif, png, jpeg): ")

    # Get MIME Type to Convert To
    to = input("Please Enter Your Image Extension Type to convert to (ex - gif, png, jpeg): ")
    while to.lower() in unsupportedSaveTypes:
        to = input("Please Enter a supported Extension Type to convert to (ex - gif, png, jpeg): ")

    # Get Options
    delete = input("Would you like to delete the original(s)? (y/n): ")
    toDel = delete.lower()[0] == 'y'

    inPlace = input("Would you like to convert the files in place? (y/n): ").lower()[0] == 'y'
    retainStructure = False
    if(not inPlace):
        retainStructure = input("Would you like to retain the file structure? (y/n): ").lower()[0] == 'y'

    isJpeg = to.lower() == "jpeg" or to.lower() == "jpg"
    webOp = False
    quality = 60
    if(isJpeg):
        webOp = input("Would you like to create web optimized copies? (y/n) ").lower()[0] == 'y'
        if(webOp):
            potential = input("Set the quality retention rate (20-95, lower = smaller, leave blank for default): ")

            while(potential.strip() != "" and not potential.isnumeric()):
                potential = input("Please put a valid value for quality(20-95) or leave blank for default: ")

            if(potential.strip() != ""):
                quality = potential
    
    MainFunctionLoop(cwd, ext, to, inPlace, retainStructure, isJpeg, quality, toDel, webOp)
   

            
def GetFileSet(cwd, ext):
    f = glob.glob("**\*."+ext, root_dir=cwd, recursive=True)
    #fileset = {file.replace(cwd + "\\", '')for file in f}
    return f

def MainFunctionLoop(cwd, ext, to, inPlace, retainStructure, isJpeg, quality, toDel, webOp, delMov):
    # Find and Trim File Paths
    fileset = GetFileSet(cwd, ext)
    delSet = []
    if(delMov):
        for type in file_extensions_to_delete:
            delSet.extend(GetFileSet(cwd, type))
        print(delSet)

    totalFiles = len(fileset) + len(delSet)

    print("Found " + (totalFiles).__str__() + " Files")

       
    if(totalFiles != 0):
        # Creating Thread Pool and using it to save parallelly(ish)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            futures = []
                    
            for file in fileset:         
                future =  pool.submit(SaveFile, file, to, cwd, inPlace, retainStructure, isJpeg, quality, ext, toDel, webOp)         
                futures.append(future)  
            

            for file in delSet:
                future = pool.submit(DeleteFile, cwd, file)
                futures.append(future)

            #print(len(futures))
            cur = 0
            while len(futures) > 0:
                #print("Threads Allocated "+str(len(futures)))
                for future in futures:
                    if(future.done()):
                        #print("Removing Thread")
                        futures.remove(future)
                        cur = cur + 1
                        file_saved(cur, totalFiles)
                time.sleep(.01)
        print(totalFiles.__str__() + " Files Converted")
    else:
        BuildUi(0)
    
def file_saved(cur, total):  
    print("Files Saved: "+str(cur)+" Total Files "+str(total))
    if(cur != 0 and cur == total):
        BuildUi(total)
        
    else:
        progress_var.set(cur/total)
        progress_bar.update()
        root.update()
    
def BuildUi(convertedAmount = -1):
    #print("Building UI")
    if(convertedAmount > -1):
        postProcessing_label = ttk.Label(root, text= convertedAmount.__str__() + " - files converted")
        postProcessing_label.grid(row=0, column=1, columnspan=1, padx=10, pady=10)

    folder_label.grid(row=0, column=0, columnspan=1, padx=10, pady=0, sticky='w')
    start_button.grid(row=0, column=2, columnspan=1, padx=10, pady=10)

    folder_entry.grid(row=1, column=0, columnspan=1, padx=10, pady=10, sticky="ew")
    browse_button.grid(row=1, column=1, columnspan=1, padx=0, pady=10) 

    combo_label.grid(row=2, column=0, columnspan=1, padx=5, pady=5)  
    combo.grid(row=2, column=1, columnspan=1, padx=5, pady=5)    

    combo_label2.grid(row=3, column=0, columnspan=1, padx=5, pady=5)    
    combo2.grid(row=3, column=1, columnspan=1, padx=5, pady=5)

    inPlace_Box.grid(row=5, column=0, columnspan=1, padx=10, pady=10)
    retain_Box.grid(row=5, column=1, columnspan=1, padx=10, pady=10)
    del_box.grid(row=5, column=2, columnspan=1, padx=10, pady=10)
    
    op_box.grid(row=6, column=0, columnspan=1, padx=10, pady=10)
    delMov_box.grid(row=6, column=1, columnspan=1, padx=10, pady=10)
    result_label.grid(row=6, column=2, columnspan=1, padx=10, pady=10)  
    
    slider.grid(row=7, column=2, columnspan=1, padx=10, pady=10)
     
    processing_label.grid_remove()
    progress_bar.grid_remove()
    root.update()


def HideUi():
    #print("Hiding UI")
    inPlace_Box.grid_remove()
    folder_label.grid_remove()
    result_label.grid_remove()
    slider.grid_remove()
    op_box.grid_remove()
    del_box.grid_remove()
    retain_Box.grid_remove()
    combo2.grid_remove()
    combo_label2.grid_remove()
    combo.grid_remove()
    combo_label.grid_remove()
    start_button.grid_remove()
    browse_button.grid_remove()
    folder_entry.grid_remove()
    delMov_box.grid_remove()
    processing_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    progress_bar.grid(row=2, column=0, columnspan=2, padx=100, pady=10)
    progress_var.set(0)

    root.update()
    


def start_process():
    # Your code to perform the desired action with the selected folder and items.
    #print("Starting")
    if(folder_entry.get() != "" and ((ext.get() != "" and to.get() != "") or delMov.get())):
        HideUi()    
        MainFunctionLoop(folder_entry.get(), ext.get(), to.get(), inPlace.get(), retainStructure.get(), to.get()=="jpeg", slider_var.get(), toDel.get(), webOp.get(), delMov.get())
   
#def gui_Process():
#Create the main window
root = ttk.Window()
#root.geometry("720x480")
root.title("Image Converter")

ext = customtkinter.StringVar()
inPlace = customtkinter.BooleanVar()
to = customtkinter.StringVar()
retainStructure = customtkinter.BooleanVar()
toDel = customtkinter.BooleanVar()
webOp = customtkinter.BooleanVar()
slider_var = customtkinter.IntVar()
slider_var.set(60)
progress_var = ttk.IntVar()
progress_var.set(0)
delMov = ttk.BooleanVar()

#Create a label and entry widget for folder selection
folder_label = ttk.Label(root, text="Select a Folder:")
folder_entry = ttk.Entry(root, width=20)
browse_button = ttk.Button(root, text="Browse", command=browse_folder)
# Create buttons for moving items and starting the process
start_button = ttk.Button(root, text="Start", command=start_process)
# Create a combobox (drop-down list)
combo_label = ttk.Label(root, text="Select Extension to Convert From:")
combo = ttk.Combobox(root, textvariable=ext, values=supportedFileTypes)
combo_label2 = ttk.Label(root, text="Select Extension to Convert To:")
combo2 = ttk.Combobox(root, textvariable=to, values=supportedFileTypes)
# Create a checkbox    
inPlace_Box = ttk.Checkbutton(root, text="Convert Files InPlace", variable=inPlace)
retain_Box = ttk.Checkbutton(root, text="Retain Original File Structure", variable=retainStructure)
del_box = ttk.Checkbutton(root, text="Delete Original(s)", variable=toDel)
delMov_box = ttk.Checkbutton(root, text="Delete Meta File(s)", variable=delMov)
op_box = ttk.Checkbutton(root, text="Create Web Optimized Copies", variable=webOp)
# Create a slider with a default value of 60       
slider = ttk.Scale(root, from_=20, to=95, variable=slider_var,length=190, orient=ttk.HORIZONTAL, command=on_slider_change)
# Create a label to display the selected value
result_label = ttk.Label(root, text=f"Quality Retention Rate: {slider_var.get()}")
# Display a processing message
processing_label = ttk.Label(root, text="Processing your request...")
progress_bar = ttk.Progressbar(root,length=250, maximum=1, variable=progress_var)

postProcessing_label = ttk.Label(root, text="0 - files converted")

BuildUi()

root.mainloop()

