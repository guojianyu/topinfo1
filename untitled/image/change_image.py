#coding=utf-8
import os  #打开文件时需要
from PIL import Image
import re

width=256
depth=256
#print list
count=0

path = os.getcwd()
flag = 'red'

a = os.path.join(path,'first','%s1.jpg')%flag
img=Image.open(a)
w,h=img.size
out = img.resize((128, 128))#resize成128*128像素大小。
out.save('test.jpg')

a = os.path.join(path,'first','%s2.jpg')%flag
img=Image.open(a)
w,h=img.size
out = img.resize((128, 128))#resize成128*128像素大小。
out.save('test1.jpg')
#iphone 5的分辨率为1136*640，如果图片分辨率超过这个值，进行图片的等比例压缩




