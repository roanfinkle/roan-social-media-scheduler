import pandas as pd
import calendar
import spacy
from datetime import datetime


# removes data entires that have expired links
def drop_expired_links(df, authors_df):
    indexes = authors_df[authors_df['authors'].isna()].index
    for i in indexes:
        df.drop(labels=i, inplace=True)

    return df

# inputs raw fb-seattle-times.csv file
# cleans up date, month, day, weekday, time, ampm
# outputs ordered lists for all these aspects 
def clean_seattle_data(data):
    calendar_date_list = []
    military_time_list = []
    for entry in data['published_at']:
        for char in str(entry):
            entry = str(entry)
            if char == ' ':
                split = str(entry).index(char)
                calendar_date_list.append(entry[0:split])
                military_time_list.append(entry[split+1:len(entry)-3])
                break

    weekday_number_list = []
    month_list = []
    day_list = []
    year_list = []
    for entry in calendar_date_list:
        month = int(entry[5:7])
        day = int(entry[8:10])
        year = int(entry[0:4])
        weekday_number_list.append(calendar.weekday(year, month, day))
        month_list.append(month)
        day_list.append(day)
        year_list.append(year)
        
    weekday_list = []
    for i in weekday_number_list:
        if i < 6:
            weekday_list.append(i+2)
        elif i == 6:
            weekday_list.append(1)

    hour_list = []
    time_list = []
    time_of_day_word_list = []
    for entry in military_time_list:
        hour_list.append(entry[:entry.index(':')])
        military_time = datetime.strptime(entry, '%H:%M')
        time_list.append(military_time.strftime('%I:%M'))
        time_of_day_word_list.append(military_time.strftime('%p'))

    time_of_day_list = []
    for i in time_of_day_word_list:
        if i == 'AM':
            time_of_day_list.append(0)
        elif i == 'PM':
            time_of_day_list.append(1)

    return calendar_date_list, month_list, day_list, year_list, weekday_list, hour_list, time_of_day_list


# inputs raw fb-seattle-times.csv file
# outputs ordered list of captions translated to utf8
def translate_seattle_captions(data):
    encoded = []
    for caption in data['message']:
        if isinstance(caption, str):
            encoded.append(caption.encode('utf-8'))
        else:
            encoded.append('')

    return encoded

# inputs list of captions
# loads in small//large nlp language model for text
# assigns asent pipeline                                                        * models and pipelines need to be downloaded via terminal *
# calculates polarity -1<p<1,: negative sentiment vs positive sentiment
# outputs ordered list of scores 
def asent_sentiment_score(captions):
    large_english_model = 'en_core_web_lg'
    small_english_model = 'en_core_web_sm'

    nlp = spacy.load(large_english_model)
    nlp.add_pipe('asent_en_v1')
    # rated_words = lexicons.get('emoji_v1')        * process emojis? which language model? *

    sentiment_scores = []
    for caption in captions:
        score = nlp(str(caption))._.polarity
        sentiment_scores.append(score.compound)

    return sentiment_scores


# inputs list of captions
# loads in sm/med/lg nlp language model for text 
# assigns spacytextblob pipeline                                                * models and pipelines need to be downloaded via terminal *
# calculates polarity -1<p<1: negative sentiment vs positive sentiment
# calculates subjectivity 0<s<1: objective vs subjective
# outputs 2 ordered lists of the scores
def textblob_sentiment_subjectivity_score(captions):
    large_english_model = 'en_core_web_lg'
    small_english_model = 'en_core_web_sm'

    nlp = spacy.load(large_english_model)
    nlp.add_pipe('spacytextblob')

    sentiment_scores = []
    subjectivity_scores = []
    for caption in captions:
        sent_score = nlp(str(caption))._.blob.polarity
        subj_score = nlp(str(caption))._.blob.subjectivity
        sentiment_scores.append(sent_score)
        subjectivity_scores.append(subj_score)

    return sentiment_scores, subjectivity_scores


