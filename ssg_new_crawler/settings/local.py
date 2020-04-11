from .base import *


DOWNLOAD_DELAY = 1

# selenium config
SELENIUM_DRIVER_EXECUTABLE_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'seleniumdriver', 'chromedriver.exe')
