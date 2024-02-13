
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

        if 'paths' not in config['listener']: 
            raise ValueError('Failed to provide filsystem path to watch.')
        self.paths = config['listener']['paths']

        self.config = config

        log_fn = ('%s_crawler.log' % date.today().isoformat())
        logging.basicConfig(filename=log_fn, level=logging.INFO,
                            format='[%(levelname)s] %(asctime)s : %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        for path in self.paths: 
            logging.info('Watching path %s', path)

        self.observer = PollingObserver()

    def run(self): 
       
        logging.info('Running crawler ...')
        event_log_handler = LoggingEventHandler()
        event_crawl_handler = CrawlerHandler(self.config)
        for path in self.paths: 
            self.observer.schedule(event_log_handler, path, recursive = True)
            self.observer.schedule(event_crawl_handler, path, recursive = True)
        self.observer.start()

        try: 
            while True:
                time.sleep(60)
        except: 
            self.observer.stop()

        self.observer.join()
