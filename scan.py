#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# Source: https://github.com/Starwhooper/RPi-docscan

#######################################################
#
# Prepare
#
#######################################################

# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time
import os
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont,ImageColor
import requests
import json
import sys
from PyPDF2 import PdfFileMerger

##### import config.json
try:
 with open(os.path.split(os.path.abspath(__file__))[0] + '/config.json','r') as file:
  cf = json.loads(file.read())
except:
 sys.exit('exit: The configuration file ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required ')

#######################################################
#
# Init Screen
#
#######################################################
sys.path.append(os.path.split(os.path.abspath(__file__))[0] + '/waveshare144)
import LCD_1in44
import LCD_Config


KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

#######################################################
#
# get system informiation only one time at start
#
#######################################################

#init GPIO
GPIO.setmode(GPIO.BCM) 
#GPIO.cleanup()
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

# 240x240 display with hardware SPI:
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 128
height = 128
image = Image.new('RGB', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
#draw.rectangle((0,0,width,height), outline=0, fill=0)
#disp.LCD_ShowImage(image,0,0)

#######################################################
#
# functions
#
#######################################################

def scantime():
    return(datetime.now().strftime("%Y%m%d-%H%M%S"))

def pdfmerge(cf,jobtime,documente_jpg):
    merger = PdfFileMerger()
    for file in document_jpg:
        pdffile = file[0:-4] + '.pdf'
        merger.append(pdffile)
    merger.write(cf['folder']['destination'] + '/' + cf['filename']['prefix'] + jobtime + ".pdf")
    merger.close()
 

def send_to_pushover(source,jobtime,format,cf):
    thumbnailfile = cf['folder']['destination'] + "/thumb." + cf["filename"]["prefix"] + jobtime + ".jpg"
    os.system("convert -thumbnail 200 " + source + " " + thumbnailfile)

    r = requests.post("https://api.pushover.net/1/messages.json", data = {
        "token": cf['pushover']['apikey'],
        "user": cf['pushover']['userkey'],
#            "html": 1,
#            "priority": 1,
        "message": 'image scan_' + jobtime + '.' + format + ' scanned'
        }
    ,
    files = {
    "attachment": ("thumb.jpg", open(thumbnailfile, 'rb'), "image/jpg")
    }
    )
    os.remove(thumbnailfile)
    return()


#######################################################
#
# do magic
#
#######################################################

# try:
while 1:
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((0, 10), 'ready', fill = "GREEN")
    draw.text((32, 30), 'A4 600dpi PNG ->', fill = "GREEN")
    draw.text((32, 60), 'A4 300dpi JPG ->', fill = "GREEN")
    draw.text((32, 90), 'A4 300dpi PDF ->', fill = "GREEN")
    disp.LCD_ShowImage(image,0,0)
    time.sleep(1)

#300dpi JPG 
    if GPIO.input(KEY2_PIN) == 0: # button is released
        jobtime = scantime()
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((0, 0), jobtime, fill = "blue")
        draw.text((0, 10), 'scan 300dpi jpg', fill = "YELLOW")
        disp.LCD_ShowImage(image,0,0)
        document = cf['folder']['destination'] + "/" + cf["filename"]["prefix"] + "" + jobtime + ".jpg"
        format = 'jpg'
        os.system("/usr/bin/scanimage > " + document + " --format=jpeg --resolution=300 --device-name='" + cf['devicename'] + "' -x 210 -y 297")
        draw.text((0, 30), 'pushover message', fill = "YELLOW")
        disp.LCD_ShowImage(image,0,0)
        send_to_pushover(document,jobtime,format,cf)

#600dpi PNG
    if GPIO.input(KEY1_PIN) == 0: # button is released
        jobtime = scantime()
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((0, 0), jobtime, fill = "blue")
        disp.LCD_ShowImage(image,0,0)
        draw.text((0, 10), 'scan 600dpi png', fill = "YELLOW")
        disp.LCD_ShowImage(image,0,0)
        document = cf['folder']['destination'] + "/" + cf["filename"]["prefix"] + "" + jobtime + ".png"
        format = 'png'
        os.system("/usr/bin/scanimage > " + document + " --format=png --resolution=600 --device-name='" + cf['devicename'] + "' -x 210 -y 297")
        draw.text((0, 30), 'pushover message', fill = "YELLOW")
        disp.LCD_ShowImage(image,0,0)
        send_to_pushover(document,jobtime,format,cf)

#300dpi PDF
    if GPIO.input(KEY3_PIN) == 0: # button is released
        
        ####scannt ganz fiele JPGs mit _01.jpg
        i = 0
#        document_jpg = [0]
        jobtime = scantime()
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((0, 0), jobtime, fill = "blue")
        while True:
            draw.text((0, 10), 'scan 300dpi pdf', fill = "YELLOW")
            draw.text((0, 20), 'page: ' + str(i+1), fill = "ORANGE")
            disp.LCD_ShowImage(image,0,0)
            try: 
                document_jpg.append(cf['folder']['temp'] + "/" + cf["filename"]["prefix"] + "" + jobtime + "_" + str(i).zfill(2) + ".jpg")
            except:
                document_jpg = [cf['folder']['temp'] + "/" + cf["filename"]["prefix"] + "" + jobtime + "_" + str(i).zfill(2) + ".jpg"]
            os.system("/usr/bin/scanimage > " + document_jpg[i] + " --format=jpeg --resolution=300 --device-name='" + cf['devicename'] + "' -x 210 -y 297")
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((0, 10), 'ready', fill = "GREEN")
            draw.text((32, 30), '         next ->', fill = "GREEN")
            draw.text((32, 60), '         done ->', fill = "GREEN")
            disp.LCD_ShowImage(image,0,0)
            time.sleep(1)
            while True:
                if GPIO.input(KEY1_PIN) == 0: # button is released
                    option = 'next'
                    i=i+1
                    break
                if GPIO.input(KEY2_PIN) == 0: # button is released
                    option = 'done'
                    break
            if option == 'done':
                break
        
        
        #####mit ocr in eine PDF oder nur so in eien pdf
        while True:
 
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((0, 10), 'OCR ?', fill = "YELLOW")
            draw.text((32, 30), '          yes ->', fill = "GREEN")
            draw.text((32, 60), '           no ->', fill = "GREEN")
            disp.LCD_ShowImage(image,0,0)
            time.sleep(1)
            while True:
                if GPIO.input(KEY1_PIN) == 0: # button is released
                    option = 'doocr'
                    break
                if GPIO.input(KEY2_PIN) == 0: # button is released
                    option = 'noocr'
                    break
            if option == 'doocr' or option == 'noocr':
                break
        
        #####DO OCR
        if option == 'doocr':
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((0, 0), jobtime, fill = "blue")
            draw.text((0, 10), 'ocr pdf', fill = "YELLOW")
            disp.LCD_ShowImage(image,0,0)

            for file in document_jpg:
                os.system("tesseract " + file + ' ' + file[0:-4] + ' -l deu+eng pdf')
            pdfmerge(cf,jobtime,document_jpg)

        #####NO OCR
        if option == 'noocr':
            for file in document_jpg:
                image_1 = Image.open(file)
                im_1 = image_1.convert('RGB')
                im_1.save(file[0:-4] + '.pdf')
            pdfmerge(cf,jobtime,document_jpg)

        format = 'pdf'
        draw.text((0, 30), 'pushover message', fill = "YELLOW")
        disp.LCD_ShowImage(image,0,0)
        send_to_pushover(document_jpg[0],jobtime,format,cf)

        for file in document_jpg:
            os.remove(file)