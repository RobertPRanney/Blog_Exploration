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
* Made progress on looking through structure and brain storming feature engineering

##### 7/21 - Thursday
* Looking through structure some more, chart all done and laid out
* added comments to post collection, probably could have done them as insert to mongo, but I am crap at mongo so quick and lazy is add them to script and re collect
* Change all arggrate dicts in collection to return list of keys
* Collecting new database with comments on ec2 instance. This drastically increases the time of collection. Can get 20 posts per call, but getting comments then requires 20 mores calls. Yuck. Time maybe 10 hours, maybe time to think about multiple cores.
* Need to choose NLP method for posts ---
* Have game plan  --- A good blog is made from good posts, so first step is to make a model for just good posts. Going to take all

##### 7/22 - Friday
* cleaning of blog dataframe continues
* cleaning of posts dataframe continues
* all blog posts put into data frame
* tfidf for blogs created
* tossed out empty blogs, not sure how I have empty blogs
* Not the most productive day

##### 7/23 - Saturday
* got nmf for tfidf
* wrote function to calculate values needed for reconstruction_err plot
* relocated accesssory stuff to a helper file, can import multiple use stuff from here to keep things nice an organized
* writing functions to sort out irrelevant blogs
* pushed files aws for testing, but it failed, deal with it tomorrow

##### 7/24 - Sunday
* increased instance size to 30GB to handle the size of the data frame after pulling out of mongo
* started a flow diagram on lucid charts to keep track of stuff
* nmf on posts done and then remerged to post data frame for modeling

##### 7/25 - Monday
* made framework to perform gridsearch for models and then pickle best model
* wrote script to plot confusion matrix for all pickled models
* scripts to pick out latent features topic words written, words put to text file

##### 7/26 - Tuesday
* Code cleaned up and ran on aws

##### 7/27 - Wednesday
* final feature engineering for blogs underway
* blogs now have post classifcation lists
* reduced nmf to 30 for interpretability

##### 7/28 - Thursday
* the topics are now named and in csv and can be merged into posts dataframe
* some eda on full post data set, really not too interesting.
* rerunning the stupid random forest, somehow the dumb thing is 4gigs large

##### 7/19 - Friday
* resume finally to a usable state, could use some polish but not bad


##### Got lazy with updates
* Project done by 7/26
* Results all compiled and presentation made
