import re

regex = "(?:(?:day|days|week|weeks|wk|wks|month|months|hour|hours|hr|hrs).{1,5}(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|[0-9]+).{1,5}(?:clean\s*|sober\s*|off))|(?:(?:I\s*|i\s*|I'*ve\s*|i'*ve\s*|i'*m\s*).{0,10}relaps(?:ed|ing)\s*)|(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|[0-9]+).{1,5}(?:day|days|week|weeks|wk|wks|month|months|hour|hours|hr|hrs).{1,5}(?:clean\s*|sober\s*))"

#r"(?:(?:day|days|week|weeks|wk|wks|month|months|hour|hours|hr|hrs).{1,5}(?:^a(?=\s)|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|[0-9]+).{1,5}(?:clean\s|sober\s|off))|(?:(?:I\s|i\s|I've\s|i've\s|i'm\s).{0,10}relaps(?:ed|ing)\s)|(?:(?:^a(?=\s)|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|[0-9]+).{1,5}(?:day|days|week|weeks|wk|wks|month|months|hour|hours|hr|hrs).{1,5}(?:clean\s|sober\s))"

s = input()

matches = re.findall(regex, s)

print(matches)

# this is day 5 clean I am not sure how I will do it this time, 3 days clean, ive relapsed 