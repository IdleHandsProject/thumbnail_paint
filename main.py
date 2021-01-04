import os
import sys
import requests
#import argparse
from urllib.parse import urlparse, urlencode, parse_qs
from youtube.video_comments import VideoComment
from time import sleep, time, asctime
from PIL import Image, ImageDraw, ImageFont, ImageTk
from clients.youtube_client import YouTubeClient
import datetime
import tkinter
import RPi.GPIO as GPIO

apikey = #REPLACE WITH YOUR API KEY
videolink = #REPLACE WITH YOUR VIDEO LINK e.g. "FV2OqOJcQRc"

numComments = 100
commentMaxPages = 1
commentsPerPage = 100
totalPixels = 64

IMAGE_INPUT_FILE = './draw_this_thumbnail.png'
IMAGE_BLANK_FILE = './blank.png'
IMAGE_CANVAS_FILE = './canvas.png'
IMAGE_FRAME_FILE = './frame.png'
IMAGE_OUTPUT_FILE = './draw_this_thumbnail.png'
IMAGE_UPLOAD = './thumbnail.png'
OPENSANS_FONT_FILE = './fonts/OpenSans-ExtraBold.ttf'
YOUTUBE_DATA_API_CREDENTIALS_LOCATION = './creds/client_secret.json'

YOUTUBE_VIDEO_ID = #REPLACE WITH YOUR VIDEO LINK e.g. "FV2OqOJcQRc"


def get_time():
    print("Getting time")
    ctime = asctime()
    return ctime


def create_thumbnail(pixel_list):
    print("Creating the thumbnail")
    image = Image.open(IMAGE_BLANK_FILE)
    canvas = Image.open(IMAGE_CANVAS_FILE)

    for px in range(0,numComments*totalPixels,5):
        x = pixel_list[px]
        y = pixel_list[px+1]
        r = pixel_list[px+2]
        g = pixel_list[px+3]
        b = pixel_list[px+4]
        if((x+y) > 0):
            #print("Trying: ", x, y, r, g, b)
            try:
                canvas.putpixel((x,y),(r,g,b))
                pixel_list[px] = 0
                pixel_list[px+1] = 0
                pixel_list[px+2] = 0
                pixel_list[px+3] = 0
                pixel_list[px+4] = 0
            except:
                print("Bad Input")
    canvas.save(IMAGE_CANVAS_FILE)
    image.paste(canvas, (18,113))
    frame = Image.open(IMAGE_FRAME_FILE)
    image.paste(frame, (0,0), frame)
    image.save(IMAGE_OUTPUT_FILE)
    filename = ("./archive/thumbnail_" + datetime.datetime.now().replace(microsecond=0).isoformat() + ".png")
    image.save(filename, "PNG", quality=100)
    image.save(IMAGE_UPLOAD, "PNG", quality=100)
    print(asctime(),f"Successfully generated the image and saved to {IMAGE_UPLOAD}")


def set_thumbnail_for_youtube_video(video_id, thumbnail):
    youtube_client = YouTubeClient(YOUTUBE_DATA_API_CREDENTIALS_LOCATION)
    response = youtube_client.set_thumbnail(video_id, thumbnail)
    print(response)


def get_pixel_list():
    vc = VideoComment(commentsPerPage, videolink, apikey)
    pixel_list = vc.get_video_comments()
    #print("The Next Move:", chosen_move)
    return(pixel_list)
    
def send_thumbnail(pixel_list):
    # Upload that thumbnail to your YouTube video
    if (GPIO.input(17) == 0):
        set_thumbnail_for_youtube_video(YOUTUBE_VIDEO_ID, IMAGE_UPLOAD)
    else:
        print("Emergency Stop Depressed")
    
def showPIL(pilImage, sleepTime):
    showImage = Image.open(pilImage) 
    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()    
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
    canvas = tkinter.Canvas(root,width=w,height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight = showImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        showImage = showImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(showImage)
    imagesprite = canvas.create_image(w/2,h/2,image=image) 
    root.after(sleepTime, root.destroy)
    root.mainloop()
    showImage.close()



GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
commentWaitTime = time()
uploadWaitTime = time()
list_of_pixels = get_pixel_list()
not_all_zeros = list_of_pixels.any()
if(not_all_zeros):
    create_thumbnail(list_of_pixels)
    send_thumbnail(list_of_pixels)
else:
    print(asctime(), "No New Comments/Data")
 
showPIL(IMAGE_UPLOAD,15000)
run = 1

uploadFlag = 0
while(run==1):
    try:
        if (int(time() - commentWaitTime) > 60):
            print(asctime(),"Collecting Comments")
            list_of_pixels = get_pixel_list()
            not_all_zeros = list_of_pixels.any()
            if(not_all_zeros):
                create_thumbnail(list_of_pixels)
                showPIL(IMAGE_UPLOAD,15000)   
                uploadFlag = 1
            commentWaitTime = time()
        if (int(time() - uploadWaitTime) > 300):
            if(uploadFlag == 1):
                print("----------Uploading Image------------")
                print("----------Uploading Image------------")
                print("----------Uploading Image------------")
                sleep(5)
                showPIL(IMAGE_UPLOAD,15000) 
                send_thumbnail(list_of_pixels)                
                uploadFlag = 0
            else:
                print(asctime(),"No New Pixels")
            uploadWaitTime = time()       
            
    except:
        run = 0