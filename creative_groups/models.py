# A Creative Group is a collection of creatives

import logging
import urllib
from zipfile import ZipFile
import datetime

from django.conf import settings
from django.db import models

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)


class CreativeGroup(models.Model):
    name = models.CharField(max_length=1000, default='Creative Group')

    def __str__(self):
        return self.name

    def create_zip(self):

        # Take all of the creatives associated with the creative group
        # Get the screenshot files
        # save as a zip

        zip_path = f"{settings.MEDIA_ROOT}/zips/{urllib.parse.quote_plus(self.name)}_{datetime.datetime.now().strftime('%m.%d.%H.%M')}.zip"

        logging.warning(zip_path)

        with ZipFile(zip_path, 'w',) as file:

            i = 1

            for creative in self.creative_set.all():

                if f'{creative.name}.png' in file.namelist():
                    file.write(creative.screenshot.path, arcname=f'{creative.name}_{i}.png')
                    i += 1

                else:
                    file.write(creative.screenshot.path, arcname=f'{creative.name}.png')

        return zip_path
