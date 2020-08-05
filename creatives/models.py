# A creative is an ad tag


import re
import logging

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from creative_groups.models import CreativeGroup

import requests
from decouple import config
from io import BytesIO
from PIL import Image, UnidentifiedImageError

log = logging.getLogger("django")


class Creative(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    requested_by = models.CharField(max_length=100, blank=True)
    adserver = models.CharField(max_length=30, blank=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    placement_id = models.CharField(max_length=50, blank=True)
    blocking = models.NullBooleanField(null=True, blank=True)
    blocking_vendor = models.CharField(max_length=30, blank=True)
    markup = models.TextField()
    markup_with_macros = models.TextField(null=True, blank=True)
    markup_with_macros_replaced = models.TextField(null=True, blank=True)
    markup_without_blocking = models.TextField(null=True, blank=True)
    screenshot = models.ImageField(upload_to='screenshots', height_field=None, width_field=None, max_length=100,
                                   blank=True)
    screenshot_url = models.URLField(blank=True)
    creative_group_id = models.ForeignKey(CreativeGroup, on_delete=models.CASCADE, blank=True, null=True)
    click_through = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

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

        # make sure macros are included if they have been added

        if self.markup_with_macros:
            markup = self.markup_with_macros
            log.info('Removing blocking from mark up with macros')
            print('mark up with macros')
        else:
            markup = self.markup
            log.info('Removing blocking from markup')
            print('mark up without macros')
            print(markup)

        if self.blocking_vendor == 'dv':
            if self.adserver == 'dcm ins':
                tag = re.compile(r'(<script type="text/adtag">\n)(.*<\/ins>)(.*)', re.DOTALL)

                tag_with_no_blocking = re.sub(tag, r'\2', markup)

                tag_with_no_blocking = tag_with_no_blocking.replace('</scr+ipt>', '</script>')

            elif self.adserver == 'dcm legacy':
                search = re.search(
                    r'(<script type=\"text/adtag\">\n)(.*</scr\+ipt>)(.*)',
                    markup, re.DOTALL)

                tag_with_no_blocking = search.group(2)

                tag_with_no_blocking = tag_with_no_blocking.replace('</scr+ipt>', '</script>')

            elif self.adserver == 'sizmek':
                search = re.search(
                    r'<script type="text/adtag">(.*)<script language="javascript".*',
                    markup, re.DOTALL)
                tag_with_no_blocking = search.group(1)

        elif self.blocking_vendor == 'ias':

            # Check for monitoring first and remove that script
            # Monitoring breaks the screenshot API
            # It will be the same regardless of tag type
            # A tag will never have blocking and monitoring

            monitoring = re.search(r'pixel\.adsafeprotected', markup)

            if monitoring is not None:
                script_regex = re.compile(
                    r'<SCRIPT TYPE="application/javascript" '
                    r'SRC="https://pixel\.adsafeprotected\.com.*skeleton.js"></SCRIPT>'
                    r'(?:.*skeleton.gif" BORDER=0 WIDTH=1 HEIGHT=1 ALT=""></NOSCRIPT>)*'
                    , re.DOTALL)

                tag_with_no_blocking = re.sub(script_regex, r'', markup)

            elif self.adserver == 'dcm ins':
                print('now im here')
                script_regex = re.compile(r'''
                    (https://)  # Use
                    (fw\.adsafeprotected\.com/rjss/)      # Remove
                    (www\.googletagservices\.com)         # Use
                    (/[0-9]*/[0-9]*)                      # Remove
                    ''', re.VERBOSE)

                tag_with_no_blocking = re.sub(script_regex, r'\1\3', markup)

            elif self.adserver == 'dcm legacy':
                script_regex = re.compile(r'''
                    (.*)                                  # Use
                    (fw\.adsafeprotected\.com/)           # Replace
                    (rjss/dc/[0-9]*/[0-9]*/)              # Remove
                    (.*)                                  # Use
                    ''', re.VERBOSE)

                tag_with_no_blocking = re.sub(script_regex, r'\1ad.doubleclick.net/\4', markup)

            elif self.adserver == 'sizmek':
                script_regex = re.compile(r'''
                    (.*https://)                          # Use
                    (fw\.adsafeprotected\.com/rjss/)      # Remove
                    (.*/)                                 # Use
                    ([0-9]*/[0-9]*/)                      # Remove
                    
                    # Note: Only unblocks script portion
                    
                    ''', re.VERBOSE)

                tag_with_no_blocking = re.sub(script_regex, r'\1\3', markup)

            elif self.adserver == 'flashtalking':
                script_regex = re.compile(r'''
                    (.*https://)                          # Use
                    (fw\.adsafeprotected\.com/rjss/)      # Remove
                    (.*/)                                 # Use
                    ([0-9]*/[0-9]*/)                      # Remove

                    # Note: Only unblocks script portion

                    ''', re.VERBOSE)

                tag_with_no_blocking = re.sub(script_regex, r'\1\3', markup)

        self.markup_without_blocking = tag_with_no_blocking
        self.save()

        return tag_with_no_blocking

    def get_dimensions(self):
        if self.adserver == 'unknown':
            log.info('The adserver is unknown so cannot find dimensions')
            return

        elif self.adserver == 'dcm ins':
            pattern = r'width:([0-9]*).*height:([0-9]*)'
            match = re.search(pattern, self.use_correct_markup())
            self.width = match[1]
            self.height = match[2]

        elif self.adserver == 'dcm legacy':
            pattern = r'sz=([0-9]*)x([0-9]*)'
            match = re.search(pattern, self.use_correct_markup())
            self.width = match[1]
            self.height = match[2]

        elif self.adserver == 'sizmek':
            pattern = r'w=([0-9]*)&h=([0-9]*)'
            match = re.search(pattern, self.use_correct_markup())
            self.width = match[1]
            self.height = match[2]

        elif self.adserver == 'flashtalking':
            pattern = r'ft_width=([0-9]*)&ft_height=([0-9]*)'
            match = re.search(pattern, self.use_correct_markup())
            self.width = match[1]
            self.height = match[2]

        self.save()

    def get_placement_id(self):
        if self.adserver == 'unknown':
            log.info('The adserver is unknown so cannot find dimensions')
            return

        elif self.adserver == 'dcm ins':
            pattern = r"data-dcm-placement='\S*\.([0-9]*)'"
            match = re.search(pattern, self.use_correct_markup())
            self.placement_id = match[1]

        elif self.adserver == 'dcm legacy':
            pattern = r'\S*\.\S*/\S*\.([0-9]*)'
            match = re.search(pattern, self.use_correct_markup())
            self.placement_id = match[1]

        elif self.adserver == 'sizmek':
            pattern = r'&pli=([0-9]*)'
            match = re.search(pattern, self.use_correct_markup())
            self.placement_id = match[1]

        elif self.adserver == 'flashtalking':
            pattern = r'ftClick_([0-9]*)'
            match = re.search(pattern, self.use_correct_markup())
            self.placement_id = match[1]

        self.save()

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

    def validate_click_through(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        browser = webdriver.Chrome(options=chrome_options)

        html_doc = self.use_correct_markup()

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

            self.click_through = 'Invalid'

        finally:
            browser.quit()
            self.save()
            return f'Click through: {self.click_through}'

    def add_macros(self):

        markup = self.markup

        if self.adserver == 'unknown':
            log.info('The adserver is unknown so cannot find dimensions')
            return

        elif self.adserver == 'dcm ins':

            '''
            Does the tag already have the resettable device ID param
            If so, populate it with the IDFA macro
            If not, add the param and the macro
            '''

            rdid = r"(data-dcm-resettable-device-id=')(')"

            match = re.search(rdid, markup)

            if match:
                markup = re.sub(rdid, r"\1[IDFA]\2", markup)
            else:
                https = r"(data-dcm-https-only)"
                markup = re.sub(https, r"\1\n    data-dcm-resettable-device-id='[IDFA]'", markup)

            '''
            Does the tag already have the click tracker field
            If so, populate it with the encoded click macro
            If not, add the param and the macro
            '''

            click_tracker = r"(data-dcm-click-tracker=')(')"

            match = re.search(click_tracker, markup)

            if match:
                markup = re.sub(rdid, r"\1[ENCODEDCLICKURL]\2", markup)
            else:
                https = r"(data-dcm-https-only)"
                markup = re.sub(https, r"\1\n    data-dcm-click-tracker='[ENCODEDCLICKURL]'", markup)

        elif self.adserver == 'dcm legacy':
            timestamp = r"(ord=\[timestamp];)"
            markup = re.sub(timestamp, r"\1click=[ENCODEDCLICKURL];", markup)

        elif self.adserver == 'sizmek':

            '''
            Find the pli param
            add the encoded click before it
            '''

            pli = r"(&pli=)"
            markup = re.sub(pli, r"&ncu=[ENCODEDCLICKURL]\1", markup)

            '''
            Add in the click URL for the noscript portion
            '''

            noscript = r"(href=\")(https://bs)"

            match = re.search(noscript, markup)

            if match:
                markup = re.sub(noscript, r"\1[CLICKURL]\2", markup)

        elif self.adserver == 'flashtalking':
            noscript = r"(href=\")(https://servedby)"

            match = re.search(noscript, markup)

            if match:
                markup = re.sub(noscript, r"\1[CLICKURL]\2", markup)

            ft_click = r"(var ftClick = \")(\")"
            markup = re.sub(ft_click, r"\1[ENCODEDCLICKURL]\2", markup)

        self.markup_with_macros = markup
        self.save()

    def replace_macros(self):

        # This will either use the markup or the mark up without blocking and replace
        # The encoded click tracker with an actual click tracker
        # No other macros are replaced right now
        # As this is for click validation

        markup = self.use_correct_markup()

        click_tracker = 'https%3A%2F%2Frtb.adentifi.com%2FClicks%3FcrId%3D163837%3BsId%3D159128%3BlId%3D29432%3BcId%3D2603%3BadExchange%3DNexage%3Baction%3Dclick%3BadId%3D607d29cf-d58a-11ea-87d7-12a1a22bbcf8%3BadThdId%3D%3BengineId%3Di-025e141792472342b%3BdIp%3DMTIuMTc1LjE3MS4xNA%3Bsite%3DNjA3ZDI5YzktZDU4YS0xMWVhLTg3ZDctMTJhMWEyMmJiY2Y4%3BadThdIdCode%3DINVALID%3BdealId%3D0%3BgeoId%3D55202%3BinventoryId%3D607d29cc-d58a-11ea-87d7-12a1a22bbcf8%3BrtdmIndicator%3D0%3Bredir%3D'

        self.markup_with_macros_replaced = markup.replace('[ENCODEDCLICKURL]', click_tracker)
        self.save()
