# Relapse Mention Detector

This is a Python script (`pipeline.py`) that analyzes a dataset from r/opiatesrecovery (`opiatesrecovery-posts.csv`), scanning for mentions of relapse; if an instance of relapse is discussed, the script attempts to infer the time window between the relapse incident and the date of posting.  

The resulting output is a new csv file (`output/relapse-dates.csv`), containing additional columns for all posts with detected instances of relapse, the corresponding regex matches, time windows for each match, and selected time window.

Before running `pipeline.py`, make sure to install all necessary packages, by running the following commands in the project directory: 

  `pip install pandas`
  
  `pip install dateparser`
  
  
