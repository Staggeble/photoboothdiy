import picamera
import pygame
import time
import os
import PIL.Image
import cups
import RPi.GPIO as GPIO

from threading import Thread
from pygame.locals import *
from time import sleep
from PIL import Image, ImageDraw

# initialise global variables
numeral = ""  # numeral is the number display
message = ""  # message is a full-screen message
background_color = ""
count_down_photo = ""
CountPhotoOnCart = ""
small_message = ""  # small_message is a lower banner message
total_image_count = 0  # Counter for Display and to monitor paper usage
photos_per_cart = 30  # Selphy takes 16 sheets per tray
image_counter = 0
image_folder = 'Photos'
templatePath = os.path.join('Photos', 'Template', "template.jpg")  # Path of template image
image_showed = False
printing = False
BUTTON_PIN = 25
# IMAGE_WIDTH = 558
# IMAGE_HEIGHT = 374
IMAGE_WIDTH = 550
IMAGE_HEIGHT = 360

# Load the background template
bgimage = PIL.Image.open(templatePath)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# initialise pygame
pygame.init()  # Initialise pygame
pygame.mouse.set_visible(False)  # hide the mouse cursor
info_object = pygame.display.Info()
screen = pygame.display.set_mode((info_object.current_w, info_object.current_h), pygame.FULLSCREEN)  # Full screen
background = pygame.Surface(screen.get_size())  # Create the background object
background = background.convert()  # Convert it to a background

screen_picture = pygame.display.set_mode((info_object.current_w, info_object.current_h),
                                         pygame.FULLSCREEN)  # Full screen
background_picture = pygame.Surface(screen_picture.get_size())  # Create the background object
background_picture = background.convert()  # Convert it to a background

transform_x = info_object.current_w  # how wide to scale the jpg when replaying
transform_y = info_object.current_h  # how high to scale the jpg when replaying

camera = picamera.PiCamera()
# Initialise the camera object
camera.resolution = (info_object.current_w, info_object.current_h)
camera.rotation = 0
camera.hflip = True
camera.vflip = False
camera.brightness = 50
camera.preview_alpha = 120
camera.preview_fullscreen = True


# camera.framerate             = 24
# camera.sharpness             = 0
# camera.contrast              = 8
# camera.saturation            = 0
# camera.ISO                   = 0
# camera.video_stabilization   = False
# camera.exposure_compensation = 0
# camera.exposure_mode         = 'auto'
# camera.meter_mode            = 'average'
# camera.awb_mode              = 'auto'
# camera.image_effect          = 'none'
# camera.color_effects         = None
# camera.crop                  = (0.0, 0.0, 1.0, 1.0)


# A function to handle keyboard/mouse/device user input events
def user_input(events):
    for event in events:  # Hit the ESC key to quit the slideshow.
        if (event.type == QUIT or
                (event.type == KEYDOWN and event.key == K_ESCAPE)):
            pygame.quit()


# set variables to properly display the image on screen at right ratio
def set_dimensions(img_w, img_h):
    # Note this only works when in booting in desktop mode.
    # When running in terminal, the size is not correct (it displays small). Why?

    # connect to global vars
    global transform_y, transform_x, offset_y, offset_x

    # based on output screen resolution, calculate how to display
    ratio_h = (info_object.current_w * img_h) / img_w

    if ratio_h < info_object.current_h:
        # Use horizontal black bars
        # print "horizontal black bars"
        transform_y = ratio_h
        transform_x = info_object.current_w
        offset_y = (info_object.current_h - ratio_h) / 2
        offset_x = 0
    elif ratio_h > info_object.current_h:
        # Use vertical black bars
        # print "vertical black bars"
        transform_x = (info_object.current_h * img_w) / img_h
        transform_y = info_object.current_h
        offset_x = (info_object.current_w - transform_x) / 2
        offset_y = 0
    else:
        # No need for black bars as photo ratio equals screen ratio
        # print "no black bars"
        transform_x = info_object.current_w
        transform_y = info_object.current_h
        offset_y = offset_x = 0


