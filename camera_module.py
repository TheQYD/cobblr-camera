"""camera_module.py: Cobblr module that uses PiTFT and RPi camera to take pictures."""
__author__ = 'Qasim Dove'
__credit__ = ['Cliff Dove', '<name of persons>']
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "emailqasim@gmail.com"

from engine import Screen
from engine import Utilities
from engine import TextWriter
from engine import SystemState
from engine import Menu
from engine import Events
import RPi.GPIO
import io
import os
import signal
import picamera
import time
import threading

signal.signal(signal.SIGINT, Utilities.GracefulExit)

class CameraState(object):
  pass

def Init():
  """Sets up the class and variables needed in order to run the camera app."""
  RPi.GPIO.setup(7, RPi.GPIO.OUT) #Flash RPi.GPIO
  RPi.GPIO.setup(8, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP) #Button RPi.GPIO
  SystemState.CameraState = CameraState
  
  RPi.GPIO.output(7, False)
  SystemState.CameraState.current_photo = ""
  SystemState.CameraState.photo_file_name = None
  SystemState.CameraState.photo_path = 'media/photos/'
  SystemState.CameraState.preview_path = SystemState.CameraState.photo_path + '.preview/'
  preview_path = SystemState.CameraState.preview_path
  SystemState.CameraState.image_effect = 0
  SystemState.CameraState.photo_tally = None
  SystemState.CameraState.flash_enabled = True
  SystemState.CameraState.exit_camera = False
  SystemState.CameraState.camera_stream = False
  SystemState.CameraState.album = False
  SystemState.CameraState.setting = 'none'
  MakePhotoPath()
  SystemState.CameraState.photo_archive = os.listdir(preview_path)
  SystemState.CameraState.photo_archive = [os.path.join(preview_path, pic) for pic in SystemState.CameraState.photo_archive]
  SystemState.CameraState.photo_archive = sorted(SystemState.CameraState.photo_archive)
  SystemState.CameraState.photo_count = len(SystemState.CameraState.photo_archive)


  SystemState.CameraState.image_effect = 0
  SystemState.CameraState.iso = 0
  SystemState.CameraState.rotation = 0
  SystemState.CameraState.brightness = 5
  SystemState.CameraState.saturation = 10
  SystemState.CameraState.contrast = 10
  SystemState.CameraState.sharpness = 10
  SystemState.CameraState.zoom = 0
  SystemState.CameraState.meter_mode = 0
  SystemState.CameraState.awb_mode = 0
  SystemState.CameraState.exposure_mode = 0
  SystemState.CameraState.shutter_speed = 0

  SystemState.CameraState.iso_values = [0, 100, 200, 320, 400, 500, 640, 800]
  SystemState.CameraState.image_effect_values = [
      'none', 'negative', 'solarize', 'sketch', 'denoise', 'emboss', 'oilpaint',
      'hatch','gpen', 'pastel', 'watercolor', 'film', 'blur', 'saturation',
      'colorswap', 'washedout', 'posterise',  'colorpoint', 'colorbalance',
      'cartoon', 'deinterlace1', 'deinterlace2'
  ]
  SystemState.CameraState.awb_mode_values = [
      'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent',
      'incandescent', 'flash', 'horizon', 'off'
  ]
  SystemState.CameraState.rotation_values = [0, 90, 180, 270]
  SystemState.CameraState.brightness_values = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
  hundred_container = [-100, -90, -80, -70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
  SystemState.CameraState.saturation_values = hundred_container
  SystemState.CameraState.contrast_values = hundred_container
  SystemState.CameraState.sharpness_values = hundred_container

  SystemState.CameraState.zoom_values = [
      (0.0, 0.0, 1.0, 1.0),
      (0.1, 0.1, 0.9, 0.9),
      (0.225, 0.225, 0.8, 0.8),
      (0.25, 0.25, 0.7, 0.7),
      (0.275, 0.275, 0.6, 0.6),
      (0.3, 0.3, 0.5, 0.5),
      (0.325, 0.325, 0.4, 0.4),
      (0.35, 0.25, 0.3, 0.3),
      (0.375, 0.375, 0.2, 0.2),
      (0.4, 0.4, 0.1, 0.1),
  ]
  SystemState.CameraState.meter_mode_values = [
      'average', 'spot', 'backlit', 'matrix'
  ]  
  SystemState.CameraState.exposure_mode_values = [
      'auto', 'night', 'nightpreview', 'backlight', 'spotlight',
      'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake',
      'fireworks', 'off'
  ]
  SystemState.CameraState.shutter_speed_values = [1000000, 100000, 10000, 1000, 100]


def MakePhotoPath():
  """Creates the folder that stores the highres and preview photo."""
  if os.path.exists(SystemState.CameraState.preview_path) == False:
    os.makedirs(SystemState.CameraState.preview_path)
  os.chown(SystemState.CameraState.preview_path, SystemState.uid, SystemState.gid)

def Process():
  """Determines what buttons were pressed with each screen touch."""
  button = str(SystemState.pressed_button)
  pygame = SystemState.pygame
  screen = SystemState.screen
  screen_mode = SystemState.screen_mode

  if button == 'flash_on':
    Menu.JumpTo(screen_mode=2, toggle=True)
    SystemState.CameraState.flash_enabled = False
  elif button == 'flash_off':
    Menu.JumpTo(screen_mode=1, toggle=True)
    SystemState.CameraState.flash_enabled = True
  elif button == 'go_back':
    Menu.Back()
    SystemState.CameraState.setting = 'none'
    SystemState.CameraState.album = False
  elif button == 'gallery':
    Menu.JumpTo(screen_mode=3)
    OpenAlbum()
  elif button == 'right_arrow':
    __ProcessRightArrow()
  elif button == 'left_arrow':
    __ProcessLeftArrow()
  elif button == 'capture':
    CallTakePhoto()
  elif button == 'delete' and SystemState.CameraState.photo_count > 0:
    Menu.JumpTo(screen_mode=4)
    BlitImage(SystemState.CameraState.current_photo, SystemState.pygame, SystemState.screen)
    TextWriter.Write(state=SystemState, text='Delete?', position=(125, 75), size=20)
  elif button == 'iso':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'iso'
  elif button == 'image_effect':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'image_effect'
  elif button == 'rotation':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'rotation'
  elif button == 'brightness':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'brightness'
  elif button == 'saturation':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'saturation'
  elif button == 'contrast':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'contrast'
  elif button == 'sharpness':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'sharpness'
  elif button == 'zoom':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'zoom'
  elif button == 'meter_mode':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'meter_mode'
  elif button == 'awb':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'awb_mode'
  elif button == 'shutter_speed':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'shutter_speed'
  elif button == 'exposure_mode':
    Menu.JumpTo(screen_mode=6)
    SystemState.CameraState.setting = 'exposure_mode'
  elif button == 'settings':
    Menu.JumpTo(screen_mode=5)
  elif button == 'accept':
    DeletePhoto()
    Menu.Back()
    OpenAlbum()
  elif button == 'decline':
    Menu.Back()
    OpenAlbum()

  if SystemState.screen_mode == 5 and SystemState.next_screen_mode == 6:
    setting = SystemState.CameraState.setting
    setting_values = setting + '_values'
    __CurrentSetting(setting_values, setting)

  SystemState.CameraState.camera_stream = False

def __PreviousSetting(property_list, property_name):
  properties = getattr(SystemState.CameraState, property_list)
  index = getattr(SystemState.CameraState, property_name)
  if index > 0:
    index -= 1
  else:
    index = len(properties) - 1
  __ProcessSettingsValues(property_name, properties, index)

def __NextSetting(property_list, property_name):
  properties = getattr(SystemState.CameraState, property_list)
  index = getattr(SystemState.CameraState, property_name)
  if index < len(properties) - 1:
    index += 1
  else:
    index = 0
  __ProcessSettingsValues(property_name, properties, index)

def __CurrentSetting(property_list, property_name):
  # Shortens code.
  properties = getattr(SystemState.CameraState, property_list)
  index = getattr(SystemState.CameraState, property_name)
  __ProcessSettingsValues(property_name, properties, index)

def __ProcessSettingsValues(property_name, properties, index):
  """Corrects settings values to auto if they equal zero."""
  property_value = properties[index]
  setattr(SystemState.camera, property_name, property_value)
  setattr(SystemState.CameraState, property_name, index)
  property_type = type(property_value)

  # Defaults all values of zero to the word auto.
  if property_value == 0 and property_type is not bool:
    property_value = 'Auto'

  # Makes 'zoom' human readable.
  if property_type is tuple:
    if index == 0:
      index = None
    property_value = str(index)

  property_name = ' '.join(property_name.split('_'))
  __WriteSettingsTitle(property_name)
  __WriteSettingsValue(property_value)


def __WriteSettingsValue(text):
  """Writes the current value of the setting being manipulated."""
  TextWriter.Write(
    state=SystemState,
    text=str(text).title(),
    position=(160, 110),
    centered=True,
    size=20,
    permatext=True,
    color=(57, 255, 20)
  )


def __WriteSettingsTitle(text):
  """Writes the name of the setting being manipulated."""
  TextWriter.Write(
    state=SystemState,
    text=str(text).title(),
    position=(160, 10),
    centered=True,
    size=25,
    permatext=True,
    color=(57, 255, 20)
  )

def __ProcessLeftArrow():
  """Processes the left arrow button while in a setting."""
  if SystemState.CameraState.setting == 'image_effect':
    __PreviousSetting('image_effect_values', 'image_effect')
  elif SystemState.CameraState.setting == 'iso':
    __PreviousSetting('iso_values', 'iso')
  elif SystemState.CameraState.setting == 'rotation':
    __PreviousSetting('rotation_values', 'rotation')
  elif SystemState.CameraState.setting == 'brightness':
    __PreviousSetting('brightness_values', 'brightness')
  elif SystemState.CameraState.setting == 'saturation':
    __PreviousSetting('saturation_values', 'saturation')
  elif SystemState.CameraState.setting == 'contrast':
    __PreviousSetting('contrast_values', 'contrast')
  elif SystemState.CameraState.setting == 'sharpness':
    __PreviousSetting('sharpness_values', 'sharpness')
  elif SystemState.CameraState.setting == 'zoom':
    __PreviousSetting('zoom_values', 'zoom')
  elif SystemState.CameraState.setting == 'meter_mode':
    __PreviousSetting('meter_mode_values', 'meter_mode')
  elif SystemState.CameraState.setting == 'awb_mode':
    __PreviousSetting('awb_mode_values', 'awb_mode')
  elif SystemState.CameraState.setting == 'shutter_speed':
    __PreviousSetting('shutter_speed_values', 'shutter_speed')
  elif SystemState.CameraState.setting == 'exposure_mode':
    __PreviousSetting('exposure_mode_values', 'exposure_mode')
  elif SystemState.screen_mode == 3:
    if SystemState.CameraState.photo_count > 0:
      PreviousPhoto()

def __ProcessRightArrow():
  """Processes the right arrow button while in a setting."""
  if SystemState.CameraState.setting == 'image_effect':
    __NextSetting('image_effect_values', 'image_effect')
  elif SystemState.CameraState.setting == 'iso':
    __NextSetting('iso_values', 'iso')
  elif SystemState.CameraState.setting == 'rotation':
    __NextSetting('rotation_values', 'rotation')
  elif SystemState.CameraState.setting == 'brightness':
    __NextSetting('brightness_values', 'brightness')
  elif SystemState.CameraState.setting == 'saturation':
    __NextSetting('saturation_values', 'saturation')
  elif SystemState.CameraState.setting == 'contrast':
    __NextSetting('contrast_values', 'contrast')
  elif SystemState.CameraState.setting == 'sharpness':
    __NextSetting('sharpness_values', 'sharpness')
  elif SystemState.CameraState.setting == 'zoom':
    __NextSetting('zoom_values', 'zoom')
  elif SystemState.CameraState.setting == 'meter_mode':
    __NextSetting('meter_mode_values', 'meter_mode')
  elif SystemState.CameraState.setting == 'awb_mode':
    __NextSetting('awb_mode_values', 'awb_mode')
  elif SystemState.CameraState.setting == 'shutter_speed':
    __NextSetting('shutter_speed_values', 'shutter_speed')
  elif SystemState.CameraState.setting == 'exposure_mode':
    __NextSetting('exposure_mode_values', 'exposure_mode')
  elif SystemState.screen_mode == 3:
    if SystemState.CameraState.photo_count > 0:
      NextPhoto()

def CallTakePhoto():
  """Takes a preview photo with the camera. """

  # Only if the flash is enabled will the flash turn on.
  if SystemState.CameraState.flash_enabled == True:
    CallFlash() 
  # Grabs the timestamp of when the photo was taken.  
  SystemState.CameraState.photo_time = str(int(time.time()))
  file_name = SystemState.CameraState.preview_path + 'PREVIEW-' + SystemState.CameraState.photo_time + '.jpeg'
  SystemState.camera.capture(file_name, use_video_port=True, splitter_port=1,  format='jpeg')
  thread = threading.Thread(target=TakePhoto)
  thread.start()
  ShowPhoto(file_name)
  thread.join()

def TakePhoto():
  """Takes a high res photo with the camera."""
  file_name = SystemState.CameraState.photo_path + SystemState.CameraState.photo_time + '.jpeg'
  SystemState.camera.resolution = (2592, 1944)
  SystemState.camera.capture(file_name, use_video_port=False, format='jpeg')
  SystemState.camera.resolution = (320, 240)

def Flash():
  """Turns on the flash light on the front of the camera."""
  time.sleep(0)
  RPi.GPIO.output(7, True)
  time.sleep(0.150)
  RPi.GPIO.output(7, False)

def CallFlash():
  """Calls the flash function in a thread."""
  thread = threading.Thread(target=Flash)
  thread.setDaemon(True)
  thread.start()

def OpenAlbum():
  """Opens the photos folder."""
 
  path = SystemState.CameraState.preview_path
  SystemState.CameraState.photo_archive = os.listdir(path)
  SystemState.CameraState.photo_archive = [os.path.join(path, pic) for pic in SystemState.CameraState.photo_archive]
  SystemState.CameraState.photo_archive = sorted(SystemState.CameraState.photo_archive)
  SystemState.CameraState.photo_count = len(SystemState.CameraState.photo_archive)
  SystemState.CameraState.album = True

  #If there is a picture in there.
  if SystemState.CameraState.photo_count > 0:
    #If that photo is in the list, go to that photo. If not, go to the last photo.
    if SystemState.CameraState.current_photo in SystemState.CameraState.photo_archive:
      SystemState.CameraState.photo_index = SystemState.CameraState.photo_archive.index(SystemState.CameraState.current_photo)
    else:
      SystemState.CameraState.photo_index = SystemState.CameraState.photo_count - 1
    ShowPhoto(file_index=SystemState.CameraState.photo_index)

  else:
    TextWriter.Write(
        state=SystemState, 
        text='No Pictures', 
        position=(95, 100),
        permatext=True,
        size=20
    )

def NextPhoto():
  """Switches to the next photo in the photo archive."""
  if SystemState.CameraState.photo_index < SystemState.CameraState.photo_count - 1:
    SystemState.CameraState.photo_index += 1
  else:
    SystemState.CameraState.photo_index = 0
  file_name = SystemState.CameraState.photo_archive[SystemState.CameraState.photo_index]
  SystemState.CameraState.photo_tally = str(SystemState.CameraState.photo_index + 1) + '/' + str(SystemState.CameraState.photo_count)
  ShowPhoto(file_name)
  

def PreviousPhoto():
  """Switches to the previous photo in the photo archive."""
  if SystemState.CameraState.photo_index > 0:
    SystemState.CameraState.photo_index -= 1
  else:
    SystemState.CameraState.photo_index = SystemState.CameraState.photo_count - 1

  file_name = SystemState.CameraState.photo_archive[SystemState.CameraState.photo_index]
  SystemState.CameraState.photo_tally = str(SystemState.CameraState.photo_index + 1) + '/' + str(SystemState.CameraState.photo_count)
  ShowPhoto(file_name)
  

def BlitImage(file_name, pygame, screen):
  """Stamps the photo on the screen object."""
  try:
    raw_image = pygame.image.load(file_name)
    scaled_image = pygame.transform.scale(raw_image, (320, 240))
    scaled_x = (320 - scaled_image.get_width()) / 2
    scaled_y = (240 - scaled_image.get_height()) / 2
    screen.blit(scaled_image, (scaled_x, scaled_y))
  except:
    screen.fill(0)
    TextWriter.Write(
        state=SystemState, 
        text='Unsupported Format',
        color=(255, 0, 0),
        position=(70, 100), 
        size=20
    )

def DeletePhoto():
  """Deletes a selected photo."""
  preview_image = SystemState.CameraState.current_photo
  full_image = ''.join(preview_image.split('.preview/PREVIEW-'))
  try:
    os.remove(preview_image)
  except: # TODO:print that preview couldn't be removed.
    print "Couldn't remove preview image" 
  
  try:
    SystemState.CameraState.photo_archive.remove(preview_image)
  except: # TODO: print that file was not removed from library.
    print "Couldn't remove from library"
  
  try:
    os.remove(full_image)
  except: # TODO: print that image not removed.
    print "Image not removed"


def ShowPhoto(file_name=None, file_index=None):
  """Displays a photo onscreen."""

  if file_name == None:
    SystemState.CameraState.current_photo = SystemState.CameraState.photo_archive[file_index]
    file_name = SystemState.CameraState.current_photo
  else:
    SystemState.CameraState.current_photo = file_name

  pygame = SystemState.pygame
  screen = SystemState.screen
  BlitImage(file_name, pygame, screen)

  if SystemState.CameraState.photo_archive != None: 
    if SystemState.screen_mode == 3:
      # Remove 'PREVIEW-' and path leaving just unix time.
      utime_string = os.path.basename(file_name).split('-')[-1].split('.')[0]
      timestamp = time.ctime(int(utime_string))

      # Writing the time and position of the photo on the screen.
      TextWriter.Write(
         state=SystemState, 
         text=timestamp, 
         position=(90, 225), 
          size=12
      )
      TextWriter.Write(
        state=SystemState, 
        text=SystemState.CameraState.photo_tally, 
        position=(135, 18), 
        size=20
      )
    elif SystemState.screen_mode != 3 and SystemState.CameraState.album == False:
      pygame.display.update()
      time.sleep(2)

def Main():
  """Runs once the user has entered the application."""

  pygame = SystemState.pygame
  while SystemState.application == 'camera':
    Events.CheckEvents()
    if SystemState.screen_mode in (1, 2, 5, 6):
      SystemState.CameraState.camera_stream = True
    else:
      SystemState.CameraState.camera_stream = False

    if SystemState.CameraState.camera_stream == True:
      # Button on RPi.GPIO 8
      if not RPi.GPIO.input(8):
        CallTakePhoto()

      SystemState.CameraState.stream = io.BytesIO() # Capture into in-memory stream
      SystemState.camera.capture(SystemState.CameraState.stream, use_video_port=True, splitter_port=0, format='rgb')
      SystemState.CameraState.stream.seek(0)
      SystemState.CameraState.stream.readinto(SystemState.rgb)  # stream -> YUV buffer
      SystemState.CameraState.stream.close()
      SystemState.img = SystemState.pygame.image.frombuffer(SystemState.rgb[0: (320 * 240 * 3)], (320, 240), 'RGB' )
      xa = (320 - SystemState.img.get_width() ) / 2
      ya = (240 - SystemState.img.get_height()) / 2
      Screen.RefreshScreen(image=SystemState.img, wx=xa, wy=ya)
