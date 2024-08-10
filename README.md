# Roan's work for the Social Media Scheduler Project at the CRC.

Here I will give a walkthrough of my code in case someone picks up where I left off.

First we will start with WebScrapingAuthors.py. This deploys a webdriver and grabs the author(s) that wrote each article. It is important to run this first because a lot of the links in the beginning of the dataset are expired, and this will classify these. I ran batches of our dataset in parallel python threads in order to save time scraping. The final output of this algorithm is authors.csv, an ordered list of authors or lack thereof.

Next is AssemblingSeattleTimes.py. This cleans up the time of the post, runs sentiment analysis (and scales the result to nonnegative), and assembles the dataset with author and topic. The output of this algorithm is cleaned-seattle-times.csv.

Next, in order to run DEA, I used R studio to remove some columns and create dummy variables for weekday & hour. For example, a post from Sunday at 1pm will have the Asent Sentiment score in Sunday column, Textblob Sentiment score in Hour13 column, and 0 in all other weekday & hour columns. The final dataframe for DEA is seattle_with_dummies.csv.

Finally we have SeattleDEA.R which is our optimization model. Assuming all filepaths are correct, this should run smoothly. However, the model isn't calculating the precise efficiency scores correctly, and we never figured out why. However, when you plot the frontier, you can spot the key DMUs that we need.



