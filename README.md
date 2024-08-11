# Roan's work for the Social Media Scheduler Project at the CRC Summer 2024.

Here I will give a walkthrough of my code in case someone picks up where I left off.

First we will start with WebScrapingAuthors.py. This deploys a webdriver and grabs the author(s) that wrote each article. It is important to run this first because a lot of the links in the beginning of the dataset are expired, and this will classify these. I ran batches of our dataset in parallel python threads in order to save time scraping. The final output of this algorithm is authors.csv, an ordered list of authors or lack thereof.

Next is AssemblingSeattleTimes.py. This cleans up the time of the post, runs sentiment analysis, and assembles the dataset with author and topic. There are annotations within the code that are more clear. The output of this algorithm is cleaned-seattle-times.csv.

Next, in order to run DEA, I used R studio to remove some columns and create dummy variables for weekday & hour. For example, a post from Sunday at 1pm will have the Asent Sentiment score in Sunday column, Textblob Sentiment score in Hour13 column, and 0 in all other weekday & hour columns. The final dataframe that will be used for DEA is seattle_with_dummies.csv.

Finally we have SeattleDEA.R which is our optimization model for the Seattle dataset. Assuming all filepaths are correct, this should run smoothly. However, the model isn't calculating the precise efficiency scores correctly, and we never figured out why. However, when you plot the frontier, you can spot the key DMUs that we need.

I've also attached a public dataset that I found online and cleaned to the best of my ability, newspapers-facebook.csv. Here is the link that I got it from, there is still more to clean if necessary: https://data.world/martinchek/2012-2016-facebook-posts/workspace/project-summary?agentid=martinchek&datasetid=2012-2016-facebook-posts

If you get confused or have any questions, please reach out:
rfinkle@purdue.edu , rfinkle@nd.edu
