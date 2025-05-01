from streamlit import columns
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import string, re, emoji

extractor = URLExtract()



def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch number of messages
    num_messages = df.shape[0]

    # fetch number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    #fetch number of media messages:
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    #fetch number of links shared:
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    temp = df[df['user'] != 'group_notification']
    x = temp['user'].value_counts().head()
    df = round((temp['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns = {'user':'user', 'count':'percent'})
    return x,df

def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('omitted', case=False, na=False)]

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    words = []
    for message in temp['message']:
        # Remove punctuation, emojis, and special characters
        message = re.sub(r'[^a-zA-Z0-9\s]', '', message)
        for word in message.lower().split():
            if word not in stop_words and word!='message' and word!='deleted' and word!='null':
                words.append(word)
    cleaned_text = " ".join(words)


    wc = WordCloud(width=500, height=500, min_font_size=10, background_color="white")
    df_wc = wc.generate(cleaned_text)
    return df_wc

def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('omitted', case=False, na=False)]

    words = []
    for message in temp['message']:
        # Remove punctuation, emojis, and special characters
        message = re.sub(r'[^a-zA-Z0-9\s]', '', message)
        for word in message.lower().split():
            if word not in stop_words and word!='message' and word!='deleted'and word!='null':
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis)))).rename(columns = {0:'emoji', 1:'count'})
    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Step 1: Convert datetime to just date
    df['only_date'] = df['date'].dt.date

    # Step 2: Group by date and count messages per day
    daily_messages = df.groupby('only_date').count()['message'].reset_index()

    # Step 3: Convert back to datetime and get day name
    daily_messages['only_date'] = pd.to_datetime(daily_messages['only_date'])
    daily_messages['day_name'] = daily_messages['only_date'].dt.day_name()

    # Step 4: Compute average messages per weekday
    avg_per_day = daily_messages.groupby('day_name')['message'].mean()

    # Step 5: Sort by weekday order
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    avg_per_day = avg_per_day.reindex(weekday_order, fill_value=0)

    return avg_per_day.sort_values(ascending=False)

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    # Truncate datetime to just date
    df['only_date'] = df['date'].dt.date

    # Group by date
    daily_messages = df.groupby('only_date').count()['message'].reset_index()
    daily_messages['only_date'] = pd.to_datetime(daily_messages['only_date'])
    daily_messages['month_name'] = daily_messages['only_date'].dt.month_name()

    # Average messages per month
    avg_per_month = daily_messages.groupby('month_name')['message'].mean()

    # Sort month order
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    avg_per_month = avg_per_month.reindex(month_order, fill_value=0)

    return avg_per_month.sort_values(ascending=False)



def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap
