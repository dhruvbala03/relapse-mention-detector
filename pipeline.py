import pandas as pd
from datetime import datetime
import re

from relapse_regexes.dayxclean_regex import *
from relapse_regexes.iverelapsed_regex import *
from relapse_regexes.xdaysclean_regex import *

from dateparser.search import search_dates
from datetime import datetime
import shutup

shutup.please()


## Install all relevant libraries


MAX_NUM_MATCHES = 5  # max number of matches to display


# gets (up to) n words before and after occurence of match in s, usually producing a (2n+1)-gram
def get_surrounding_context(s, match, n):

    # moves back a word if dir=-1, moves up a word if dir=1; returns first/last word if boundary is reached
    def move_one_word(s, pos, dir=1):
        if dir == -1:
            while pos > 0:
                pos = pos - 1
                if s[pos] == ' ':
                    return pos+1
            return 0
        else:
            l = len(s)
            while pos < l-1:
                pos = pos + 1
                if s[pos] == ' ':
                    return pos
            return l

    rng = match.span()
    a = rng[0]
    b = rng[1]

    # expand range up to n words before and after match
    for i in range (0,n):
        a = move_one_word(s, a-1, -1)
        b = move_one_word(s, b+1, 1)

    return s[a:b]


# find regex matches for each post
def get_regex(df, args):
    # pass in as many parameters as needed ex. title and text for a post
    print('Matching regex expressions...')
    df['fulltext'] = ''
    for col in args:
        df['fulltext'] = df['fulltext'] + df[col]

    df = df.groupby("author").filter(lambda x: len(x) >= 2)

    # combines regexes for three cases
    def build_regex():
        regex_str = '|'.join([
            build_regex_dayxclean(), build_regex_iverelapsed(), build_regex_xdaysclean()
        ])
        return regex_str

    regex = build_regex()  
    
    # regex value should be "(?:(?:day|days|week|weeks|wk|wks|month|months|hour|hours|hr|hrs).{1,5}(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|[0-9]+).{1,5}(?:clean\s*|sober\s*|off))|(?:(?:I\s*|i\s*|I'*ve\s*|i'*ve\s*|i'*m\s*).{0,10}relaps(?:ed|ing)\s*)|(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|[0-9]+).{1,5}(?:day|days|week|weeks|wk|wks|month|months|hour|hours|hr|hrs).{1,5}(?:clean\s*|sober\s*))"

    posts = df['fulltext'].tolist()

    matcheslist = []  # list of matches list for each post
    matchCounts = []  # list of num matches for each post

    # get lists of matches and number of matches for each post
    for post in posts:
        post = str(post)
        post = post.replace("yr", "year"); post = post.replace("mth", "month"); post = post.replace("mo", "month")  # ensure that timeparser picks up essential time words
        post = post.replace("after", ""); post = post.replace("After", "")  # avoid getting negative window (the word 'after' causes timeparser to look for future--rather than past--dates)
        post = re.sub(r"(?:d|D)ay\s*(\d+)\s*clean", r"$1 days clean", post)  # handle "day x" case (else timeparser doesn't pick it up)
        matches = re.finditer(regex, post)
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

    # generate a list of columns 'regexmatch_i' for i from 0 to MAX_NUM_MATCHES
    regexmatch_columns = [ [matcheslist[r][c] for r in range(0,len(matcheslist))] for c in range(0,MAX_NUM_MATCHES) ]
    for i in range(0,len(regexmatch_columns)):
        df['regexmatch_'+str(i)] = pd.Series(regexmatch_columns[i])

    print('Regex Expressions matched.')
    return df


def extract_data(df):
    # given a text (regex match) and post date, identify a time window, if one exists; otherwise, return empty string
    def get_time_window(text, post_date):
        dateparser_settings = {"RELATIVE_BASE": post_date, 'PREFER_DATES_FROM': 'past'}
        possible_dates = search_dates(text, settings=dateparser_settings, languages=['en'])
        if possible_dates == None:
            return ""
        else:
            relapse_date = min([possible_date[1] for possible_date in possible_dates])
            time_window = post_date - relapse_date
            return time_window

    # create time window column for each regex match
    for i in range(0, MAX_NUM_MATCHES):
        df['window_'+str(i)] = df.apply(lambda x: get_time_window(x['regexmatch_'+str(i)], x['postDate'].to_pydatetime()), axis=1)
    
    # identify minimum time windows and create a column with these values
    minwindows = []
    for index,row in df.iterrows():
        windows = []
        for i in range(0,MAX_NUM_MATCHES):
            if row['window_'+str(i)] != "":
                windows.append(row['window_'+str(i)])
        if len(windows) == 0:
            minwindow = ""
        else:
            minwindow = min(windows)
        minwindows.append(minwindow)

    # we select the smallest time window
    df['selected_window'] = minwindows

    df.to_csv("output/relapse-dates.csv")
    print("Done!\n\nSee output/relapse-dates.csv\n")


def get_windows(file, *args):
    # load file and clean data.
    df = pd.read_csv(file)
    df = df[df.author != "[removed]"]
    df = df[df.author != "[deleted]"]

    # gather relapse disclosure posts using regular expressions.
    regex_df = get_regex(df, args)  

    print('Parsing Matches for time expressions...')

    # convert epoch value to pandas date time value.
    def getdate(epoch):    
        return pd.Timestamp(datetime.fromtimestamp(int(epoch)))

    # create a new column with datetime post values.
    regex_df['postDate'] = regex_df['created_utc'].apply(getdate)

    result = regex_df

    extract_data(result)


if __name__ == '__main__':
    # pass in the csv file name and the names of the column(s) you want to parse for relapse expressions.
    get_windows('opiatesrecovery-posts.csv', 'title', 'selftext')
