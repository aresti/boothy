#!/bin/env python2.7
# Photobooth by Andy Smith and Josh Quick 2016
# www.github.com/aresti/boothy.git

import sys
import argparse
import logging
import photobooth
import copy_queue
import time


def main():
	parser = argparse.ArgumentParser(description='Run Boothy...')
	parser.add_argument('--striplength', help='Number of photos to take', type=int, default=3)
	parser.add_argument('--mode', choices=['burst', 'still'], help='Choose the GoPro capture mode', default='still')
	parser.add_argument('--countdown', help='Length of countdown', type=int, default=3)
	parser.add_argument('--video_time', help='Length of video', type=int, default=45)
	args = parser.parse_args()

	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	handler = logging.FileHandler('boothy.log')
	handler.setLevel(logging.INFO)
	logger.addHandler(handler)
	logger.info('Boothy started')

	print """
	              ____
		 _[]_/____\__n_
		|_____.--.__()_|
		|LI  //# \\\\    |
		|    \\\\__//    |
		|     '--'     |
	        '--------------'

    Photobooth by Andy Smith and Josh Quick
	"""
	time.sleep(2)

	pb = photobooth.PhotoBooth(logger, args.mode, args.countdown, args.striplength)	
	pb.camera.start_preview()
	pb.camera.preview.alpha = 75

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