# inputs raw fb-seattle-times.csv file
# scales asent sentiment from -1<s<1 to 0<s<2000
# scales textblob sentiment from -1<s<1 to 0<s<2000
# scales textblob subjectivity from 0<s<1 to 0<s<1000
# scales engagement from ... to ...
# outputs lists of all these aspects
def clean_seattle_for_dea(data):
    tb_sent_input, tb_subj_input = textblob_sentiment_subjectivity_score(translate_seattle_captions(data))
    asent_sent_input = asent_sentiment_score(translate_seattle_captions(data))
    eng_input = data['engagement_rate']

    asent_sent_output = []
    for entry in asent_sent_input:
        if str(entry) == '0':
            asent_sent_output.append(int(1000))
        else:
            entry = float(entry) + 1
            entry = str(entry)[0:5]
            entry = float(entry) * 1000
            asent_sent_output.append(int(entry))
    
    tb_sent_output = []
    for entry in tb_sent_input:
        if str(entry) == '0':
            tb_sent_output.append(int(1000))
        else:
            entry = float(entry) + 1
            entry = str(entry)[0:5]
            entry = float(entry) * 1000
            tb_sent_output.append(int(entry))

    tb_subj_output = []
    for entry in tb_subj_input:
        if str(entry) == '1':
            tb_subj_output.append(int(1000))
        else:
            entry = str(entry)[0:5]
            entry = float(entry) * 1000
            tb_subj_output.append(int(entry))

    eng_output = []
    for entry in eng_input:
        entry = str(entry)[:5]
        entry = float(entry) * 100
        entry = int(round(entry))
        eng_output.append(entry)

    return asent_sent_output, tb_sent_output, tb_subj_output, eng_output


# inputs raw fb-seattle-times.csv file
# outputs list of tokenized captions 
def tokenize_captions(data):
    captions = data['message']
    large_english_model = 'en_core_web_lg'
    small_english_model = 'en_core_web_sm'

    nlp = spacy.load(large_english_model)
    stop_words = spacy.lang.en.stop_words.STOP_WORDS

    tokens = []
    for caption in captions:
        temp = nlp(str(caption).lower())
        filtered = [token.lemma_ for token in temp if token.is_alpha and token.lemma_ not in stop_words]
        tokens.append(' '.join(filtered))

    return tokens


# inputs list of tokenized captions
# creates a txt file for every tokenized caption, which is used as Input for TopicModelingTool GUI downloaded online
def extract_seattle_captions(tokens):
    for i in range(0, 5706):
        filepath = '/Users/roanfinkle/Downloads/CRC/TopicModelingData/caption' + i +'.txt'
        with open(filepath, 'w') as file:
            file.write(tokens[i])


# inputs weighted topics csv which is generated from TopicModelingTool
# first line are general topic names I came up with based on the generated key words
# outputs a list of the dominant topic(s) for each caption
#
# it would probably be easier to do topic modeling in python with gensim
# we didn't even end up using this because I didn't like the results
#
def assemble_modeled_topics(topic_weights_df):
    topics = ['Health & Safety', 'City', 'Entertainment', 'Education', 'Contest', 'Sports']
    filenames = topic_weights_df['filename']
    t1 = topic_weights_df['T1']
    t1_weights = topic_weights_df['T1 Weight']
    t2 = topic_weights_df['T2']

    filenumbers = []
    for filename in filenames:
        length = len(filename)
        if length == 87:
            filenumbers.append(int(filename[length-8:length-4]))
        elif length == 86:
            filenumbers.append(int(filename[length-7:length-4]))
        elif length == 85:
            filenumbers.append(int(filename[length-6:length-4]))
        elif length == 84:
            filenumbers.append(int(filename[length-5:length-4]))

    topic_weights_df['filename'] = filenumbers    
    topic_weights_df = topic_weights_df.sort_values(by='filename', ascending=True)

    topics_list = []
    for i in range(0, len(topic_weights_df)):
        if float(t1_weights[i]) >= 0.4:
            topics_list.append(topics[t1[i]])
        else:
            temp = str(topics[t1[i]]) + ', ' + str(topics[t2[i]])
            topics_list.append(temp)

    return topics_list

# some of the links are shortened and some are in their true form
# if the link is shortened, this uses a webdriver to get its true form
def correct_links(data):
    links = data['link']

    fixed_links = []
    for link in links:
        if len(link) == 22 or len(link) == 23:
            try:
                driver = webdriver.Chrome()
                driver.get(str(link))
                fixed_links.append(str(driver.current_url))
            except Exception as e:
                print('Error: ' + str(e))
        else:
            fixed_links.append(link)

    return fixed_links


