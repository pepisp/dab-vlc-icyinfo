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
#Organization: Wroclaw University of Technology

import re
import asyncio
import sys
import functools
import signal
import os


DEBUG=1

test_str = u"In: [   -==|==    ]      [0x7f1380004948] access_http access debug: New Title=Pianochocolate - Jean Honeymoon - Bang Bang (Pianochocolate Remix)\nIn: [   -==|==    ]      [0x7f1380004948] access_http access debug: New Title=Pianochocolate - Jean Honeymoon - Bang Bang (Pianochocolate Remix)\nIn: [     -|      ]      [0x7f1380004948] access_http access debug: New Title=Nuclear Cowboys - Nuclear Cowboys - A Morning In The City\nIn: [ -====|====- ]      [0x7f1380004948] access_http access debug: New Title=CloZee - Colossal\nIn: [  ====|====  ]      [0x7f1380004948] access_http access debug: New Title=Steady Hussle - Stick Around\nIn: [ -====|===== ]      [0x7f1380004948] access_http access debug: New Title=Meltin' Kolcha - Reflexions Faites\nIn: [    ==|      ]      [0x7f1380004948] access_http access debug: New Title=Michael Ellis - Half a Million (Tell me what it's like)\nIn: [  ====|====  ]      [0x7f1380004948] access_http access debug: New Title=(null)\nIn: [     =|-     ]      [0x7f1380004948] access_http access debug: New Title=Wasaru - Can we speak\nIn: [!=====|======]      [0x7f1380004948] access_http access debug: New Title=K4MMERER - Sunrise\nIn: [  ====|===   ]      [0x7f1380004948] access_http access debug: New Title=Pianochocolate - Jean Honeymoon - Bang Bang (Pianochocolate Remix)\nIn: [      |      ]      [0x7f1380004948] access_http access debug: New Title=Nuclear Cowboys - Nuclear Cowboys - A Morning In The City\n\n"

def ask_exit(signame):
    print("got signal %s: exit" % signame)
    loop.stop()

def get_from_stdin(loop,re_comp,dls_queue,vlc_lock):
    line=sys.stdin.readline()
    meta_text=re.search(re_comp,line)
    if meta_text:
        print("Now on-air:")
        print(meta_text.groups()[0])
        try:
            dls_queue.get_nowait()              #Empty the queue, new data is comming...
        except:
            print("queue was empty")
        finally:
            print('Trying to put on queue...')
            print(dls_queue.full())
            dls_queue.put_nowait(meta_text.groups()[0])
            print(dls_queue.full())
            print("text on queue")
            if vlc_lock.locked():
                vlc_lock.release()
 



@asyncio.coroutine         
def send_dls_text(dls_file,dls_queue):
    while 1:
        print('DLS sent')
        print(dls_queue.full())
        new_text=yield from dls_queue.get()
        print(new_text)
        with open(dls_file,'w') as dls_f:
            dls_f.write(new_text)
        
@asyncio.coroutine
def put_default_dls(vlc_lock,dls_queue,dls_file,dls_default_file):
    if not vlc_lock.locked():
        yield from vlc_lock.acquire()
        
    while 1:
        yield from asyncio.sleep(30)
        if vlc_lock.locked():
            try:
                dls_queue.get_nowait()              #Empty the queue, new data is comming...
            except:
                print("queue was empty")
            finally:
                print('Trying to put on queue...')
                print(dls_queue.full())
                with open(dls_default_file,'r') as dls_def_f:
                    default_text=dls_def_f.readline()
                with open(dls_file,'w') as dls_f:
                    dls_f.write(default_text)
                print(dls_queue.full())
                print("Default text on queue")    
        else:
            yield from vlc_lock.acquire()
            
             
if __name__=='__main__':
    
    
    if len(sys.argv) < 3:
        print("Please specify dls output file, and file containing default text")
        sys.exit(1)

    
    re_icy= re.compile(r'New Title=\(null\)|New Title=(.+)')
#     meta_text=re.search(re_icy,test_str)
#     print(meta_text.groups()[0])
    dls_file = sys.argv[1]
    dls_default_file=sys.argv[2]
    
    loop=asyncio.get_event_loop()
    vlc_lock=asyncio.Lock(loop=loop)
    dls_queue=asyncio.Queue(1)
    
    
    loop.add_reader(sys.stdin,functools.partial(get_from_stdin,loop,re_icy,dls_queue,vlc_lock))
    
    
    
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                            functools.partial(ask_exit, signame))

    print("Event loop running forever, press Ctrl+C to interrupt.")
    print("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())
    
    dls_send_task=loop.create_task(send_dls_text(dls_file, dls_queue))
    default_text=loop.create_task(put_default_dls(vlc_lock,dls_queue,dls_file,dls_default_file))
    tasks=(dls_send_task,default_text)
    
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    finally:
        print('Going down...')
        loop.close()    

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

