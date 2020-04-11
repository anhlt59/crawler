# -*- coding: utf-8 -*-
import os


LOGCONF = os.path.join(os.path.dirname(__file__), '..', '..', 'logging.ini'),

BOT_NAME = 'ssg_new_crawler'

SPIDER_MODULES = ['ssg_new_crawler.spiders']
NEWSPIDER_MODULE = 'ssg_new_crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5
DOWNLOAD_TIMEOUT = 10
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
#SPIDER_MIDDLEWARES = {
#    'ssg_new_crawler.middlewares.SsgNewCrawlerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
#DOWNLOADER_MIDDLEWARES = {
#    'ssg_new_crawler.middlewares.SsgNewCrawlerDownloaderMiddleware': 543,
#}

# Enable or disable extensions
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
#ITEM_PIPELINES = {
#    'ssg_new_crawler.pipelines.SsgNewCrawlerPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Retry request
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# SPLASH_SETTINGS
# SPLASH_URL = 'http://127.0.0.1:8050'
# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
# SPIDER_MIDDLEWARES = {'scrapy_splash.SplashDeduplicateArgsMiddleware': 100}

# SELENIUM_SETTINGS
SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'seleniumdriver', 'chromedriver')
SELENIUM_DRIVER_ARGUMENTS = ['--no-sandbox', '--headless']
