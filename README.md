# RPi-docscan #

Offer a small service with waveshare 144 support on Raspberry Pi Zero to scan documents direct on NAS drive.

Main features:
* support local OCR with tesseract
* support remote OCR with OCR Space
* support little OLED Screen
* support pushover

![Display](https://github.com/Starwhooper/RPi-docscan/blob/main/examples/case.jpg)

## Installation ##
install all needed packages to prepare the software environtent of your Raspberry Pi:
```bash
sudo raspi-config
  and enable Interface type SPI
```

```bash
sudo apt install python3-pip python3-pil git libatlas-base-dev
sudo pip3 install RPi.GPIO psutil numpy netifaces spidev
```
and this tool itself:
```bash
cd /opt
sudo git clone https://github.com/Starwhooper/RPi-docscan
```

## First configurtion ##
```bash
sudo cp /opt/RPi-docscan/config.json.example /opt/RPi-docscan/config.json
sudo nano /opt/RPi-status-on-OLED/config.json
```
This Tool used sane. Use this sources to know the right settings:
* sane documentation: http://www.sane-project.org/man/scanimage.1.html
* get device-name via: sudo /usr/bin/scanimage -L
* get all possible setting for your device: /usr/bin/scanimage --device-name="pixma:04A9190D" -A


## Start ##
add it to rc.local to autostart as boot
```bash
sudo nano /etc/rc.local
/opt/RPi-docscan/scan.py
```

## Update ##
If you already use it, feel free to update with
```bash
cd /opt/RPi-docscan
sudo git pull origin main
```

## Hardware ##
### Case ###
Case to enclosure Raspberry Pi zero ans Waveshare 1.44inch LCD HAT_ https://www.thingiverse.com/thing:5324460
