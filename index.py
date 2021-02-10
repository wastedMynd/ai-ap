import random

import requests
import os
from urllib.parse import urlparse
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec

from selenium.webdriver.support.wait import WebDriverWait

from driver import get_browser
from utils import sleep
from selenium.webdriver.common.by import By
import cli_colour_utils as makeup
from threading import Thread


# links and locators for com.ai-ap
base = 'https://www.ai-ap.com/'
landing_page = f'{base}/archive/AI/#'

user_agent_list = [
        ('Mozilla/5.0 (X11; Linux x86_64) '
         'AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/57.0.2987.110 '
         'Safari/537.36'),  # chrome
        ('Mozilla/5.0 (X11; Linux x86_64) '
         'AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/61.0.3163.79 '
         'Safari/537.36'),  # chrome
        ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
         'Gecko/20100101 '
         'Firefox/55.0'),  # firefox
        ('Mozilla/5.0 (X11; Linux x86_64) '
         'AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/61.0.3163.91 '
         'Safari/537.36'),  # chrome
        ('Mozilla/5.0 (X11; Linux x86_64) '
         'AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/62.0.3202.89 '
         'Safari/537.36'),  # chrome
        ('Mozilla/5.0 (X11; Linux x86_64) '
         'AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/63.0.3239.108 '
         'Safari/537.36'),  # chrome
    ]


def main():
    download_dir = os.path.join(os.environ.get("HOME"), "Downloads/ai-ap/")
    os.makedirs(download_dir, exist_ok=True)

    # region go to the landing page
    browser = get_browser()
    browser.get(landing_page)
    # endregion

    try:
        while next_button := WebDriverWait(browser, 30).until(
                ec.presence_of_element_located((By.LINK_TEXT, "Next"))
        ):
            # scrap with paging
            artist = (By.XPATH, "//span[@class='artist']")

            if (WebDriverWait(browser, 30).until(
                    ec.presence_of_element_located(artist)
            )) is None:
                continue

            artists = browser.find_elements_by_xpath(artist[1])
            for artist_name_element in artists:
                artist_name_element.click()
                sleep(30)
                if (art := WebDriverWait(browser, 30).until(
                        ec.presence_of_element_located((By.ID, "slide_img"))
                )) is None:
                    continue

                # region check existence of art and downloading it when it is not present..

                url = art.find_element_by_tag_name("img").get_attribute("src")
                image_name = os.path.basename(urlparse(url).path)

                download_path = os.path.join(download_dir, image_name)

                # checking download file-size
                os.makedirs(download_dir, exist_ok=True)
                file_size = 0 if not os.path.exists(download_path) else os.stat(download_path).st_size

                headers = {
                    "User-Agent": random.choice(user_agent_list),
                    'Accept-Language': 'en-US,en;q=0.5',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Range': f'bytes={file_size}-'
                }

                print(makeup.mockup_text_as_ok_blue("attempting to download..."),
                      makeup.mockup_text_as_bold_white(image_name))

                initial_response = requests.head(url)

                length = int(initial_response.headers.get("content-length"))

                if file_size < length:
                    with requests.get(url, headers=headers, stream=True) as response:
                        with open(download_path, 'a+b') as downloaded_file:
                            for chunk in response.iter_content(chunk_size=1024):
                                downloaded_file.write(chunk)

                    print(makeup.mockup_text_as_bold_white(image_name),
                          makeup.mockup_text_as_ok_green(" downloaded!"))
                else:
                    print(makeup.mockup_text_as_bold_white(image_name),
                          makeup.mockup_text_as_fail_red(" already downloaded!"))

                # endregion

                # locate close button
                if (close_btn := WebDriverWait(browser, 30).until(
                        ec.presence_of_element_located((By.LINK_TEXT, "Close"))
                )) is None:
                    continue

                # go back last page
                close_btn.click()
                sleep(20)

            # click on next button
            next_button.click()
            print(makeup.mockup_text_as_ok_blue(makeup.mockup_text_as_bold_white("going to the next set...")))

    except TimeoutException:
        print(makeup.mockup_text_as_fail_red(makeup.mockup_text_as_bold_white("end of set")))

    finally:
        browser.close()


if __name__ == '__main__':
    main()
