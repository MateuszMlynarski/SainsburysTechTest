#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import argparse, json, asyncio, sys, signal, platform
from argparse import RawTextHelpFormatter
from SttClasses.SainsburysTechTest import SainsburysTechTest


if sys.version_info < (3, 4):
    raise SystemExit("Sainsbury's tech test requires at least Python 3.4, sorry.")


def main():
    warranty_warning = ''

    # Check if it runs under Linux. Otherwaise there is no warranty to run properly
    if platform.system() != 'Linux':
        warranty_warning = "\nWarning! Sainsbury's tech test was created under Linux system. There is no warranty it will run properly under " + platform.system() + ".\n"
        print(warranty_warning)

    # Information to show after -h parameter will be used
    parser = argparse.ArgumentParser(
        description="Sainsbury's tech test - console application that scrapes the Sainsbury’s grocery site - Ripe Fruits page and returns a JSON array of all the products on the page." + warranty_warning,
        epilog="Author: Rafal Przetakowski <rprzetakowski@gmail.com>",
        formatter_class=RawTextHelpFormatter,
        conflict_handler='resolve'
    )
    parser.parse_args()

    # Get asyncio event loop to work asynchronous
    loop = asyncio.get_event_loop()

    # New SainsburysTechTest object
    sTest = SainsburysTechTest(loop)

    # Asyncio task
    asyncio.Task(
        sTest.run('http://hiring-tests.s3-website-eu-west-1.amazonaws.com/2015_Developer_Scrape/5_products.html'))

    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
    except RuntimeError:
        pass

    loop.run_forever()

    # Show result of SainsburysTechTest
    result = sTest.get_result()
    print (result)


if __name__ == "__main__":
    main()
