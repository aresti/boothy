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
import itertools

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

def home_screen(screen):
	screen1 = pygame.Surface(screen.get_size())
	screen1 = screen1.convert()
	screen1.fill((255, 255, 255))

	screen_info = pygame.display.Info()
	w, h = screen_info.current_w, screen_info.current_h
	
	title_font = pygame.font.Font(font_paths['MAIN'], h/4)
	title_text = title_font.render('Photo Booth', 1, (0,0,0))
	title_rect = title_text.get_rect()
	title_rect.centerx = screen1.get_rect().centerx
	title_rect.centery = screen1.get_rect().centery
	screen1.blit(title_text, title_rect)

	heart1 = pygame.transform.scale(pygame.image.load('static/heart-1.png'), (h/5, h/5))
	heart2 = pygame.transform.scale(pygame.image.load('static/heart-2.png'), (h/6, h/6))
	screen1.blit(heart1, (h/15,h/15))
	screen1.blit(heart2, (h/4,h/7))

	screen2 = screen1.copy()
	screen3 = screen1.copy()

	action_font = pygame.font.Font(font_paths['MAIN'], h/10)
	
	photo_action_text = action_font.render('Left button for photos', 1, (0,0,0))
	photo_action_rect = photo_action_text.get_rect()
	photo_action_rect.centerx = screen1.get_rect().centerx
	photo_action_rect.centery = screen1.get_rect().centery + (h/4)
	screen1.blit(photo_action_text, photo_action_rect) 
	
	video_action_text = action_font.render('Right button for video', 1, (0,0,0))
	video_action_rect = video_action_text.get_rect()
	video_action_rect.centerx = screen1.get_rect().centerx
	video_action_rect.centery = screen1.get_rect().centery + (h/4)
	screen2.blit(video_action_text, video_action_rect) 

	screen_order = [screen1, screen3, screen2, screen3]
	for s in itertools.cycle(screen_order):
		event = pygame.event.poll()
		if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			sys.exit()
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_0:
			return
		screen.blit(s, (0, 0))
		pygame.display.flip()
		time.sleep(1.5)

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
		home_screen(screen)

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
		
		if args.mode == 'still':
			download_list = matches
		elif args.mode == 'burst':
			download_list = []	
			jump = int(round(30.0 / args.striplength))
			for n, photo in enumerate(range(0, 29, jump)):
				download_list.append(matches[photo])
		
		camera.preview.alpha = 0
		
		for file_name in download_list:	
			url = base_url + file_name
			download_result = wget.download(url)
			print download_result
			
			img = pygame.transform.scale(pygame.image.load(file_name), (w, h))
			screen.blit(img,(0,0))
			pygame.display.flip()
	
		gopro.command('delete_all')
		time.sleep(4)

		screen_update(screen, '')
		preview_fade(camera.preview, 75, 3)
		pygame.event.clear()
						
if __name__ == '__main__':
	main()
