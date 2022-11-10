import pandas as pd
from datetime import datetime
from datetime import timedelta
import re
from sutime import SUTime
import matplotlib.pyplot as plt

from relapse_regexes.dayxclean_regex import *
from relapse_regexes.iverelapsed_regex import *
from relapse_regexes.xdaysclean_regex import *


# Install all relevant libraries including SUTime.
# SUTime installation instructions: https://github.com/FraBle/python-sutime
def get_regex(df, args):
    # pass in as many parameters as needed ex. title and text for a post
    print('Matching regex expressions...')
    df['fulltext'] = ''
    for col in args:
        df['fulltext'] = df['fulltext'] + df[col]

    df = df.groupby("author").filter(lambda x: len(x) >= 2)


    def build_regex():
        regex_str = '(?:' + '|'.join([
            build_regex_dayxclean(), build_regex_iverelapsed(), build_regex_xdaysclean()
        ]) + ')'

        return "(" + regex_str + ")"
        
    # def build_regex():
    #     # order: SELF then RELAPSE
    #     regex_str = ''.join([
    #         '.{0,50}', SELF_REGEX, '.{0,10}', RELAPSE_REGEX, '.{0,50}'
    #     ])

    #     return "(" + regex_str + ")"

    regex = build_regex()
    print(regex)
    df['regexmatch'] = df.fulltext.astype(str).str.extract(regex, flags=re.IGNORECASE, expand=False)
    result = df[~df['regexmatch'].isna()]
    print('Regex Expressions matched.')
    return result


def extract_data(df):
    def getWindow(post_date, relapse_date):
        post = datetime.strptime(post_date, "%Y-%m-%d")
        try:
            relapse = datetime.strptime(relapse_date, "%Y-%m-%d")
        except ValueError:
            try:
                relapse = datetime.strptime(relapse_date, "%Y-%m")
            except ValueError:
                return None
        window = post - relapse
        days = window / timedelta(days=1)
        if days < 0:  # catches errors such as "a year later" where relapse is in reference to another event
            return None
        else:
            return days

    def Datetime_format(timex_value):
        if len(timex_value) > 7:
            return timex_value[0:10]
        else:
            return timex_value

    df['time_x'] = df['sutime_results'].map(lambda v: v['value'])
    df['window'] = df.apply(lambda x: getWindow(Datetime_format(x['postDate']), Datetime_format(x['time_x'])), axis=1)
    print('mean: ' + str(df['window'].mean()))
    print('median: ' + str(df['window'].median()))
    bins = []

    # start val at 10 if 0 is a big outlier.
    val = 0
    while val < 1000:
        bins.append(val)
        val = val + 10
    plt.hist(df.window, bins, color="black")
    plt.savefig('window-data.jpg', dpi=300)
    df.to_csv("relapse-dates.csv")


def get_windows(file, *args):
    # loading the file and cleaning the data.
    df = pd.read_csv(file)
    df = df[df.author != "[removed]"]
    df = df[df.author != "[deleted]"]

    # gathering relapse disclosure posts using regular expressions.
    regex_df = get_regex(df, args)

    print('Parsing Matches for time expressions...')
    sutime = SUTime(mark_time_ranges=False, include_range=False)

    def getdate(epoch):
        # converts epoch value to date time.
        return str(datetime.fromtimestamp(int(epoch)))

    def getTime(refDate, text):
        exclude = ['SET', 'DURATION', 'PAST_REF', 'PRESENT_REF']
        # The results of Type, Duration, and Set are being excluded as well as dates of the generic type PAST_REF and
        # PRESENT_REF.
        temporals = sutime.parse(text, refDate)
        for i in temporals:
            # Returning the first time expression of type date.
            if i['type'] not in exclude and i['value'] not in exclude:
                return i
        return None

    # creating a new column with datetime post values.
    regex_df['postDate'] = regex_df['created_utc'].apply(getdate)

    # Passing the text and post date value into a function that calls SUTime parsing.
    regex_df['sutime_results'] = regex_df.apply(lambda x: getTime(x['postDate'], x['regexmatch']), axis=1)

    # excluding results where no date value was found.
    result = regex_df[~regex_df['sutime_results'].isna()]

    # calculating windows and displaying the data.

    extract_data(result)


if __name__ == '__main__':
    # Pass in the csv file name and the names of the column(s) you want to parse for relapse expressions.
    get_windows('opiatesrecovery-posts.csv', 'title', 'selftext')