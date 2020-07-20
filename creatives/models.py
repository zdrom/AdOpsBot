# A creative is an ad tag

import io
from pprint import pprint
import re
import logging
from urllib.parse import urlparse

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
import requests

from AdOpsBot import settings
from creative_groups.models import CreativeGroup

import requests
from decouple import config
from io import BytesIO
from PIL import Image, UnidentifiedImageError

log = logging.getLogger("django")


class Creative(models.Model):
    name = models.CharField(max_length=100)
    requested_by = models.CharField(max_length=100, blank=True)
    adserver = models.CharField(max_length=30, blank=True)
    blocking = models.NullBooleanField(null=True, blank=True)
    blocking_vendor = models.CharField(max_length=30, blank=True)
    markup = models.TextField()
    markup_without_blocking = models.TextField(blank=True)
    screenshot = models.ImageField(upload_to='screenshots', height_field=None, width_field=None, max_length=100,
                                   blank=True)
    screenshot_url = models.URLField(blank=True)
    creative_group_id = models.ForeignKey(CreativeGroup, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def clean_up(self):
        # Remove Potential formatting that slack adds
        self.markup = re.sub(pattern=r'^```|```$', repl='', string=self.markup)
        self.markup = re.sub(pattern='/^`|`$/', repl='', string=self.markup)
        # Slack replaces the straight quotes with angled quotes -- swap straight quotes back in
        self.markup = self.markup.replace('’', "'")
        self.markup = self.markup.replace('‘', "'")
        self.markup = self.markup.replace('“', '"')
        self.markup = self.markup.replace('”', '"')
        self.markup = self.markup.replace('_x000D_', '')
        self.save()

    def determine_adserver(self):

        search = re.search(r'ins|doubleclick|bs\.serving|servedby\.flashtalking|adsafeprotected\.com/rjss/dc',
                           self.markup)

        if search is None:
            self.adserver = 'unknown'
            self.save()
            log.warning('The adserver could not be determined')
            return

        if search.group() == 'ins':
            self.adserver = 'dcm ins'

        elif search.group() == 'doubleclick' or search.group() == 'adsafeprotected.com/rjss/dc':
            self.adserver = 'dcm legacy'

        elif search.group() == 'bs.serving':
            self.adserver = 'sizmek'

        elif search.group() == 'servedby.flashtalking':
            self.adserver = 'flashtalking'

        self.save()

        log.info(f'The adserver is {self.adserver}')

        return self.adserver

    def has_blocking(self):

        # If blocking is not present
        # set .blocking to False
        # return False

        # If blocking is present
        # set .blocking to true
        # set .blocking_vendor to blocking vendor found
        # return true

        # This will also test for monitoring as
        # IAS monitoring scripts have caused image errors

        search = re.search(r'adsafeprotected|cdn\.doubleverify', self.markup)

        if search is not None:

            self.blocking = True

            if search.group() == 'adsafeprotected':
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
            log.info('Using markup_without_blocking')
            return self.markup_without_blocking
        else:
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

            elif self.adserver == 'sizmek':
                search = re.search(
                    r'<script type="text/adtag">(.*)<script language="javascript".*',
                    self.markup, re.DOTALL)
                tag_with_no_blocking = search.group(1)

        elif self.blocking_vendor == 'ias':

            # Check for monitoring first and remove that script
            # Monitoring breaks the screenshot API
            # It will be the same regardless of tag type
            # A tag will never have blocking and monitoring

            monitoring = re.search(r'pixel\.adsafeprotected', self.markup)

            if monitoring is not None:
                script_regex = re.compile(
                    r'<SCRIPT TYPE="application/javascript" '
                    r'SRC="https://pixel\.adsafeprotected\.com.*skeleton.js"></SCRIPT>'
                    r'(?:.*skeleton.gif" BORDER=0 WIDTH=1 HEIGHT=1 ALT=""></NOSCRIPT>)*'
                    , re.DOTALL)

                tag_with_no_blocking = re.sub(script_regex, r'', self.markup)

            elif self.adserver == 'dcm ins':

                if monitoring is not None:
                    script_regex = re.compile(r'''
                        (.*</ins>)  # Use
                        (.*)      # Remove
                        ''', re.VERBOSE)

                    tag_with_no_blocking = re.sub(script_regex, r'\1', self.markup)

                else:
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

            elif self.adserver == 'flashtalking':
                pass

        self.markup_without_blocking = tag_with_no_blocking
        self.save()

        return tag_with_no_blocking

    def take_screenshot(self):

        # Uses the HCTI API to take a screenshot of the ad tag code provided

        hcti_api_endpoint = "https://hcti.io/v1/image"
        hcti_api_user_id = config('hcti_api_user_id')
        hcti_api_key = config('hcti_api_key')

        data = {
            'html': self.use_correct_markup(),
            'device_scale': 1,
            'ms_delay': 3000
        }

        image = requests.post(url=hcti_api_endpoint, data=data, auth=(hcti_api_user_id, hcti_api_key))

        self.screenshot_url = image.json()['url']
        self.save()

        log.info(f'Successfully took screenshot for {self.name}')
        log.info(self.screenshot_url)

    def save_image(self):

        log.info(f'Saving Creative: {self.name}')

        r = requests.get(self.screenshot_url, auth=(config('hcti_api_user_id'), config('hcti_api_key')))

        try:

            i = Image.open(BytesIO(r.content))

        except UnidentifiedImageError:

            log.error(msg=f'image error for {self.name}')

            return self.name

        buffer = BytesIO()
        
        # '''
        # API Automatically saves at 2X images for retina purposes
        # Resize to proper dimensions
        # '''
        #
        # width, height = i.size
        #
        # log.info(f'width: {width} and height: {height}')
        #
        # new_width = int(width / 2)
        # new_height = int(height / 2)
        #
        # new_dimensions = (new_width, new_height)
        #
        # i = i.resize(new_dimensions)

        i.save(buffer, format='PNG')

        im = InMemoryUploadedFile(
            buffer,
            None,
            f'{self.name}.png',
            'image/png',
            buffer.tell(),
            None)

        self.screenshot = im
        self.save()

        log.info(f'Successfully saved image for {self.name}')

        return None
