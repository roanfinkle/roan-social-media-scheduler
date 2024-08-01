# Roan's work for Social Media Scheduler Project at the CRC.

Here I will give a walkthrough of my code in case someone picks up where I left off.

First we will start with WebScrapingAuthors.py. This algorithm deploys a Selenium webdriver and grabs the author(s) that wrote each article. It is important to run this first because a lot of the links in the beginning of the dataset are expired, and this will classify these. I ran batches of our dataset in parallel python threads in order to save time scraping. The final output of this algorithm is authors.csv, an ordered list of authors or lack thereof.


