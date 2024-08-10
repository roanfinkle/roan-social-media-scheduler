import pandas as pd
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import requests
import os
from selenium.common.exceptions import TimeoutException, InvalidArgumentException, WebDriverException
import argparse


def author_web_scraping(data):
    # run this in console first, only need to one time: ChromeDriverManager().install
    all_links = data['link']

    # try/except checks if link is expired, declares True/False for the iteration
    authors_list = []
    counter = 0
    try:
        for link in all_links:
            temp_author = ''
            exists: bool

            try: 
                # options = webdriver.ChromeOptions()
                # options.add_argument('--headless')
                # driver = webdriver.Chrome(options=options) 
                driver = webdriver.Chrome()
                driver.get(str(link)) 
                wait = WebDriverWait(driver, 3)
                wait.until(lambda d: d.find_element(By.CSS_SELECTOR, 'span[itemprop="name"]').is_displayed())
                exists = True
            except (TimeoutException, InvalidArgumentException, WebDriverException):
                exists = False
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
                exists = False
            
            # if link is valid, appends author(s) to a dict. if link is expired, appends ''
            if exists:
                authors_html = driver.find_elements(By.CSS_SELECTOR, 'span[itemprop="name"]')

                temp_authors = []
                for author_html in authors_html:
                    temp_authors.append(author_html.text)

                if len(temp_authors) > 1:
                    temp_author = ', '.join(temp_authors).lower()
                else:
                    temp_author = temp_authors[0].lower()

                entry_dict = {'link': link, 'authors': temp_author}
                authors_list.append(entry_dict)

            elif not exists:
                entry_dict = {'link': link, 'authors': ''}
                authors_list.append(entry_dict)

            print(f'\nPID:{os.getpid()}, iterations:{counter}, author:{temp_author}, link:{link}')
            counter += 1

    except (SystemExit, KeyboardInterrupt):
        print('Interrupted by User')

    finally: 
        try:
            driver.close()
        except: 
            pass

    return pd.DataFrame.from_records(authors_list)


def parse():
    parser = argparse.ArgumentParser(description="Scrapes things.")

    parser.add_argument('--batch', type=int, required=True, help="The batch number to process")
    args = parser.parse_args()

    # read the value
    print(f"Processing batch {args.batch}")
    
    return args


def scrape_authors():
    args = parse()

    batch_size = 100
    start = int(args.batch) * batch_size     # batch 0 -> 0;    batch 1 -> 100;   batch 2 -> 200, etc
    end = start + batch_size 

    seattle_csv_file = pd.read_csv('/Users/roanfinkle/Downloads/CRC/fb-seattle-times.csv')
    authors_df = author_web_scraping(seattle_csv_file.iloc[start:end])
    
    pid = os.getpid()
    authors_df.to_csv('/Users/roanfinkle/Downloads/CRC/authors/authors-df-' + str(pid) + '.csv', index=False)

# after running the batches for web scraping, come back and run this
# takes all batches and alligns correctly with entries
def order_authors(ordered_data):
    ordered_links = ordered_data['link']
    files = []
    unordered_links: list = []
    authors: list = []
    directory = '/Users/roanfinkle/Downloads/CRC/authors'

    for file in os.listdir(directory):
        if file.endswith('.csv'):
            file = str(file)[:len(str(file))-4]
            files.append(int(file))
    
    files = sorted(files)

    for file in files:
        df = pd.read_csv(directory + '/' + str(file) + '.csv')
        for link in df['link']:
            unordered_links.append(link)
        for author in df['authors']:
            authors.append(author)

    length = []
    for author in authors:
        if ',' not in str(author):
            length.append(author)

    print(len(set(length)))
    return pd.DataFrame(authors)


if __name__ == '__main__':
    # scrape_authors()

    seattle_csv_file = pd.read_csv('/Users/roanfinkle/Downloads/CRC/fb-seattle-times.csv')
    export_authors = order_authors(seattle_csv_file)
    export_authors.to_csv('/Users/roanfinkle/Downloads/CRC/authors.csv')

