"""
WSGI config for Amadou_Issaka_Project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import threading
import schedule
from django.core.wsgi import get_wsgi_application

from IphoneScrapper.scapper.avitoScrapp import AvitoScrapp
from IphoneScrapper.scapper.marocAnnonceScrapp import MarocAnnonceScrapp

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Amadou_Issaka_Project.settings')

application = get_wsgi_application()


def backgroundAvitoScrapp():
    schedule.every(5).minutes.do(AvitoScrapp)
    while True:
        schedule.run_pending()


def backgroundMarocAnnonceScrapp():
    schedule.every(5).minutes.do(MarocAnnonceScrapp)
    while True:
        schedule.run_pending()


avito = threading.Thread(target=backgroundAvitoScrapp)
marocAnnonce = threading.Thread(target=backgroundMarocAnnonceScrapp)
avito.start()
marocAnnonce.start()
