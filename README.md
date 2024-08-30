# LeagueHistorian

Thank you for checking out this repo.

I have been a long time fan of fantasy football and have played in various types of league on different platforms (nfl.com, espn, sleeper, etc). 

My favorite platform is Sleeper because it provides very insightful and fascinating statistics about your league and matchup. There is one league I have over 10 years of history in, but I am disappointed that the platform that league is on does not offer the same detailed level of statistics as the platforms I am in newer leagues on.

To solve this problem, I have started this project in which I intend to create an application that both extracts the data from my older league and makes it easy and conveneint to construct customized statistics and records for the league. Eventually, I would also like to find a way to systematically convert this data into prompts for chatGPT to get entertaining recaps of any given weeks matchup (what records were broken that week, how have the teams with matchups played against each other historically, how did trades that have occured this year affect the outcome of the matchup, etc)

I have two main goals for this project in progress:

1. To design modules that efficiently extract the data from a user's nfl.com fantasy football league and store it in an orderly format, both historical data and data from live matchups in progress.
   
2. To use either prompt-engineering or ChatGPT4s API to submit summaries of the data scraped from a league to generate entertaining recaps of specified weeks that are unique to the history of the league.

Curently, Goal 1 has almost been met, with scrapers created that extract large amount of data from the league and modules that transform the data to a more orderly format. What remains to be done for Goal 1 is loading of the etxracted/transformed data into an SQLite database for easy and efficient retrieval.

Goal 2 is still in the brainstorming phase, and I am still deciding exactly how I want to achieve it.

If you have any suggestions, or would like to contribute to this project, please feel free to contact me at the email listed in my profile!


