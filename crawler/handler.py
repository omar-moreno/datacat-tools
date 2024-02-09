

import watchdog.events

from CDMSDataCatalog import CDMSDataCatalog
from crawler import Crawler

class CrawlerHandler(watchdog.events.FileSystemEventHandler):

    def __init__(self, config): 
        if 'config' in config['catalog']:
            dc_config = config['catalog']['config']
        dc = CDMSDataCatalog(config_file=dc_config)
        crawler = Crawler(dc, config)
    
    def on_any_event(self, event):
        if event.event_type == 'deleted' or event.event_type == 'created':
            crawler.crawl(event.src_path)
            print('Event type %s' % event.event_type)
            print('Is Directory %s' % event.is_directory)
            print('Path %s' % event.src_path)

    

