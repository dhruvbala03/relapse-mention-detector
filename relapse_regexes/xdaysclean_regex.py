

# regular expression - follows the format "X days clean"

DATE_REGEX = '(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|[0-9]+)'

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

CLEAN_REGEXES = [
"clean",
"sober",
]

CLEAN_REGEX = '(?:' + '\\s*|'.join(CLEAN_REGEXES) + '\\s*)'
# be careful about the number of whitespaces around each component

def build_regex_xdaysclean():

    regex_str = ''.join([
        DATE_REGEX,
        '.{1,5}',
        TIME_REGEX,
        '.{1,5}',
        CLEAN_REGEX,
    ])

    return "(?:" + regex_str + ")"


