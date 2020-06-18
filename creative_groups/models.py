# A Creative Group is a collection of creatives

import logging
import os
import random
import tempfile
import urllib
from io import BytesIO
from zipfile import ZipFile, BadZipFile
import datetime

import requests
from PIL import Image, UnidentifiedImageError
from decouple import config
from django.conf import settings
from django.core.files.storage import default_storage, Storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.http import FileResponse
from io import StringIO, BytesIO

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)


class CreativeGroup(models.Model):
    name = models.CharField(max_length=1000, default='Creative Group')
    zip = models.FileField(upload_to='zips', blank=True)

    def __str__(self):
        return self.name

    def create_zip(self):
        return