# grabs the subsection "topic" that appears in the website link
def assemble_website_topics(links):
    topics_list = []
    for link in links:
        if str(link)[:6] == 'http:/':
            link_no_domain = str(link)[28:]
            for char in link_no_domain:
                if char == '/':
                    topic = link_no_domain[:link_no_domain.index(char)]

                    if topic == 'seattle-news':
                        link_no_domain = link_no_domain[13:]
                        for char in link_no_domain:
                            if char == '/':
                                topic = link_no_domain[:link_no_domain.index(char)]
                                if str(topic) == 'politics' or str(topic) == 'environment' or str(topic) == 'education' or str(topic) == 'crime' or str(topic) == 'health' or str(topic) == 'weather' or str(topic) == 'transportation' or str(topic) == 'obituaries' or str(topic) == 'science':
                                    topics_list.append(topic)
                                else:
                                    topics_list.append('seattle-news')
                                break

                    else:
                        topics_list.append(topic)

                    break

        elif str(link)[:6] == 'https:':
            link_no_domain = str(link)[29:]
            for char in link_no_domain:
                if char == '/':
                    topic = link_no_domain[:link_no_domain.index(char)]

                    if topic == 'seattle-news':
                        link_no_domain = link_no_domain[13:]
                        for char in link_no_domain:
                            if char == '/':
                                topic = link_no_domain[:link_no_domain.index(char)]
                                if str(topic) == 'politics' or str(topic) == 'environment' or str(topic) == 'education' or str(topic) == 'crime' or str(topic) == 'health' or str(topic) == 'weather' or str(topic) == 'transportation' or str(topic) == 'obituaries' or str(topic) == 'science':
                                    topics_list.append(topic)
                                else:
                                    topics_list.append('seattle-news')
                                break

                    else:
                        topics_list.append(topic)

                    break

    return topics_list


# inputs raw fb-seattle-times.csv file, and topic weight distribution csv from TopicModelingTool
# outputs fully assembled and scaled dataframe
def assemble_seattle_for_dea(data, topic_weights, authors):
    new_data = pd.DataFrame()
    dates, months, days, years, weekdays, hours, ampm = clean_seattle_data(data)
    asent_sent, tb_sent, tb_subj, eng = clean_seattle_for_dea(data)
    topics = assemble_website_topics(correct_links(data))
    links = correct_links(data)

    # independant variables
    new_data['Link'] = links
    new_data['Month'] = months
    new_data['Day'] = days
    new_data['Weekday'] = weekdays
    new_data['Hour'] = hours
    new_data['Topic'] = topics
    new_data['Author'] = authors
    new_data['Asent_Sentiment'] = asent_sent
    new_data['Textblob_Sentiment'] = tb_sent
    new_data['Textblob_Subjectivity'] = tb_subj

    # dependant variables
    new_data['Engagement'] = eng
    new_data['Total_Reach'] = data['total_reach']
    new_data['Organic_Reach'] = data['organic_reach']
    new_data['Paid_Reach'] = data['paid_reach']
    new_data['Viral_Reach'] = data['viral_reach']
    new_data['Engaged_Users'] = data['engaged_users']
    new_data['Engaged_Page_Fans'] = data['engaged_page_fans']
    new_data['Other_Engaged_Users'] = data['other_engaged_users']
    new_data['Fan_Reach'] = data['fan_reach']
    new_data['Consumptions'] = data['consumptions']
    new_data['Link_Clicks'] = data['link_clicks']
    new_data['Photo_Views'] = data['photo_views']
    new_data['Video_Plays'] = data['video_plays']
    new_data['Other_Clicks'] = data['other_clicks']
    new_data['Total_Engagement'] = data['total_engagement']
    new_data['Likes'] = data['likes']
    new_data['Comments'] = data['comments']
    new_data['Shares'] = data['shares']
    new_data['Total_Impressions'] = data['total_impressions']
    new_data['Organic_Impressions'] = data['organic_impressions']
    new_data['Paid_Impressions'] = data['paid_impressions']
    new_data['Viral_Impressions'] = data['viral_impressions']
    new_data['Stories'] = data['stories']
    new_data['Story_Likes'] = data['story_likes']
    new_data['Story_Comments'] = data['story_comments']
    new_data['Story_Shares'] = data['story_shares']

    return new_data


if __name__ == '__main__':
    seattle_csv_file = pd.read_csv('/Users/roanfinkle/Downloads/CRC/fb-seattle-times.csv')
    topic_weights = pd.read_csv('/Users/roanfinkle/Downloads/CRC/Topic Modeling/6-800-3-10, 4294/output_csv/topics-in-docs.csv')
    authors = pd.read_csv('/Users/roanfinkle/Downloads/CRC/authors.csv')

    df_good_links = drop_expired_links(seattle_csv_file, authors)


    # this next line outputs the assembled data as a csv to given filepath, takes a little bit to run
    assemble_seattle_for_dea(df_good_links, topic_weights, authors).to_csv('/Users/roanfinkle/downloads/CRC/assembled-seattle-times.csv')