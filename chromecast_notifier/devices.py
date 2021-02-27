import logging
import os
import sys
import time

import pychromecast

logger = logging.getLogger(__name__)


class Device:
    def cast(self, url, **kwargs):
        raise NotImplementedError


class HostDevice(Device):

    def __init__(self):
        self.is_playing = False

    def cast(self, *, path, **kwargs):
        while self.is_playing is True:
            time.sleep(1)
        self.is_playing = True
        os.system(f'play {path}')
        self.is_playing = False


class ChromecastDevice(Device):

    def __init__(self, friendly_names):
        self.cast_device = self.get_chromecast(friendly_names)

    @staticmethod
    def get_chromecast(friendly_names=('All Audio Speakers')):
        logger.info(f"Getting chromecast with name {friendly_names}")
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names)

        if not chromecasts:
            logger.error(f'No chromecast with name "{friendly_names}" discovered')
            sys.exit(1)
        return chromecasts[0]

    def cast(self, *, url, title='Announcement', **kwargs):

        cast_device = self.cast_device

        cast_device.wait()
        media_controller = cast_device.media_controller
        while media_controller.is_playing:
            time.sleep(0.01)

        media_controller.play_media(url, 'audio/mp3', title=title)
        while not media_controller.is_playing:
            time.sleep(0.01)
        return
