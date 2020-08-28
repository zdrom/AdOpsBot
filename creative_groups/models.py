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
from django.core.files.temp import NamedTemporaryFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.http import FileResponse
from io import StringIO, BytesIO

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from slack import WebClient

log = logging.getLogger("django")


class CreativeGroup(models.Model):
    name = models.CharField(max_length=1000, default='Creative Group')
    zip = models.FileField(upload_to='zips', blank=True)

    def __str__(self):
        return self.name

    def click_and_pic(self, channel, progress_meter):

        slack_client = WebClient(config('SLACK_BOT_TOKEN'))

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        browser = webdriver.Chrome(options=chrome_options)

        creatives = self.creative_set.all()

        p = 0  # progress meter counter

        for creative in creatives:

            p += 1

            html_doc = creative.use_correct_markup()

            log.info(f'Mark Up with macros replaced: {creative.markup_with_macros_replaced}')

            browser.get("data:text/html;charset=utf-8,{html_doc}".format(html_doc=html_doc))

            # Wait for the creative to render
            browser.implicitly_wait(1.5)

            '''
            Save the screenshot
            Crop the image 
            there is an 8x8 border on the top and left so crop include that in the crop
            move from temp file to default storage
            '''
            temp = NamedTemporaryFile(prefix='screenshot', suffix='.png')
            browser.save_screenshot(temp.name)
            im = Image.open(temp)
            cropped_dimensions = (8, 8, int(creative.width) + 8, int(creative.height) + 8)
            log.warning(f'The cropped dimensions are {cropped_dimensions}')
            cropped = im.crop(cropped_dimensions)

            temp_out = NamedTemporaryFile(prefix='screenshot_out', suffix='.png')
            cropped.save(temp_out.name)

            creative.screenshot = default_storage.save('screenshots/screenshot.png', temp_out)
            creative.save()

            try:
                if creative.adserver == 'dcm ins':
                    el = browser.find_element_by_tag_name('ins')
                elif creative.adserver == 'dcm legacy':
                    el = browser.find_element_by_tag_name('a')
                elif creative.adserver == 'sizmek':
                    imgs = browser.find_elements_by_tag_name('img')
                    # in case there are any 1x1s
                    # find the image that has dimensions greater than 1x1
                    for img in imgs:
                        print(int(img.get_attribute('width')) > 1)
                        if int(img.get_attribute('width')) > 1:
                            el = img
                            break
                elif creative.adserver == 'flashtalking':
                    # served in an iframe
                    browser.switch_to.frame(0)
                    # in case there are any 1x1s
                    # find the image that has dimensions greater than 1x1
                    imgs = browser.find_elements_by_tag_name('img')
                    for img in imgs:
                        if int(img.get_attribute('width')) > 1:
                            el = img
                            break

                el.click()

                # switch to the newly opened tab

                try:
                    browser.switch_to.window(browser.window_handles[1])
                except:
                    log.exception(f'{creative.name} has an invalid click through')
                    creative.click_through = 'Unable to determine'
                    creative.save()
                    slack_client.chat_update(channel=channel, ts=progress_meter['ts'], text=f'{ p } out of { creatives.count() } complete')
                    continue

                '''
                Primarily for sizmek but this makes sure that an actual url is captured
                instead of about:blank
                , for instance
                '''

                log.info(f'Waiting for this to contain http: {browser.current_url}')

                WebDriverWait(browser, 10).until(
                    EC.url_contains('http'))

                creative.click_through = browser.current_url

                log.info(f'{creative.name} click through: {creative.click_through}')
                creative.save()

                browser.close()
                browser.switch_to.window(browser.window_handles[-1])

                slack_client.chat_update(channel=channel, ts=progress_meter['ts'],
                                         text=f'{p} out of {creatives.count()} complete')

            except (NoSuchElementException, WebDriverException) as e:
                log.exception(f'{creative.name} has an invalid click through')
                creative.click_through = 'Unable to determine'
                creative.save()
                slack_client.chat_update(channel=channel, ts=progress_meter['ts'],
                                         text=f'{p} out of {creatives.count()} complete')

        browser.quit()
