# A creative is an ad tag

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
    blocking = models.NullBooleanField(null=True, blank=True)
    blocking_vendor = models.CharField(max_length=30, blank=True)
    markup = models.TextField()
    markup_without_blocking = models.TextField(blank=True)
    screenshot = models.ImageField(upload_to='screenshots', height_field=None, width_field=None, max_length=100,
                                   blank=True)
    screenshot_url = models.URLField(blank=True)
    creative_group_id = models.ForeignKey(CreativeGroup,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def determine_adserver(self):

        search = re.search(r'ins|doubleclick|bs\.serving|servedby\.flashtalking|adsafeprotected\.com/rjss/dc',
                           self.markup)

        if search is None:
            self.adserver = 'unknown'
            self.save()
            logging.debug('The adserver could not be determined')
            return

        logging.debug(f'The adserver found is {search.group()}')

        if search.group() == 'ins':
            self.adserver = 'dcm ins'

        elif search.group() == 'doubleclick' or search.group() == 'adsafeprotected.com/rjss/dc':
            self.adserver = 'dcm legacy'

        elif search.group() == 'bs.serving':
            self.adserver = 'sizmek'

        elif search.group() == 'servedby.flashtalking':
            self.adserver = 'flashtalking'

        self.save()

        logging.debug(f'The adserver is {self.adserver}')

        return

    def has_blocking(self):

        # If blocking is not present
        # set .blocking to False
        # return False

        # If blocking is present
        # set .blocking to true
        # set .blocking_vendor to blocking vendor found
        # return true

        search = re.search(r'fw\.adsafeprotected|cdn\.doubleverify', self.markup)

        if search is not None:

            self.blocking = True

            if search.group() == 'fw.adsafeprotected':
                self.blocking_vendor = 'ias'
            elif search.group() == 'cdn.doubleverify':
                self.blocking_vendor = 'dv'

            self.save()

            return True

        else:

            self.blocking = False
            self.save()

            return False

    def use_correct_markup(self):

        # Uses the markup or markup_without_blocking depending on if has_blocking is true

        if self.blocking:
            logging.debug('Using markup_without_blocking')
            return self.markup_without_blocking
        else:
            logging.debug('Using markup_without_blocking')
            return self.markup

    def remove_blocking(self):
        if self.blocking_vendor == 'dv':
            if self.adserver == 'dcm ins':
                search = re.search(
                    r'((<script type="text\/adtag">\n)(.*<\/ins>)(.*))',
                    self.markup, re.DOTALL)

                tag_with_no_blocking = search.group(3)

                tag_with_no_blocking = tag_with_no_blocking.replace('</scr+ipt>', '</script>')

            elif self.adserver == 'dcm legacy':
                search = re.search(
                    r'(<script type=\"text/adtag\">\n)(.*<\/scr\+ipt>)(.*)',
                    self.markup, re.DOTALL)

                tag_with_no_blocking = search.group(2)

                tag_with_no_blocking = tag_with_no_blocking.replace('</scr+ipt>', '</script>')

        elif self.blocking_vendor == 'ias':
            if self.adserver == 'dcm ins':

                script_regex = re.compile(r'''
                    (https://)  # Use
                    (fw\.adsafeprotected\.com/rjss/)      # Remove
                    (www\.googletagservices\.com)         # Use
                    (/[0-9]*/[0-9]*)                      # Remove
                    (/dcm/dcmads\.js)                     # Use
                    ''', re.VERBOSE)

                tag_with_no_blocking = re.sub(script_regex, r'\1\3\5', self.markup)

            elif self.adserver == 'dcm legacy':
                script_regex = re.compile(r'''
                    (.*)                                  # Use
                    (fw\.adsafeprotected\.com/)           # Replace
                    (rjss/dc/[0-9]*/[0-9]*/)              # Remove
                    (.*)                                  # Use
                    ''', re.VERBOSE)

                tag_with_no_blocking = re.sub(script_regex, r'\1ad.doubleclick.net/\4', self.markup)

            elif self.adserver == 'sizmek':
                script_regex = re.compile(r'''
                    (.*https://)                          # Use
                    (fw\.adsafeprotected\.com/rjss/)      # Remove
                    (.*/)                                 # Use
                    ([0-9]*/[0-9]*/)                      # Remove
                    (.*</script>)                         # Use
                    
                    # Note: Only unblocks script portion
                    
                    ''', re.VERBOSE)

                tag_with_no_blocking = re.sub(script_regex, r'\1\3\5', self.markup)

        self.markup_without_blocking = tag_with_no_blocking
        self.save()

    def take_screenshot(self):

        # Uses the HCTI API to take a screenshot of the ad tag code provided

        hcti_api_endpoint = "https://hcti.io/v1/image?ms_delay=3000"
        hcti_api_user_id = config('hcti_api_user_id')
        hcti_api_key = config('hcti_api_key')

        data = {'html': self.use_correct_markup()}

        image = requests.post(url=hcti_api_endpoint, data=data, auth=(hcti_api_user_id, hcti_api_key))

        self.screenshot_url = image.json()['url']
        self.save()

    def save_screenshot(self):

        # Saves the screenshot taken by the HCTI API URL locally

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