def init_folder():
    global image_folder
    global message

    message = 'Folder Check...'
    update_display()
    message = ''

    # check image folder existing, create if not exists
    if not os.path.isdir(image_folder):
        os.makedirs(image_folder)

    image_folder2 = os.path.join(image_folder, 'images')
    if not os.path.isdir(image_folder2):
        os.makedirs(image_folder2)


def display_text(font_size, text_to_display):
    global numeral
    global message
    global screen
    global background
    global pygame
    global image_showed
    global screen_picture
    global background_picture
    global count_down_photo

    if background_color != "":
        # print(background_color)
        background.fill(pygame.Color("black"))
    if text_to_display != "":
        # print(display_text)
        font = pygame.font.Font(None, font_size)
        text = font.render(text_to_display, 1, (227, 157, 200))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if image_showed:
            background_picture.blit(text, textpos)
        else:
            background.blit(text, textpos)


def update_display():
    # init global variables from main thread
    global numeral
    global message
    global screen
    global background
    global pygame
    global image_showed
    global screen_picture
    global background_picture
    global count_down_photo

    background.fill(pygame.Color("white"))  # White background
    # display_text(100, message)
    # display_text(800, numeral)
    # display_text(500, count_down_photo)

    if background_color != "":
        # print(background_color)
        background.fill(pygame.Color("black"))
    if message != "":
        # print(display_text)
        font = pygame.font.Font(None, 100)
        text = font.render(message, 1, (227, 157, 200))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if image_showed:
            background_picture.blit(text, textpos)
        else:
            background.blit(text, textpos)

    if numeral != "":
        # print(display_text)
        font = pygame.font.Font(None, 800)
        text = font.render(numeral, 1, (227, 157, 200))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if image_showed:
            background_picture.blit(text, textpos)
        else:
            background.blit(text, textpos)

    if count_down_photo != "":
        # print(display_text)
        font = pygame.font.Font(None, 500)
        text = font.render(count_down_photo, 1, (227, 157, 200))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        if image_showed:
            background_picture.blit(text, textpos)
        else:
            background.blit(text, textpos)

    if image_showed:
        screen_picture.blit(background_picture, (0, 0))
    else:
        screen.blit(background, (0, 0))

    pygame.display.flip()
    return


def show_picture(file, delay):
    global pygame
    global screen_picture
    global background_picture
    global image_showed
    background_picture.fill((0, 0, 0))
    img = pygame.image.load(file)
    img = pygame.transform.scale(img, screen_picture.get_size())  # Make the image full screen
    # background_picture.set_alpha(200)
    background_picture.blit(img, (0, 0))
    screen.blit(background_picture, (0, 0))
    pygame.display.flip()  # update the display
    image_showed = True
    time.sleep(delay)


# display one image on screen
def show_image(image_path):
    screen.fill(pygame.Color("white"))  # clear the screen
    img = pygame.image.load(image_path)  # load the image
    img = img.convert()
    set_dimensions(img.get_width(), img.get_height())  # set pixel dimensions based on image
    x = (info_object.current_w / 2) - (img.get_width() / 2)
    y = (info_object.current_h / 2) - (img.get_height() / 2)
    screen.blit(img, (x, y))
    pygame.display.flip()


def capture_picture():
    global image_counter
    global image_folder
    global numeral
    global message
    global screen
    global background
    global screen_picture
    global background_picture
    global pygame
    global image_showed
    global count_down_photo
    global background_color

    background_color = ""
    numeral = ""
    message = ""
    update_display()
    time.sleep(1)
    count_down_photo = ""
    update_display()
    background.fill(pygame.Color("black"))
    screen.blit(background, (0, 0))
    pygame.display.flip()
    camera.start_preview()
    background_color = "black"

    for x in range(3, -1, -1):
        if x == 0:
            numeral = ""
            message = "STRIKE A POSE"
        else:
            numeral = str(x)
            message = ""
        update_display()
        time.sleep(1)

    background_color = ""
    numeral = ""
    message = ""
    update_display()
    image_counter = image_counter + 1
    ts = time.time()
    filename = os.path.join(image_folder, 'images', str(image_counter) + "_" + str(ts) + '.jpg')
    camera.capture(filename, resize=(IMAGE_WIDTH, IMAGE_HEIGHT))
    camera.stop_preview()
    show_picture(filename, 2)
    image_showed = False
    return filename


