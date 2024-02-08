
import logging
import time

from datetime import date
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

class Listener:
    ""
    ""

    def __init__(self, config):

        if 'path' not in config['listener']: 
            raise ValueError('Failed to provide filsystem path to watch.')
        self.path = config['listener']['path']

        log_fn = ('%s_crawler.log' % date.today().isoformat())
        logging.basicConfig(filename=log_fn, level=logging.INFO,
                            format='[%(levelname)s] %(asctime)s : %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        logging.info('Watching path %s', self.path)

        self.observer = Observer()

    def run(self): 
        
        print('Running')
        event_handler = LoggingEventHandler()
        self.observer.schedule(event_handler, self.path, recursive = True)
        self.observer.start()

        try: 
            while True:
                print('in loop')
                time.sleep(5)
        except: 
            self.observer.stop()

        self.observer.join()
