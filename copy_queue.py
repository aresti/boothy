import os
import sys
import shutil
import threading
import Queue
import glob
import time

class FileCopy(threading.Thread):

	def __init__(self, queue, files, dir):
		threading.Thread.__init__(self)
		self.queue = queue
		self.dir = dir
		self.files = files

	def run(self):
		# Copy files then add them to the queue
		for f in self.files:
			exists_path = self.dir + f.split('/')[-1]
			if os.path.exists(exists_path):
				i = 1
				while True:
					a = exists_path + '(%s)' %i
					if not os.path.exists(a):
						shutil.move(f, a)
						print 'Completed move', a
						break
					else:
						i += 1
			else:
				shutil.move(f, self.dir)
				print 'Completed move', f
			self.queue.put(f)
		self.queue.put(None)  # signal completion

def main():
	#volume = '/media/UNTITLED/' + 'BOOTHY_STORE'
	watch_dir = '/Users/josh/Downloads/boothy/'
	volume = '/Users/josh/Downloads/boothy/' + 'test/'	
	if not os.path.exists(volume):
		os.makedirs(volume)

	try:
		while True:
			files = glob.glob(watch_dir + '*jpg')
			if files:
				queue = Queue.Queue()
				print 'Copying %s %s' %(len(files), ('file' if len(files) == 1 else 'files'))
				copythread = FileCopy(queue, files, volume)
				copythread.start()
				while True:
					x = queue.get()
					if x is None:
						break
				copythread.join()
				print 'Completed batch...'
			time.sleep(1)
	except KeyboardInterrupt:
		pass

if __name__ == '__main__':
	main()
