# -*- coding: utf-8 -*
'''!
  @file  get_temp_press.py
  @brief  Get the sensor data by polling
  @details  Configure the sensor power mode and parameters (for compensating the calibrated temperature and relative humidity in gas measurement)
  @copyright  Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license  The MIT License (MIT)
  @author  [qsjhyy](yihuan.huang@dfrobot.com)
  @version  V1.0
  @date  2021-10-28
  @url  https://github.com/DFRobot/DFRobot_ENS160
'''
from __future__ import print_function
import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from DFRobot_ENS160 import *

'''
  # Select communication interface I2C, please comment out SPI interface. And vise versa.
  # I2C : For Fermion version, I2C communication address setting: 
  #         connect SDO pin to GND, I2C address is 0×52 now;
  #         connect SDO pin to VCC(3v3), I2C address is 0x53 now
  # SPI : Set up digital pin according to the on-board pin connected with SPI chip-select pin.
'''
sensor = DFRobot_ENS160_I2C(i2c_addr = 0x53, bus = 1)
# sensor = DFRobot_ENS160_SPI(cs=8, bus=0, dev=0, speed=2000000)


def setup():
  while (sensor.begin() == False):
    print ('Please check that the device is properly connected')
    time.sleep(3)
  print("sensor begin successfully!!!")

  '''
    # Configure power mode
    # mode Configurable power mode:
    #   ENS160_SLEEP_MODE: DEEP SLEEP mode (low power standby)
    #   ENS160_IDLE_MODE: IDLE mode (low-power)
    #   ENS160_STANDARD_MODE: STANDARD Gas Sensing Modes
  '''
  sensor.set_PWR_mode(ENS160_STANDARD_MODE)

  '''
    # Users write ambient temperature and relative humidity into ENS160 for calibration and compensation of the measured gas data.
    # ambient_temp Compensate the current ambient temperature, float type, unit: C
    # relative_humidity Compensate the current ambient humidity, float type, unit: %rH
  '''
  sensor.set_temp_and_hum(ambient_temp=25.00, relative_humidity=50.00)
  
  # TODO: not hardcode temperature and humidity levels, rather get them from the server or from other sensor's readings

def loop():

  '''
    # Get CO2 equivalent concentration calculated according to the detected data of VOCs and hydrogen (eCO2 – Equivalent CO2)
    # Return value range: 400–65000, unit: ppm
    # Five levels: Excellent(400 - 600), Good(600 - 800), Moderate(800 - 1000), 
    #               Poor(1000 - 1500), Unhealthy(> 1500)
  '''
  
  try:
    val = sensor.get_ECO2_ppm
  
    print("Carbon dioxide equivalent concentration : %u ppm" %(val))
    
    payload = {
        'service' :'LEMS',
        'LEMS_ID' :1,
        'sensor'  :'ENS160',
        'co2'     :val,
        'unit_co2':'ppm',
    }
    
    response = requests.post(web_server_url,json=payload)
    print('Status Code:', response.status_code)
    print('Response:',response.text)

  except RuntimeError as e:
    print('Error reading or posting CO2 value',e)

  time.sleep(10)
  
def is_connected(url):
  try:
    response = requests.get(url,timeout=5)
    return response.status_code==200
  except requests.RequestException:
    return False


if __name__ == "__main__":
  
  web_server_url = 'http://192.168.255.33:8385/json'
  
  # wait for network
  
  while not is_connected('https://www.google.com'):
    print("Waiting for network connectivity...")
    time.sleep(2)
  
  setup()
  
  while True:
    loop()
