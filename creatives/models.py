import io
import re
import logging
from urllib.parse import urlparse

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
import requests
from creative_groups.models import CreativeGroup

import requests
from decouple import config
from io import BytesIO
from PIL import Image


class Creative(models.Model):
    name = models.CharField(max_length=100)
    adserver = models.CharField(max_length=30, blank=True)
    blocking = models.BooleanField()
    blocking_vendor = models.CharField(max_length=30, blank=True)
    markup = models.TextField()
    screenshot = models.ImageField(upload_to='screenshots', height_field=None, width_field=None, max_length=100, blank=True)
    screenshot_url = models.URLField(blank=True)
    creative_group_id = models.ForeignKey(CreativeGroup,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def check_for_blocking(self):
        search = re.search(r'fw\.adsafeprotected|cdn\.doubleverify', self.markup)
        if search is None:
            return False
        else:
            return True

    def remove_blocking(self):
        print(self.name)

    def take_screenshot(self):
        hcti_api_endpoint = "https://hcti.io/v1/image"
        hcti_api_user_id = config('hcti_api_user_id')
        hcti_api_key = config('hcti_api_key')

        data = {'html': self.markup}

        image = requests.post(url=hcti_api_endpoint, data=data, auth=(hcti_api_user_id, hcti_api_key))

        self.screenshot_url = image.json()['url']
        self.save()

    def save_screenshot(self):

        logging.debug(self.screenshot_url)  # The screenshot url from HCTI

        r = requests.get(self.screenshot_url, auth=(config('hcti_api_user_id'), config('hcti_api_key')))

        i = Image.open(BytesIO(r.content))

        name = f"{urlparse(self.screenshot_url).path.split('/')[-1]}.png"

        logging.debug(name)  # The name from the url from HCTI

        buffer = BytesIO()

        i.save(buffer, format='PNG')

        im = InMemoryUploadedFile(
            buffer,
            None,
            name,
            'image/png',
            buffer.tell(),
            None)

        self.screenshot = im
        self.save()
