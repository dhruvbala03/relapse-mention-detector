import pandas as pd
from datetime import datetime
from datetime import timedelta
import re
from sutime import SUTime
import matplotlib.pyplot as plt

from relapse_regexes.dayxclean_regex import *
from relapse_regexes.iverelapsed_regex import *
from relapse_regexes.xdaysclean_regex import *
from time_mention_identifier import get_surrounding_context


# Install all relevant libraries including SUTime.
# SUTime installation instructions: https://github.com/FraBle/python-sutime

MAX_NUM_MATCHES = 5

# n is the number of match columns
def get_regex(df, args):  # TODO: see line 114
    # pass in as many parameters as needed ex. title and text for a post
    print('Matching regex expressions...')
    df['fulltext'] = ''
    for col in args:
        df['fulltext'] = df['fulltext'] + df[col]

    df = df.groupby("author").filter(lambda x: len(x) >= 2)


    # def build_regex():
    #     regex_str = '|'.join([
    #         build_regex_dayxclean(), build_regex_iverelapsed(), build_regex_xdaysclean()
    #     ])

    #     return regex_str
    

    # regex = build_regex()

    regex = "(?:(?:day|days|week|weeks|wk|wks|month|months|hour|hours|hr|hrs).{1,5}(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|[0-9]+).{1,5}(?:clean\s*|sober\s*|off))|(?:(?:I\s*|i\s*|I'*ve\s*|i'*ve\s*|i'*m\s*).{0,10}relaps(?:ed|ing)\s*)|(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|[0-9]+).{1,5}(?:day|days|week|weeks|wk|wks|month|months|hour|hours|hr|hrs).{1,5}(?:clean\s*|sober\s*))"

    MAX_NUM_MATCHES = 5  # number of matches to display
    posts = df['fulltext'].tolist()

    matcheslist = []  # list of matches list for each post
    matchCounts = [] # list of booleans indicating whether post has matches

    for post in posts:
        matches = re.finditer(regex, str(post))
        matches = [ get_surrounding_context(post, match, 3) for match in matches ]
        l = len(matches)
        matchCounts.append(l)
        if l < MAX_NUM_MATCHES:
            matches.extend(['' for i in range(0,MAX_NUM_MATCHES-l)])
        else:
            matches = matches[0:MAX_NUM_MATCHES]
        matcheslist.append(matches)

    df['num_matches'] = pd.Series(matchCounts)

    # filter out posts that don't have any matches
    df = df.loc[df['num_matches'] > 0]

    # want a list of columns 'regexmatch_i' for i from 0 to MAX_NUM_MATCHES
    regexmatch_columns = [ [matcheslist[r][c] for r in range(0,len(matcheslist))] for c in range(0,MAX_NUM_MATCHES) ]

    for i in range(0,len(regexmatch_columns)):
        df['regexmatch_'+str(i)] = pd.Series(regexmatch_columns[i])
    
    df.to_csv("regex-matches.csv")

    print('Regex Expressions matched.')
    return df


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
    regex_df = get_regex(df, args)  # TODO: how should I integrate multiple series?

    print('Parsing Matches for time expressions...')
    sutime = SUTime(mark_time_ranges=False, include_range=False)

    def getdate(epoch):
        # converts epoch value to date time.
        return str(datetime.fromtimestamp(int(epoch)))

    def getTime(refDate, text):
        exclude = ['SET', 'DURATION', 'PAST_REF', 'PRESENT_REF']
        # The results of Type, Duration, and Set are being excluded as well as dates of the generic type PAST_REF and
        # PRESENT_REF.
        temporals = sutime.parse(str(text), refDate)
        for i in temporals:
            # Returning the first time expression of type date.
            if i['type'] not in exclude and i['value'] not in exclude:
                return i
        return None

    # creating a new column with datetime post values.
    regex_df['postDate'] = regex_df['created_utc'].apply(getdate)

    # Passing the text and post date value into a function that calls SUTime parsing.
    def getRegexMatchList(columnEntry):
        if columnEntry == '':
            return -1
        return columnEntry.split(' ||.|| ')  # splitting by delimiter from earlier

    def getMinTime(row):
        matches = getRegexMatchList(row['regexmatch'])
        if matches == -1:
            return -1
        times = []
        for match in matches:
            # print("\n\npost date: " + row['postDate'] + "\tmatch: " + match)
            time = getTime(row['postDate'], match)
            print(time)
            times.append(time)
        return 0 #min(times)


    # for i in range(0,MAX_NUM_MATCHES):
    #     regex_df['sutime_results'+str(i)] = regex_df.apply(lambda x: getTime(x['postDate'], x['regexmatch_'+str(i)]), axis=1)

    regex_df['sutime_results'] = regex_df.apply(lambda x: (getTime(x['postDate'], x['regexmatch_0']) if x['regexmatch_0'] != '' else -1), axis=1)

    regex_df.to_csv("sutime-extractions.csv")

    # # excluding results where no date value was found.
    # result = regex_df[~regex_df['sutime_results'].isna()]

    # calculating windows and displaying the data.

    result = regex_df

    extract_data(result)


if __name__ == '__main__':
    # Pass in the csv file name and the names of the column(s) you want to parse for relapse expressions.
    get_windows('opiatesrecovery-posts.csv', 'title', 'selftext')
