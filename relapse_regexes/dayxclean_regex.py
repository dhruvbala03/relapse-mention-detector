

TIME_REGEXES = [
"day",
"days",
"week",
"weeks",
"wk",
"wks",
"month",
"months",
"hour",
"hours",
"hr",
"hrs"
]
TIME_REGEX = '(?:' + '|'.join(TIME_REGEXES) + ')'

DATE_REGEX = '(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|[0-9]+)'


CLEAN_REGEXES = [
"clean",
"sober",
"off"
]

CLEAN_REGEX = '(?:' + '\\s*|'.join(CLEAN_REGEXES) + ')'


# be careful about the number of whitespaces around each component

def build_regex_dayxclean():

    regex_str = ''.join([
        TIME_REGEX,
        '.{1,5}',
      # allowing 1 to 5 characters in between each component
        DATE_REGEX,
        '.{1,5}',
        CLEAN_REGEX,  
    ])

    return "(?:" + regex_str + ")"



