# encoding: utf-8

import time
from selenium import webdriver
import time
from PIL import Image


driver = webdriver.PhantomJS(executable_path = './phantomjs')

#driver.get('http://pobedafilm.ru/card/?f=chuzhoj-zavet&d=2017-05-27&t=11:05&g=1')
driver.get('http://pobedafilm.ru/card/?f=piraty-karibskogo-morya-mertvecy-ne-rasskazyvayut-skazki-imx&d=2017-05-27&t=13:55&g=1')

time.sleep(1)

e2 = driver.find_element_by_xpath('//*[@id="cb"]')
loc2 = e2.location

e = driver.find_element_by_css_selector("body > div.seat")
loc = e.location
size = e.size
print loc, size
driver.save_screenshot('out.png')

img = Image.open("out.png")
width, height = img.size
print img.size
area = (loc2['x'], loc2['y'] - size['height']/2, loc2['x'] + size['width'], loc2['y'] + size['height']/2)
img = img.crop(area)
img.save("out2.png") 

driver.quit()

