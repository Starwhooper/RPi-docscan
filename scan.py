#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# Source: https://github.com/Starwhooper/RPi-docscan

#######################################################
#
# Prepare
#
#######################################################

# -*- coding:utf-8 -*-
from PIL import Image,ImageDraw,ImageFont,ImageColor
from PyPDF2 import PdfFileMerger
from datetime import datetime
import RPi.GPIO as GPIO
import json
import os
import requests
import subprocess
import sys
import time
import urllib.request


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
sys.path.append(os.path.split(os.path.abspath(__file__))[0] + '/waveshare144')
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
    return(datetime.now().strftime(cf['filename']['timestamp']))

def ocrspace(documentfile):
#    cf_ocrspace_apikey = 'K85906370488957'
    
    payload = {'isOverlayRequired': False, 'apikey': cf['ocrspace']['apikey'], 'isCreateSearchablePdf' : True, 'isSearchablePdfHideTextLayer' : True, 'OCREngine' : 2, }
    with open(documentfile, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image', files={documentfile: f}, data=payload, )
    
    pdfcontent = json.loads(r.content.decode())    
    urllib.request.urlretrieve(pdfcontent['SearchablePDFURL'], documentfile[0:-4] + '.pdf')

def pdfmerge(cf,jobtime,documente_jpg):
    merger = PdfFileMerger()
    for file in document_jpg:
        pdffile = file[0:-4] + '.pdf'
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((0, 0), 'merge', fill = cf['color']['font'])
        draw.text((0, 10), os.path.basename(pdffile), fill = cf['color']['font'])
        disp.LCD_ShowImage(image,0,0)
        print('add ' + pdffile)
        merger.append(pdffile)
        os.remove(pdffile)        

    print('merge all to ' + cf['folder']['destination'] + '/' + cf['filename']['prefix'] + jobtime + ".pdf")
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



while 1:
    scannerfound = 0
    while scannerfound == 0:
        try:
            scanner = subprocess.check_output("/usr/bin/scanimage -n --device-name='" + cf['devicename'] + "' --format=jpeg", shell=True)
            scannerfound = 1
        except:
            scannerfound = 0
        if scannerfound == 0:
            draw.rectangle((0,0,width,height), outline=0, fill="RED")
            draw.text((10, 10), 'wait for scanner', fill = cf['color']['font'])
            disp.LCD_ShowImage(image,0,0)
            time.sleep(2)

    destinationfound = 0
    while destinationfound == 0:
        if os.path.exists(cf['folder']['destination']) == True: 
            destinationfound = 1
        else:
            draw.rectangle((0,0,width,height), outline=0, fill="RED")
            draw.text((5, 10), 'destination not', fill = cf['color']['font'])
            draw.text((5, 20), 'available', fill = cf['color']['font'])
            draw.text((5, 40), cf['folder']['destination'][0:19], fill = cf['color']['font'])
            draw.text((5, 50), cf['folder']['destination'][20:39], fill = cf['color']['font'])
            draw.text((5, 60), cf['folder']['destination'][40:59], fill = cf['color']['font'])
            disp.LCD_ShowImage(image,0,0)
            time.sleep(2)

    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((0, 10), 'ready', fill = cf['color']['font'])
    draw.text((10, 30), 'Image File ->', fill = cf['color']['font'])
#    draw.text((32, 60), 'A4 300dpi JPG ->', fill = cf['color']['font'])
    draw.text((10, 90), 'PDF Document ->', fill = cf['color']['font'])
    disp.LCD_ShowImage(image,0,0)
    time.sleep(0.2)


#scan Images
    if GPIO.input(KEY1_PIN) == 0: # button is released

        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((0, 10), 'which file formant ?', fill = cf['color']['font'])
        draw.text((10, 30), 'PNG ->', fill = cf['color']['font'])
        draw.text((10, 60), 'JPEG ->', fill = cf['color']['font'])
        draw.text((10, 90), 'TIFF ->', fill = cf['color']['font'])
        disp.LCD_ShowImage(image,0,0)
        time.sleep(1)
        
        fileformat = 'xxx'
        fileextension = 'xxx'
        while fileformat == 'xxx':
            if GPIO.input(KEY1_PIN) == 0: 
                fileformat = 'png'
                fileextension = 'png'
            elif GPIO.input(KEY2_PIN) == 0:
                fileformat = 'jpeg'
                fileextension = 'jpg'
            elif GPIO.input(KEY3_PIN) == 0:
                fileformat = 'tiff'
                fileextension = 'tif'

        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((0, 10), 'which page formant ?', fill = cf['color']['font'])
        draw.text((10, 30), 'A4 ->', fill = cf['color']['font'])
        draw.text((10, 60), 'A5 upright ->', fill = cf['color']['font'])
        draw.text((10, 90), 'A5 landscape  ->', fill = cf['color']['font'])
        disp.LCD_ShowImage(image,0,0)
        time.sleep(1)

        papersize_x = 0
        papersize_y = 0
        while papersize_x == 0:
            if GPIO.input(KEY1_PIN) == 0: 
                papersize_x = 210
                papersize_y = 297
            elif GPIO.input(KEY2_PIN) == 0:
                papersize_x = 148
                papersize_y = 210
            elif GPIO.input(KEY3_PIN) == 0:
                papersize_x = 210
                papersize_y = 148
            

        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((0, 10), 'which resolution ?', fill = cf['color']['font'])
        draw.text((0, 30), '150dpi (to print) ->', fill = cf['color']['font'])
        draw.text((0, 60), '300dpi (documents) ->', fill = cf['color']['font'])
        draw.text((0, 90), '600dpi (detailed images)  ->', fill = cf['color']['font'])
        disp.LCD_ShowImage(image,0,0)
        time.sleep(1)

        resolution = 0

        while resolution == 0:
            if GPIO.input(KEY1_PIN) == 0: 
                resolution = 150
            elif GPIO.input(KEY2_PIN) == 0:
                resolution = 300
            elif GPIO.input(KEY3_PIN) == 0:
                resolution = 600

        jobtime = scantime()
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((0, 0), jobtime, fill = cf['color']['font'])
        disp.LCD_ShowImage(image,0,0)
        draw.text((0, 10), 'scan ' + str(resolution) + 'dpi ' + fileformat, fill = cf['color']['font'])
        disp.LCD_ShowImage(image,0,0)
        document = cf['folder']['destination'] + "/" + cf["filename"]["prefix"] + "" + jobtime + "." + fileextension
        os.system("/usr/bin/scanimage > " + document + " --format=" + fileformat + " --resolution=" + str(resolution) + " --device-name='" + cf['devicename'] + "' -x " + str(papersize_x) + " -y " + str(papersize_y))
        draw.text((0, 30), 'pushover message', fill = cf['color']['font'])
        disp.LCD_ShowImage(image,0,0)
        send_to_pushover(document,jobtime,fileextension,cf)


#scan PDF
    if GPIO.input(KEY3_PIN) == 0: # button is released
        biggestfilesize = 0
        ####scannt ganz viele JPGs mit _01.jpg
        i = 0
#        document_jpg = [0]
        jobtime = scantime()
        while True:
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((0, 0), jobtime, fill = cf['color']['font'])
            draw.text((0, 10), 'scan 300dpi pdf', fill = cf['color']['font'])
            draw.text((0, 20), 'page: ' + str(i+1), fill = cf['color']['font'])
            disp.LCD_ShowImage(image,0,0)
            try: 
                document_jpg.append(cf['folder']['temp'] + "/" + cf["filename"]["prefix"] + "" + jobtime + "_" + str(i).zfill(2) + ".jpg")
            except:
                document_jpg = [cf['folder']['temp'] + "/" + cf["filename"]["prefix"] + "" + jobtime + "_" + str(i).zfill(2) + ".jpg"]

            os.system("/usr/bin/scanimage > " + document_jpg[i] + " --format=jpeg --resolution=300 --device-name='" + cf['devicename'] + "' -x " + str(cf['papersize']['x']) + " -y " + str(cf['papersize']['y']))
            filesize = os.path.getsize(document_jpg[i])
            if filesize >= biggestfilesize: biggestfilesize = filesize
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((0, 0), 'ready', fill = cf['color']['font'])
            draw.text((32, 25), '            next', fill = cf['color']['font'])
            draw.text((32, 35), '              ->', fill = cf['color']['font'])
            draw.text((32, 55), '            done', fill = cf['color']['font'])
            draw.text((32, 65), '              ->', fill = cf['color']['font'])

            #thumbnail and counter
            thumb = Image.open(document_jpg[i])
            thumb_x = 100
            thumb = thumb.resize((thumb_x,int(thumb.height / thumb.width * thumb_x)))
            image.paste(thumb,(0,15))
            draw.ellipse((5, 110, 20, 120), fill="BLACK")
            draw.text((10,110), str(i+1), fill=cf['color']['font'])

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
        
        #####mit ocr in eine PDF oder nur so in eine pdf
        while True:
 
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((0, 10), 'OCR ?', fill = cf['color']['font'])
            draw.text((0, 30), '             local ->', fill = cf['color']['font'])
            draw.text((0, 55), '            remote ->', fill = cf['color']['font'])
            if biggestfilesize <= cf['ocrspace']['limit']:
                draw.text((0, 65), '      size: ' + str(round(biggestfilesize/1024/1024,2)) + 'MB', fill = cf['color']['font'])
            else:
                draw.text((0, 65), '      size: ' + str(round(biggestfilesize/1024/1024,2)) + 'MB', fill = 'RED')
            draw.text((0, 90), '                no ->', fill = cf['color']['font'])
            disp.LCD_ShowImage(image,0,0)
            time.sleep(1)
            while True:
                if GPIO.input(KEY1_PIN) == 0: # button is released
                    option = 'doocr'
                    ocroption = 'localocr'
                    break
                if GPIO.input(KEY2_PIN) == 0: # button is released
                    option = 'doocr'
                    ocroption = 'remoteocr'
                    break
                if GPIO.input(KEY3_PIN) == 0: # button is released
                    option = 'noocr'
                    break
            if option == 'doocr' or option == 'noocr':
                break
       
        #####DO OCR
        if option == 'doocr':
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.text((0, 0), jobtime, fill = cf['color']['font'])
            draw.text((0, 10), 'ocr pdf', fill = cf['color']['font'])
            disp.LCD_ShowImage(image,0,0)
            
            for file in document_jpg:
#                print(file)
                draw.rectangle((0,0,width,height), outline=0, fill=0)
                draw.text((0, 0), 'convert and ocr', fill = cf['color']['font'])
                draw.text((0, 10), os.path.basename(file), fill = cf['color']['font'])
                draw.text((0, 20), 'to pdf', fill = cf['color']['font'])
                disp.LCD_ShowImage(image,0,0)
                #local ocr
                if ocroption == 'localocr':
                    print('start tesseract:' + file)
                    os.system("tesseract " + file + ' ' + file[0:-4] + ' -l deu+eng pdf')
                #remote ocr
                elif ocroption == 'remoteocr':
                    print('start ocrspace:' + file)
                    ocrspace(file)
                else: print('miss ocroption value')
               
                
            pdfmerge(cf,jobtime,document_jpg)

        #####NO OCR
        if option == 'noocr':
        
            for file in document_jpg:
                draw.rectangle((0,0,width,height), outline=0, fill=0)
                draw.text((0, 0), 'convert', fill = cf['color']['font'])
                draw.text((0, 10), os.path.basename(file), fill = cf['color']['font'])
                draw.text((0, 20), 'to pdf', fill = cf['color']['font'])
                disp.LCD_ShowImage(image,0,0)

                image_1 = Image.open(file)
                im_1 = image_1.convert('RGB')
                im_1.save(file[0:-4] + '.pdf', resolution=300)
            pdfmerge(cf,jobtime,document_jpg)

        format = 'pdf'
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((0, 30), 'pushover message', fill = cf['color']['font'])
        disp.LCD_ShowImage(image,0,0)
        send_to_pushover(document_jpg[0],jobtime,format,cf)
        
        for file in document_jpg:
            os.remove(file)
        del document_jpg
