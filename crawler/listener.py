
import logging
import time

from datetime import date
from watchdog.observers.polling import PollingObserver
from watchdog.events import LoggingEventHandler

from handler import CrawlerHandler

class Listener:
    ""
    ""

    def __init__(self, config):

        if 'path' not in config['listener']: 
            raise ValueError('Failed to provide filsystem path to watch.')
        self.path = config['listener']['path']

        self.config = config

        log_fn = ('%s_crawler.log' % date.today().isoformat())
        logging.basicConfig(filename=log_fn, level=logging.INFO,
                            format='[%(levelname)s] %(asctime)s : %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        logging.info('Watching path %s', self.path)

        self.observer = PollingObserver()

    def run(self): 
       
        logging.info('Running crawler ...')
        event_log_handler = LoggingEventHandler()
        event_crawl_handler = CrawlerHandler(self.config)
        self.observer.schedule(event_log_handler, self.path, recursive = True)
        self.observer.schedule(event_crawl_handler, self.path, recursive = True)
        self.observer.start()

        try: 
            while True:
                time.sleep(60)
        except: 
            self.observer.stop()

        self.observer.join()
