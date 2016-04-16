#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import unittest, json, asyncio, signal
from SttClasses.SainsburysTechTest import SainsburysTechTest


class TestSainsburysTechTest(unittest.TestCase):
    # Incorrect URL for test
    __incorrect_url = 'http://unknown-page.un.known.domain/something-null.html';

    # Correct URL
    __correct_url = 'http://hiring-tests.s3-website-eu-west-1.amazonaws.com/2015_Developer_Scrape/5_products.html'

    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def testSainsburysTechTestExist(self):
        """Checks if SainsburysTechTest exists"""
        stt = SainsburysTechTest(self.loop)
        del stt

    def testGetContentFromUrl(self):
        """Checks if SainsburysTechTest can take content from correct URL -content size must be greader than 30 kb"""
        stt = SainsburysTechTest(self.loop)
        result = stt.get_content_from_url(self.__correct_url)
        assert float(result['content_size'].replace('kb', '')) > 30

    def testGetNullContentFromUrl(self):
        """Checks if SainsburysTechTest returns empty string as a content from incorrect URL - content size must be equal to zero"""
        stt = SainsburysTechTest(self.loop)
        result = stt.get_content_from_url(self.__incorrect_url)
        assert float(result['content_size'].replace('kb', '')) == 0

    def testGetDefaultResult(self):
        """Checks if SainsburysTechTest returns default result"""
        stt = SainsburysTechTest(self.loop)
        asyncio.Task(stt.run(self.__incorrect_url))

        try:
            self.loop.add_signal_handler(signal.SIGINT, self.loop.stop)
        except RuntimeError:
            pass

        self.loop.run_forever()

        result = stt.get_result()
        assert (result['results'] == [] and result['total'] == 0.0)

    def testGetCorrectResult(self):
        """Checks if SainsburysTechTest returns correct result"""
        stt = SainsburysTechTest(self.loop)
        asyncio.Task(stt.run(self.__correct_url))

        try:
            self.loop.add_signal_handler(signal.SIGINT, self.loop.stop)
        except RuntimeError:
            pass

        self.loop.run_forever()
        result = stt.get_result()
        assert (len(result['results']) == 7 and result['total'] == 15.1)
        for result_data in result['results']:
            assert result_data['unit_price'] > 0
            assert float(result_data['size'].replace('kb', '')) > 0
            assert len(result_data['title']) > 0
            assert len(result_data['description']) > 0


if __name__ == "__main__":
    unittest.main()
