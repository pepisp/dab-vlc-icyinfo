#!/usr/bin/python3
#
# This script parses the dab-enc VLC standard output and
# extracts ICY info for the mot-encoder.
#
# Usage:
# dab-enc -v <opitons> | mot-icyinfo-vlc.py file.dls file-with-default.dls
#
# the file-with-default.dls contains DLS text to be sent when there
# is no ICY info
#
#This script has been written on basis of file from Opendigitalradio/dab-scripts/icy-info.py
#https://github.com/Opendigitalradio/dab-scripts
#
#Author: Piotr Piotrowski
#Organization: Wroclaw University of Technologie

import re
import asyncio
import sys

DEBUG=1

test_str = u"In: [   -==|==    ]      [0x7f1380004948] access_http access debug: New Title=Pianochocolate - Jean Honeymoon - Bang Bang (Pianochocolate Remix)\nIn: [   -==|==    ]      [0x7f1380004948] access_http access debug: New Title=Pianochocolate - Jean Honeymoon - Bang Bang (Pianochocolate Remix)\nIn: [     -|      ]      [0x7f1380004948] access_http access debug: New Title=Nuclear Cowboys - Nuclear Cowboys - A Morning In The City\nIn: [ -====|====- ]      [0x7f1380004948] access_http access debug: New Title=CloZee - Colossal\nIn: [  ====|====  ]      [0x7f1380004948] access_http access debug: New Title=Steady Hussle - Stick Around\nIn: [ -====|===== ]      [0x7f1380004948] access_http access debug: New Title=Meltin' Kolcha - Reflexions Faites\nIn: [    ==|      ]      [0x7f1380004948] access_http access debug: New Title=Michael Ellis - Half a Million (Tell me what it's like)\nIn: [  ====|====  ]      [0x7f1380004948] access_http access debug: New Title=(null)\nIn: [     =|-     ]      [0x7f1380004948] access_http access debug: New Title=Wasaru - Can we speak\nIn: [!=====|======]      [0x7f1380004948] access_http access debug: New Title=K4MMERER - Sunrise\nIn: [  ====|===   ]      [0x7f1380004948] access_http access debug: New Title=Pianochocolate - Jean Honeymoon - Bang Bang (Pianochocolate Remix)\nIn: [      |      ]      [0x7f1380004948] access_http access debug: New Title=Nuclear Cowboys - Nuclear Cowboys - A Morning In The City\n\n"


def get_from_stdin(re_comp):
    line=sys.stdin.readline()
    meta_text=re.search(re_comp,line)
    if meta_text:
        print("Now on-air:")
        print(meta_text.groups()[0])

if __name__=='__main__':
    
    
    if len(sys.argv) < 3:
        print("Please specify dls output file, and file containing default text")
        sys.exit(1)

    dls_file = sys.argv[1]
    re_icy= re.compile(r'New Title=\(null\)|New Title=(.+)')
#     meta_text=re.search(re_icy,test_str)
#     print(meta_text.groups()[0])
    loop=asyncio.get_event_loop()
    
    loop.add_reader(sys.stdin,get_from_stdin,re_icy)
#     print('start')
#     while True:
#         line=sys.stdin.readline()
#         meta_text=re.search(re_icy,line)
#         if meta_text:
#             print("Now on-air:")
#             print(meta_text.groups()[0])
    loop.run_forever()    
    print('stop')   

# def new_dlstext(text):
#     if text.strip() == "":
#         try:
#             fd = open(default_textfile, "r")
#             text = fd.read().strip()
#             fd.close()
#         except Exception as e:
#             print("Could not read default text from {}: {}".format(default_textfile, e))
# 
#     print("New Text: {}".format(text))
# 
#     fd = open(dls_file, "w")
#     fd.write(text)
#     fd.close()
# 
# wait_timeout = 5
# nodls_timeout = 0
# 
# 
# while True:
#     # readline is blocking, therefore we cannot send a default text
#     # after some timeout
#     new_data = sys.stdin.readline()
#     if not new_data:
#         break
# 
#     match = re_icy.match(new_data)
# 
#     if match:
#         artist_title = match.groups()[0]
#         new_dlstext(artist_title)
#     else:
#         print("{}".format(new_data.strip()))
# 
# if False:
#     # The select call creates a one ICY delay, and it's not clear why...
#     while True:
#         rfds, wfds, efds = select.select( [sys.stdin], [], [], wait_timeout)
# 
#         if rfds:
#             # new data available on stdin
#             print("SELECT !")
#             new_data = sys.stdin.readline()
#             print("DATA ! {}".format(new_data))
# 
#             if not new_data:
#                 break
# 
#             match = re_icy.match(new_data)
# 
#             if match:
#                 artist_title = match.groups()[0]
#                 new_dlstext(artist_title)
#             else:
#                 print("{}".format(new_data.strip()))
# 
#         else:
#             # timeout reading stdin
#             nodls_timeout += 1
# 
#             if nodls_timeout == 100:
#                 new_dlstext("")
#                 nodls_timeout = 0
# 
#         time.sleep(.1)

