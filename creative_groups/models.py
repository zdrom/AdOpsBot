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

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)


class CreativeGroup(models.Model):
    name = models.CharField(max_length=1000, default='Creative Group')
    zip = models.FileField(upload_to='zips', blank=True)

    def __str__(self):
        return self.name

    def validate_click_through(self):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        browser = webdriver.Chrome(options=chrome_options)

        creatives = self.creative_set.all()

        for creative in creatives:
            try:
                browser.get("data:text/html;charset=utf-8,{html_doc}".format(html_doc=html_doc))

                if self.adserver == 'dcm ins' or self.adserver == 'dcm legacy':
                    el = browser.find_element_by_tag_name('a')
                if self.adserver == 'sizmek':
                    imgs = browser.find_elements_by_tag_name('img')
                    # in case there are any 1x1s
                    # find the image that has dimensions greater than 1x1
                    for img in imgs:
                        print(int(img.get_attribute('width')) > 1)
                        if int(img.get_attribute('width')) > 1:
                            el = img
                            break
                if self.adserver == 'flashtalking':
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
                browser.switch_to.window(browser.window_handles[1])

                '''
                Primarily for sizmek but this makes sure that an actual url is captured
                instead of about:blank
                , for instance
                '''

                WebDriverWait(browser, 10).until(
                    EC.url_contains('http'))

                self.click_through = browser.current_url

            except NoSuchElementException:
                creative.click_through = 'Invalid'

            creative.save()
            browser.close()
            browser.switch_to.window(browser.window_handles[-1])

        browser.quit()