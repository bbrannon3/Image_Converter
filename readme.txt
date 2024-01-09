Instructions:
    FIRST TIME ONLY - Make sure Python is installed
    FIRST TIME ONLY - Run pip install pillow pillow-heif customtkinter ttkbootstrap packaging    
    Run python Img_Convert.py 
    Browse to the top directory containing the files you wish to convert.
    Enter the file extension you wish to convert FROM.
    Enter the file extension you wish to convert TO.
    Press the Start Button in the upper right of the window.
    Viola your files have been converted. 
    -Love Brody <3

WARNING: This will attempt to convert/delete all files in the given directory and all subdirectories into the given type. Be careful where you run this.

Options:
    Convert Files InPlace - Places Converted Files in the same Directory as the Original Files.

    Retain Original File Structure - If enabled and when not converting InPlace, places the converted files into a copy of the folder structure. Otherwise all files will be placed in the "ConvertedFiles" directory.

    Delete Original(s) - If Enabled, Deletes the Original Files after conversion is complete.

    Create Web Optimized Copies - ONLY FOR CONVERTING TO JPEG FILES, When enabled creates an additional file that has been compressed for usage on the web. Use the Quality Retention Rate Slider to change how agressive the compression is.

    Delete Meta File(s) - If Enabled Deletes ".MOV", ".plist", and ".aae" files to reduce disk usage.