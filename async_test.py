#!/usr/bin/python3

import re
import asyncio
import sys
import functools
import signal
import os

def ask_exit(signame):
    print("got signal %s: exit" % signame)
    loop.stop()

def get_from_stdin(re_comp):
    line=sys.stdin.readline()
    meta_text=re.search(re_comp,line)
    if meta_text:
        print(meta_text.groups()[0])



@asyncio.coroutine         
def send_dls_text(loop):
    while 1: 
        print('DLS sent')
        yield from asyncio.sleep(5)
        
    
             
if __name__=='__main__':
    
    
    if len(sys.argv) < 3:
        print("Please specify dls output file, and file containing default text")
        sys.exit(1)

    
    re_icy= re.compile(r'New Title=\(null\)|New Title=(.+)')
#     meta_text=re.search(re_icy,test_str)
#     print(meta_text.groups()[0])
    dls_file = sys.argv[1]

    
    loop=asyncio.get_event_loop()
   
    loop.add_reader(sys.stdin,functools.partial(get_from_stdin,re_icy))
    dls_send_task=loop.create_task(send_dls_text(loop))
    
    
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                            functools.partial(ask_exit, signame))

    print("Event loop running forever, press Ctrl+C to interrupt.")
    print("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())

    try:
        loop.run_until_complete(asyncio.wait_for(dls_send_task,None))
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

