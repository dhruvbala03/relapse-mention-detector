
import re
from textblob import TextBlob
from spellchecker import SpellChecker
import nltk

TIME_WORDS = ["year", "yr", "month", "week", "wk", "day", "night", "nite", "hour", "hr"]

TIME_REGEX = "(?:" + "|".join(TIME_WORDS) + ")"

CONTEXT_SCOPE_RADIUS = 3

# TODO: deal with weird apostrophe issue, account for words like "won't" way earlier in the sentence? (next step)


# gets (up to) n words before and after occurence of match in s--usually producing a (2n+1)-gram
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


# returns true if s contains any member of list as a substring, false otherwise
def str_contains_any(s, list):
    for sub in list:
        if sub in s:
            return True
    return False


# # take in string
# print("\nenter source text: ")
# post = input()


def extract_time_mentions(post):
    # extract words from post 
    blob = TextBlob(post)
    words = blob.words
    words = [word.replace("[ ]*’[ ]*", "'") for word in words]  # TODO: fix -- so as to avoid issues with weird apostrophe
    #print(" ".join(words))

    # spell correction 
    spell = SpellChecker()
    mistakes = spell.unknown(words)
    spell.word_frequency.load_words(TIME_WORDS) 
    words_corrected = []
    for word in words:
        should_correct = False
        corrected = ""
        if word in mistakes:
            if not str_contains_any(word, TIME_WORDS):  # ensure that we are not losing any info by falsely correcting time words
                corrected = spell.correction(word)
                if corrected != None:
                    should_correct = True
        words_corrected.append(corrected if should_correct else word)


    s = " ".join(words_corrected).lower()
    print("\nspell corrected: \n" + s)


    # find regex matches
    matches = re.finditer(TIME_REGEX, s)

    # extract context for each match
    contexts = [get_surrounding_context(s, match, CONTEXT_SCOPE_RADIUS) for match in matches]

    print("\nMATCHES:")
    print(contexts)
    print("\n")





# TEST CASES:

## INPUT
### OUTPUT

## one year ago I tried to eat paper, and it did not taste very good.  I puked for 5 days straight
### ['one year ago i tried', 'puked for 5 days straight']

## I’m 7 days oxy free in inpatient detox and need advice
### ['i i 7 days oxy free in']

## The doctor on site said I can take 1mg a day and go down the next 3 days I’m here to an even lower dose that I can keep tapering at home or I can just stop taking it.
### ['take my a day and go down', 'the next 3 days i i i']

## i went running a couple daays ago and it wad fun.  wont be doing it for weejfks, though
### ['running a couple days ago and it', 'doing it for weeks though']

## one time moinths ago on a rainy day i went  swmming
### ['one time months ago on a', 'on a rainy day i went swimming']

## It has been 3 wks since I relsaped.  before that i  relapsed once 4 yrs ago
### ['has been 3 wks since i released', 'relapsed once 4 yrs ago']

