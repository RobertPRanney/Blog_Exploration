# Project Progress
I seem to have trouble remmbering from day to day so here I will keep track

##### 7/18 - Monday
* Finished off the rest of the api pulling functions, can pull blog info given a url, can pull all posts given an id taken from that info. This brings down lots of meta data that I need to make into interesting features
* Decided on a subset, have to abandon data science as it doesn't seem to get much traffic, going with fitness
* wasted a few hours of my life on grabbing links from google search, I woluld like to write a scraper but even doing it manually google gets mad, a few hours of life down the drain for 8500 links. Yields about 3500 URLS. Some of these will be garbage, need to decide how to filter them out

##### 7/19 - Tuesday
* Made a script to get all blog info from the api, and then put it into a mongodb, tested it on local. Lots of issues prevent can pop up though, so many try except blocks and errors are written to a text file for later viewing
* got ec2 instance running, probably an overkill one, will transfer mongodb info to something else when it finishes and kill it
* get mongodb installed and running on ec2 instance, took too much time
* data collection script running on ec2 instance, detach in own tmux session. Rough guess is it will take 20 hours to collect.
* Examined error log and found key insert issues, lots of them, investigated it a bit tonight, not sure where, but built structure chart to help out.

##### 7/20 - Wednesday
* Found issues with key inserts. Post json object has three fields that are dicts where the keys are just whatver garbage a person makes, and the values hold stuff like url. So lots of poorly formatted junk there. Made aggregates of these in data collection step.
* Rewrote blog collectiion script, is more efficient when limiting size, and is utilizes threading, maybe could even make it multi processing and gather data super fast in the future.
* Well, didn't understand storage/memory junk, asked tim and erich, now understand it better. New bigger instance, should do better this time.
* Made a play set from first 100 possible urls, got 71 blogs to play with, dumped to csv file with mongo export, not sure if this is best way, ask tommorow. 


* TO DO:
    1) polish resume, finsih structure chart of data, I keep getting confused, start thinking of way to filter to a usable amount of blogs. Investigate on small local subset.