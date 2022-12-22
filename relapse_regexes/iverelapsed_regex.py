
# regular expression - follows the format "I've relapsed"

SELF_REGEXES = [
"I",
"i",
"I'*ve",
"i\'*ve",
"i\'*m"
]
SELF_REGEX = '(?:' + '\\s*|'.join(SELF_REGEXES) + '\\s*)'
# be careful about the number of whitespaces around each component

RELAPSE_REGEX = 'relaps(?:ed|ing)' + '\\s*'

def build_regex_iverelapsed():
    '''
    Returns a compiled regex with the definitions
    '''
    #order: SELF then RELAPSE
    regex_str = ''.join([
        SELF_REGEX,
        '.{0,10}',
        RELAPSE_REGEX,
    ])

    return "(?:" + regex_str + ")"



