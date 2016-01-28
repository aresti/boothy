import time
import picamera
import pygame
import datetime
import sys
import urllib2
import re
import wget
import goprohero
import settings
import argparse

from pygame.locals import *

font_paths = {}
for f in settings.fonts:
	font_paths[f] = pygame.font.match_font(settings.fonts[f])

def screen_update(screen, text, fsize=500):
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((255, 255, 255))
	
	font = pygame.font.Font(font_paths['MAIN'], fsize)
	text_obj = font.render(str(text), 1, (0, 0, 0))
	textpos = text_obj.get_rect()
	textpos.centerx = background.get_rect().centerx
	textpos.centery = background.get_rect().centery
	background.blit(text_obj, textpos)
	
	screen.blit(background, (0, 0))
	pygame.display.flip()


def preview_fade(preview, end_alpha, sec):
	delta = end_alpha - preview.alpha
	if delta == 0:
		return
	step_time = round(sec / abs(delta), 5)
	print(step_time)
	while preview.alpha != end_alpha:
		if delta > 0:
			preview.alpha = min(255, preview.alpha+5)
		else:
			preview.alpha = max(0, preview.alpha-5)
		time.sleep(step_time)

def countdown(n, screen):
	for each in range(n, 0, -1):
		screen_update(screen, each)
		time.sleep(1)

def main():	
	parser = argparse.ArgumentParser(description='Run Boothy...')
	parser.add_argument('--striplength', help='Number of photos to take', type=int, default=3)
	parser.add_argument('--mode', choices=['burst', 'still'], help='Choose the GoPro capture mode', default='burst')
	parser.add_argument('--countdown', help='Length of countdown', type=int, default=5)
	args = parser.parse_args()

	camera = picamera.PiCamera()
	camera.vflip = True

	pygame.init()
	screen_info = pygame.display.Info()
	w, h = screen_info.current_w, screen_info.current_h
	screen = pygame.display.set_mode((w,h),pygame.FULLSCREEN)

	gopro = goprohero.GoProHero(password=settings.gopro['passwd'])
	if gopro.status()['npics']:
		time.sleep(1)
		gopro.command('delete_all')	
		time.sleep(10)

	gopro.command('mode', '%s' %args.mode)
	time.sleep(1)
	assert gopro.status()['mode'] == args.mode
	
	camera.start_preview()
	camera.preview.alpha = 75

	pygame.event.clear()
	
	while True:
		screen_update(screen, 'Photo Booth', 250)

		pygame.event.wait()
		if pygame.key.get_pressed()[K_ESCAPE]:
			sys.exit()
		
		screen_update(screen, '')
		preview_fade(camera.preview, 125, 3) 
		
		if args.mode == 'burst':
			countdown(args.countdown, screen)
			screen_update(screen, 'Capturing!', 200)
			gopro.command('record', 'on')
			time.sleep(4)

			for i, attempt in enumerate(range(100)):
				screen_update(screen, 'Processing' + '.'*(i%6), 200)
				time.sleep(1)
				if gopro.status()['npics'] == 30:
					break	
		elif args.mode == 'still':
			for _ in range(args.striplength):
				countdown(args.countdown, screen)
				screen_update(screen, 'Cheese!', 200)
				time.sleep(1)
				gopro.command('record', 'on')
			time.sleep(2)
	
		screen_update(screen, 'Photos coming up!', 200)

		base_url = 'http://10.5.5.9:8080/DCIM/100GOPRO/'
		matches = ''
		object = urllib2.urlopen(base_url)
		source = '\n'.join(object.readlines())
		matches = re.findall('<a class="link" href="?\'?([^"\'>]*)', source)
		
		jump = int(round(30.0 / args.striplength))
		for n, photo in enumerate(range(0, 29, jump)):
			file_name = matches[photo]
			#screen_update(screen, 'Downloading %i/%i' %(n+1, args.striplength), 200)
			url = base_url + file_name
			download_result = wget.download(url)
			print download_result
			
			img = pygame.transform.scale(pygame.image.load(file_name), (w, h))
			screen.blit(img,(0,0))
			if n == 0:
				camera.preview.alpha = 0
			pygame.display.flip()
	
		gopro.command('delete_all')
		time.sleep(4)

		screen_update(screen, '')
		preview_fade(camera.preview, 75, 3)
		
		pygame.event.clear()
						
if __name__ == '__main__':
	main()
