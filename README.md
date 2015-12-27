1. **Description**
  - This is the camera application written for the Raspberry Pi's camera.

2. **Requirements**
  - Raspberry Pi Model B+ or more (https://www.adafruit.com/products/2358)
  - Adafruit 2.8in PiTFT (https://www.adafruit.com/products/1601)
  - Raspberry Pi Camera (https://www.adafruit.com/products/1367)
  - Adafruit Powerboost 1000C (Optional) (https://www.adafruit.com/products/2465)
  - Adafruit Lipo Battery 500mAh (Optional) (https://www.adafruit.com/products/1578)
  - The cobblr software (https://github.com/RoboQYD/cobblr)

3. **Installation**
  1. Clone the repository.
  2. Enter the cobblr-camera directory.
  3. Run "setup.py install <path>" where <path> is the location of the cobblr file.
  4. Enter the cobblr/config directory.
  5. Open "cobblr.yaml" and add "-camera" to the list of applications.
  6. Run cobblr.

4. **Notes**

  - If you want to automatically enter the camera application, change the cobblr.yaml
    startup application to "camera".
