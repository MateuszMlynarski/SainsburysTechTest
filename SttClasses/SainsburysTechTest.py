#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import urllib.parse, urllib.request, re, asyncio, bs4
from bs4 import BeautifulSoup


class SainsburysTechTest:
    def __init__(self, loop):
        """
        Contstructor sets default params
            :param loop - asyncio event loop
            :returns {}
        """
        # asyncio event loop
        self.loop = loop

        # List of links which are currently parsed
        self.busy = set()

        # return result
        self.__result = {'results': [], 'total': 0}

    def get_links(self, url):
        """
        Method prepares links from products list
            :param url -- Link to Sainsbury's test web page
            :returns [] -- list of products links
        """
        product_links = []
        content = self.get_content_from_url(url)
        soup = BeautifulSoup(content['content'], "lxml")

        # Getting product list container
        for products_list in soup.find_all('ul', {'class': 'productLister listView'}):

            # Getting every link from product list container
            for link in products_list.find_all('a'):
                product_links.append(link.get('href'))

        return product_links

    def get_result(self):
        """Returns prepared result"""
        return self.__result

    def get_content_from_url(self, url):
        """
        Read HTML data from URL. If nothing found returns empty string
            :param url -- link to web page
            :returns {'content_size': '0kb', 'content': ''}
        """
        try:
            resource = urllib.request.urlopen(url)
            serviceCharset = resource.headers.get_content_charset()
            if serviceCharset is None:
                serviceCharset = 'UTF-8'

            # Getting content
            content = resource.read().decode(serviceCharset)

            # Getting Content-Length in kb
            content_length = round(float(resource.headers.get('Content-Length')) / 1024, 2)

            return {'content_size': str(content_length) + 'kb', 'content': content}
        except:
            return {'content_size': '0kb', 'content': ''}

    @asyncio.coroutine
    def run(self, link):
        """
        Runs asyncio task for every product link
            :param link -- url to product description web page
        """
        links = self.get_links(link)

        # Runs asyncio task for every product link
        for content_page in links:
            asyncio.Task(self.process(content_page)).result

            # wait a while
            yield from asyncio.sleep(.01)

        self.loop.stop()

    @asyncio.coroutine
    def process(self, service):
        """
        Runs process for parsing description page
            :param service -- url for product description web page
        """
        # Sets service url to busy list
        self.busy.add(service)

        # default result list
        result = {'title': '', 'size': '', 'unit_price': '', 'description': ''}
        content = self.get_content_from_url(service)
        result['size'] = content['content_size']

        soup = BeautifulSoup(content['content'], "lxml")

        # Getting data from product summary
        for product_summary in soup.find_all('div', {'class': 'productSummary'}):

            # Getting product title
            for product_title_container in product_summary.find_all('div',
                                                                    {'class': 'productTitleDescriptionContainer'}):
                for product_title in product_title_container.find_all('h1'):
                    result['title'] = product_title.string

            # Getting product price
            for price in product_summary.find_all('p', {'class': 'pricePerUnit'}):
                unit_price = price.contents[0].replace('\n£', '')
                result['unit_price'] = float(unit_price)

        # Getting product content container
        for product_content in soup.find_all('productcontent'):
            description = product_content.htmlcontent.find_all('div', {'class': 'productText'})[0]

            # Getting all elements of description
            for content_element in description.contents:
                if isinstance(content_element, bs4.element.Tag) and content_element.string is not None:
                    content = content_element.string.replace('\n', '')
                    result['description'] = result['description'] + ' ' + content

        # append method result to global results list
        self.__result['results'].append(result)

        # sets sum of unit prices
        self.__result['total'] = round(self.__result['total'] + result['unit_price'], 2)

        # remove service url from busy list
        self.busy.remove(service)
