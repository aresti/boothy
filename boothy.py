#!/bin/env python3.2
# Photobooth by Andy Smith and Josh Quick 2016
# www.github.com/aresti/boothy.git

import sys
import os
import argparse
import logging
import photobooth
import time

def main():
    parser = argparse.ArgumentParser(description='Run Boothy...')
    parser.add_argument('--striplength', help='Number of photos to take', 
                type=int, default=3)
    parser.add_argument('--mode', choices=['burst', 'still'], 
                help='Choose the GoPro capture mode', default='still')
    parser.add_argument('--countdown', help='Length of countdown', type=int, default=3)
    parser.add_argument('--video_time', help='Length of video', type=int, default=15)
    parser.add_argument('--storage_volume', help='Location to copy files to', 
                default='/media/pi/UNTITLED/BOOTHY_STORE')
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('boothy.log')
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.info('Boothy started')

    print("""
              ____
         _[]_/____\__n_
        |_____.--.__()_|
        |LI  //# \\\\    |
        |    \\\\__//    |
        |     '--'     |
        '--------------'

    Photobooth by Andy Smith and Josh Quick
    """)
    time.sleep(2)

    pb = photobooth.PhotoBooth(logger, args.storage_volume, args.mode, 
                   args.countdown, args.striplength)    

    while True:
        action = pb.home_screen()
        if action == 0:
            pb.photo_run()
        elif action == 1:
            pb.video_run(args.video_time)
        elif action == -1:
            sys.exit()
                        
if __name__ == '__main__':
    main()
