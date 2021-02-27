import datetime
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from threading import Thread, Lock
from typing import List

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi import Form
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from simple_parsing import ArgumentParser

from .devices import HostDevice, ChromecastDevice, Device
from .utils import get_ip_addr, hashname, get_url, text_to_wav

templates = Jinja2Templates(directory=f"{Path(__file__).parent}/templates")

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scheduler.start()

load_dotenv()

lock = Lock()


@dataclass
class Settings:
    cache_path: str = f'{os.environ["HOME"]}/.cache/chromecast-notify/wav'
    play_on_host: bool = True
    last_played_text: str = ''
    cast_name: List[str] = field(default_factory=lambda: ['All Speakers'])
    ip_add: str = get_ip_addr()
    do_not_disturb: bool = False
    port: int = 8084
    voice_name: str = 'en-GB-Wavenet-C'


class Text(BaseModel):
    text: str


class TTSNotifier:

    def __init__(self, settings):
        self.devices: List[Device] = []
        self.settings = settings

    def register(self, device: Device):
        self.devices.append(device)

    def play(self, text):
        self.settings.last_played_text = text
        filename = f'{hashname(text)}.wav'
        path = f'{self.settings.cache_path}/{filename}'
        url = get_url(text, self.settings.ip_add, self.settings.port)
        if not os.path.exists(path):
            text_to_wav(voice_name=self.settings.voice_name, text=text, filename=path)
        with lock:
            logger.info(f'Casting {url}')
            for device in self.devices:
                device.cast(url=url, path=os.path.join(self.settings.cache_path, filename), title=text)
        return filename


def create_app(notifier, settings: Settings) -> FastAPI:
    app = FastAPI()

    @app.get('/wav/{filename}')
    def get_wav(filename):
        return FileResponse(f'{settings.cache_path}/{filename}')

    @app.get("/info")
    async def info():
        return settings

    @app.get("/")
    async def serve_home(request: Request):
        return templates.TemplateResponse("settings.html", {"request": request})

    @app.get('/unmute')
    def unmute():
        settings.do_not_disturb = False
        return 'Unmuted'

    @app.get('/mute')
    def mute():
        settings.do_not_disturb = True
        try:
            scheduler.remove_job(job_id='snooze')
        except:
            pass
        return 'muted'

    def notify(text):
        if settings.do_not_disturb:
            return 'Do not disturb is on. Unmute to allow notifications.'
        Thread(target=notifier.play, args=(text,)).start()
        return {'text': text, 'wav': get_url(text=text, ip_add=settings.ip_add, port=settings.port)}

    @app.get("/notify")
    def get_notify(text):
        return notify(text)

    @app.post("/notify")
    def post_notify(text: str = Form(None)):
        return notify(text)

    @app.get("/ismuted")
    def is_muted():
        return {'isMuted': settings.do_not_disturb}

    @app.get('/mute/{minutes}')
    def snooze(minutes):
        settings.do_not_disturb = True
        trigger = DateTrigger(datetime.datetime.now() + datetime.timedelta(minutes=int(minutes)))
        try:
            scheduler.reschedule_job(func=unmute,
                                     job_id='snooze',
                                     trigger=trigger)
        except:
            scheduler.add_job(func=unmute,
                              id='snooze',
                              trigger=trigger)
        return f'snoozed till {trigger}'

    return app


def create_parser():
    parser = ArgumentParser()
    parser.add_arguments(Settings, dest='settings')
    return parser


def main(args):
    settings = args.settings
    tts_notifier = TTSNotifier(settings)
    tts_notifier.register(ChromecastDevice(settings.cast_name))
    if settings.play_on_host:
        tts_notifier.register(HostDevice())
    app = create_app(tts_notifier, settings)
    Thread(target=tts_notifier.play, args=('Chromecast notifier started',)).start()
    uvicorn.run(app, port=settings.port, host='0.0.0.0')


if __name__ == "__main__":
    args = create_parser().parse_args()
    main(args)
