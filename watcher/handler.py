
import os
import watchdog.events

from CDMSDataCatalog import CDMSDataCatalog
from crawler.crawler import Crawler

class CrawlerHandler(watchdog.events.FileSystemEventHandler):

    def __init__(self, config): 
        if 'config' in config['catalog']:
            dc_config = config['catalog']['config']
        dc = CDMSDataCatalog(config_file=dc_config)
        self.crawler = Crawler(dc, config)
    
    def on_any_event(self, event):
        if event.event_type != 'moved':
            if (event.event_type == 'modified') & event.is_directory: return
            path = event.src_path
            path = os.path.dirname(path[path.find('/CDMS'):])
            self.crawler.crawl(path)

    