def take_pictures():
    global image_counter
    global image_folder
    global numeral
    global message
    global screen
    global background
    global pygame
    global image_showed
    global count_down_photo
    global background_color
    global printing
    global PhotosPerCart
    global total_image_count

    user_input(pygame.event.get())
    count_down_photo = "1/3"
    filename1 = capture_picture()

    count_down_photo = "2/3"
    filename2 = capture_picture()

    count_down_photo = "3/3"
    filename3 = capture_picture()

    count_down_photo = ""
    message = "Please wait..."
    update_display()

    image1 = PIL.Image.open(filename1)
    image2 = PIL.Image.open(filename2)
    image3 = PIL.Image.open(filename3)
    total_image_count = total_image_count + 1

    bgimage.paste(image1, (625, 30))
    bgimage.paste(image2, (625, 410))
    bgimage.paste(image3, (55, 410))
    # Create the final filename
    ts = time.time()
    final_image_name = os.path.join(image_folder, "Final_" + str(total_image_count) + "_" + str(ts) + ".jpg")
    # Save it to the usb drive
    bgimage.save(final_image_name)
    # Save a temp file, it's faster to print from the pi than usb
    bgimage.save('/home/pi/Desktop/tempprint.jpg')
    show_picture('/home/pi/Desktop/tempprint.jpg', 3)
    bgimage2 = bgimage.rotate(90)
    bgimage2.save('/home/pi/Desktop/tempprint.jpg')
    image_showed = False
    message = "Press the button to print"
    update_display()
    time.sleep(1)
    message = ""
    update_display()
    printing = False
    wait_for_printing_event()
    numeral = ""
    message = ""
    print(printing)
    if printing:
        if total_image_count <= photos_per_cart:
            if os.path.isfile('/home/pi/Desktop/tempprint.jpg'):
                # Open a connection to cups
                conn = cups.Connection()
                # get a list of printers
                printers = conn.getPrinters()
                # select printer 0
                printer_name = printers.keys()[0]
                message = "Printing in progress..."
                update_display()
                time.sleep(1)
                # print the buffer file
                print_queue_length = len(conn.getJobs())
                if print_queue_length > 1:
                    show_picture('/home/pi/Desktop/tempprint.jpg', 3)
                    conn.enablePrinter(printer_name)
                    message = "Impression impossible"  # unsure how to translate this ...
                    update_display()
                    time.sleep(1)
                else:
                    conn.printFile(printer_name, '/home/pi/Desktop/tempprint.jpg', "PhotoBooth", {})
                    time.sleep(40)
        else:
            message = "We will send you your photos"
            numeral = ""
            update_display()
            time.sleep(1)

    message = ""
    numeral = ""
    image_showed = False
    update_display()
    time.sleep(1)


def my_callback(channel):
    global printing
    GPIO.remove_event_detect(BUTTON_PIN)
    printing = True


def wait_for_printing_event():
    global background_color
    global numeral
    global message
    global printing
    global pygame
    count_down = 5
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING)
    GPIO.add_event_callback(BUTTON_PIN, my_callback)

    while printing == False and count_down > 0:
        if printing:
            return
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    GPIO.remove_event_detect(BUTTON_PIN)
                    printing = True
                    return
        background_color = ""
        numeral = str(count_down)
        message = ""
        update_display()
        count_down = count_down - 1
        time.sleep(1)

    GPIO.remove_event_detect(BUTTON_PIN)


def wait_for_event():
    global pygame
    not_event = True
    while not_event:
        input_state = GPIO.input(BUTTON_PIN)
        if not input_state:
            not_event = False
            return
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                if event.key == pygame.K_DOWN:
                    not_event = False
                    return
        time.sleep(0.2)


def main(thread_name, *args):
    init_folder()
    while True:
        show_image('images/start_camera.jpg')
        wait_for_event()
        time.sleep(0.2)
        take_pictures()
    GPIO.cleanup()


# launch the main thread
Thread(target=main, args=('Main', 1)).start()

