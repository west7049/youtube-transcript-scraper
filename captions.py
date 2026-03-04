# modify these values
filename = 'videos.csv'                                           # filename with video ids
colname = 'contentDetails_videoId'                                # column storing video ids
publishedcolname = 'contentDetails_videoPublishedAt'              # column storing video upload time
delimiter = ','                                                   # delimiter, e.g. ',' for CSV or '\t' for TAB
sleeptime = [5,15]                                                # random seconds range before fetching next video id

#do not modify below
from time import sleep
import csv
import json
import random
import os.path

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

ytt_api = YouTubeTranscriptApi()

def storecaptions(writefilename, captions=""):
    file = open(writefilename, "w", encoding="utf-8")
    file.write(captions)
    file.close()

def gettranscript(videoid, publishedAt):
    # check if transcript file already exists
    filekey = "_".join([publishedAt, videoid]) if publishedAt else videoid
    writefilename = 'captions/transcript_%s.txt' % filekey
    if os.path.isfile(writefilename):
        return 'transcript file already exists'

    try:
        transcript = ytt_api.fetch(videoid).to_raw_data()
    except TranscriptsDisabled:
        storecaptions(writefilename)
        return 'video has no captions'
    except NoTranscriptFound:
        storecaptions(writefilename)
        return 'no transcript found'
    except VideoUnavailable:
        return 'video unavailable'
    except Exception as e:
        return 'error: %s' % str(e)

    captions = json.dumps(transcript, sort_keys=True, indent=4)
    storecaptions(writefilename, captions)

    # cool down
    sleep(random.uniform(sleeptime[0], sleeptime[1]))

    return 'ok'

# log function
def logit(id, msg):
    logwriter.writerow({'id': id, 'msg': msg})

# prepare log file
logwrite = open('captions.log', 'w', newline='\n')
logwriter = csv.DictWriter(logwrite, fieldnames=['id', 'msg'])
logwriter.writeheader()

# read CSV file
csvread = open(filename, newline='\n')
csvreader = csv.DictReader(csvread, delimiter=delimiter, quoting=csv.QUOTE_NONE)
rowcount = len(open(filename).readlines())

for row in csvreader:
    videoId = row[colname]
    publishedOn = row[publishedcolname] if publishedcolname in row else None
    msg = gettranscript(videoId, publishedOn)
    logit(row[colname], msg)
    rowcount -= 1
    print(str(rowcount) + " :  " + row[colname] + " : " + msg)