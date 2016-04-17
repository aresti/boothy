import goprohero
import os
import time
import picamera
import pygame
import datetime
import urllib
import re
import wget
import settings
import itertools
import lamp
import button
import shutil

from pygame.locals import *

class PhotoBooth():

    def __init__(self, logger, storage_volume, 
             photo_mode='still', cntdwn=3, striplength=4, exit=False):
        self.photo_mode = photo_mode
        self.cntdwn = cntdwn
        self.striplength = striplength
        self.logger = logger
        self.storage_volume = storage_volume
        self.exit = exit
        self.font_paths = {}
        for f in settings.fonts:
            self.font_paths[f] = pygame.font.match_font(settings.fonts[f])
        
        self.camera_init()
        self.pygame_init()
        self.gopro_init()
        self.lamp_init()
        self.button_init()

    def filecopy_init(self):
        if not os.path.exists(self.storage_volume):
            os.makedirs(self.storage_volume)
            self.logger.info('Static dir created at %s' %(self.storage_volume))

    def camera_init(self):
        self.camera = picamera.PiCamera()
        self.camera.vflip = True
        self.camera.start_preview()
        self.camera.preview.alpha = 75
        self.logger.info('PiCamera initialised')

    def lamp_init(self):
        self.low_lamp = lamp.Lamp(settings.gpio['low_lamp'])
        self.high_lamp = lamp.Lamp(settings.gpio['high_lamp'])

    def button_init(self):
        self.photo_button = button.Button(settings.gpio['photo_button'])
        self.video_button = button.Button(settings.gpio['video_button'])

    def pygame_init(self):
        pygame.init()
        self.display_info = pygame.display.Info()
        self.display_w, self.display_h = self.display_info.current_w, self.display_info.current_h
        self.display = pygame.display.set_mode((self.display_w,self.display_h),pygame.FULLSCREEN)
        self.logger.info('Pygame initialised')

    def gopro_init(self):
        self.gopro = goprohero.GoProHero(password=settings.gopro['passwd'])
        self.gopro.base_url = 'http://' + settings.gopro['ip']
        for command, value in settings.gopro['init']:
            self.logger.info('GoPro API call: %s, %s' %(command, value))
            self.gopro.command(command, value)
            time.sleep(2)
        status = self.gopro.status()
        self.logger.info('GoPro status: %s' %(status))
        if status['npics'] or status['nvids']:
            self.logger.info('Files found on GoPro, deleting...')
            time.sleep(1)
            self.gopro.command('delete_all')    
        config = self.gopro.config()
        self.logger.info('GoPro initialised')
    

    def display_update(self, text, fsize=500):
        background = pygame.Surface(self.display.get_size())
        background = background.convert()
        background.fill((255, 255, 255))
        
        font = pygame.font.Font(self.font_paths['MAIN'], fsize)
        text_obj = font.render(str(text), 1, (0, 0, 0))
        textpos = text_obj.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        background.blit(text_obj, textpos)
    
        self.display.blit(background, (0, 0))
        pygame.display.flip()

    def home_screen(self):
        self.logger.info('Home screen loop started')
        w = self.display_w
        h = self.display_h
        screen1 = pygame.Surface(self.display.get_size())
        screen1 = screen1.convert()
        screen1.fill((255, 255, 255))

        title_font = pygame.font.Font(self.font_paths['MAIN'], int(h/4))
        title_text = title_font.render('Photo Booth', 1, (0,0,0))
        title_rect = title_text.get_rect()
        title_rect.centerx = screen1.get_rect().centerx
        title_rect.centery = screen1.get_rect().centery
        screen1.blit(title_text, title_rect)

        heart1 = pygame.transform.scale(pygame.image.load('static/heart-1.png'), (int(h/5), int(h/5)))
        heart2 = pygame.transform.scale(pygame.image.load('static/heart-2.png'), (int(h/6), int(h/6)))
        screen1.blit(heart1, (int(h/15),int(h/15)))
        screen1.blit(heart2, (int(h/4),int(h/7)))

        screen2 = screen1.copy()
        screen3 = screen1.copy()

        action_font = pygame.font.Font(self.font_paths['MAIN'], int(h/10))
    
        photo_action_text = action_font.render('Choose photos or video guestbook!', 1, (0,0,0))
        photo_action_rect = photo_action_text.get_rect()
        photo_action_rect.centerx = screen1.get_rect().centerx
        photo_action_rect.centery = screen1.get_rect().centery + (h/4)
        screen1.blit(photo_action_text, photo_action_rect) 
        
        screen_order = [screen1, screen3]
        for i, s in enumerate(itertools.cycle(screen_order)):
            event = pygame.event.poll()
            pygame.event.clear()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.logger.info('Escape key registered')
                    self.filecopy.exit = True
                    self.filecopy.join()
                    return -1
                elif event.key == pygame.K_0:
                    return 0
                elif event.key == pygame.K_1:
                    return 1
            self.display.blit(s, (0, 0))
            pygame.display.flip()
            if i%2 == 1:
                time.sleep(0.5)
            else:
                time.sleep(2)

    def preview_fade(self, end_alpha, sec):
        preview = self.camera.preview
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

    def countdown(self, n):
        for each in range(n, 0, -1):
            self.display_update(each)
            time.sleep(1)

    def photo_run(self):
        self.logger.info('Photo run started: striplength=%s, mode=%s' %(self.striplength, self.photo_mode))
        self.display_update('')
        self.preview_fade(125, 3) 
    
        self.gopro.command('mode', self.photo_mode)
        
        if self.photo_mode == 'burst':
            self.countdown(self.cntdwn)
            self.display_update('Capturing!', 200)
            self.gopro.command('record', 'on')
            self.time.sleep(4)

            for i, attempt in enumerate(range(100)):
                self.display_update('Processing' + '.'*(i%6), 200)
                time.sleep(1)
                if self.gopro.status()['npics'] == 30:
                    break    
        elif self.photo_mode == 'still':
            for photo in range(self.striplength):
                self.display_update('Photo %i of %i' % (photo + 1, self.striplength), 200)
                time.sleep(2)
                self.countdown(self.cntdwn)
                self.gopro.command('record', 'on')
                self.display_update('Smile!', 300)
                time.sleep(3)

        self.display_update('Photos coming up!', 200)

        base_url = self.gopro.base_url + '/DCIM/100GOPRO/'
        matches = ''
        source = urllib.request.urlopen(base_url).read().decode()
        matches = re.findall('<a class="link" href="?\'?([^"\'>]*)', source)
        
        if self.photo_mode == 'still':
            download_list = matches
        elif self.photo_mode == 'burst':
            download_list = []    
            jump = int(round(30.0 / self.striplength))
            for n, photo in enumerate(range(0, 29, jump)):
                download_list.append(matches[photo])
        
        self.camera.preview.alpha = 0
        
        for f in download_list:    
            img_url = base_url + f
            self.logger.info('Attempting to download ' + img_url)
            download_result = wget.download(img_url)
            self.logger.info('Download result: ' + download_result)    
            img = pygame.transform.scale(pygame.image.load(f), (self.display_w, self.display_h))
            self.display.blit(img,(0,0))
            pygame.display.flip()
            shutil.move(f, self.storage_volume)

        self.logger.info('Attempting delete all from GoPro')
        self.gopro.command('delete_all')
        time.sleep(4)

        self.display_update('')
        self.preview_fade(75, 3)


    def video_run(self, record_time):    
        self.logger.info('Video run started')
        self.gopro.command('mode', 'video')
        time.sleep(1)

        self.display_update('Press any button to record', 100)
        self.logger.info('Recording initiated by user keypress')        

        pygame.event.wait()
        self.display_update('')
        self.preview_fade(200, 3)
        self.gopro.command('record', 'on')
    
        for n in range(record_time, 0, -1):
            self.display_update(n, 300)    
            time.sleep(1)
    
        self.logger.info('Recording stopped')
        self.gopro.command('record', 'off')
        time.sleep(1)
    
        self.display_update('Processing video', 200)

        base_url = self.gopro.base_url + '/DCIM/100GOPRO/'
        matches = ''
        source = urllib.request.urlopen(base_url).read().decode()
        matches = re.findall('<a class="link" href="?\'?([^"\'>]*)', source)
        download_list = [m for m in matches if m[-4:] == ".MP4"]
        
        self.camera.preview.alpha = 0
        
        for f in download_list:
            img_url = base_url + f
            self.logger.info('Attempting to download video ' + img_url)
            download_result = wget.download(img_url)
            self.logger.info('Download result: ' + download_result)
            shutil.move(f, self.storage_volume)
        
        self.logger.info('Attempting to delete all from GoPro')
        self.gopro.command('delete_all')
        time.sleep(4)

        self.display_update('')
        self.preview_fade(75, 3)
