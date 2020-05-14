from __future__ import print_function
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DayLocator, DateFormatter
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd
from TweetAnalyzer.config import data_dir
from TweetAnalyzer import SSIXAnalyzer, TweetStore, sentiments

print("Starting program..")

ssix = SSIXAnalyzer(data_dir)

keywords = {}
keywords["leave"] = ["ukip", "no2eu", "britainout", "voteleave", "leaveeu"]
keywords["undecided"] = ["euref", "eureferendum", "takecontrol"]
keywords["stay"] = ["#strongerin", "remain", "ukineu"]


def count_for_set(df, sentiments_df, keys):

    # distinct days
    counts = defaultdict(int)

    for i, idx in enumerate(df.index):
        if i % 5000 == 0:
            print("Processed {} tweets".format(i))

        tweet = df.loc[idx, "text"]
        day = df["date"][idx]
        for key in keys:
            if key in tweet:
                sentiments_df.loc[day] += 1

                df = df.drop(idx)
                break

def printTweetStats(undistributed_tweets, sentiments_per_day):
    n_undistributed = len(undistributed_tweets)
    sentiments_all_time = sentiments_per_day.sum()
    n_distributed = sentiments_all_time.sum()
    print("====  Number of undistributed tweets: {}.".format(n_undistributed))
    print("Number of distributed tweets: {}.".format(n_distributed))
    print(sentiments_all_time)
    print(sentiments_per_day)

tweets = TweetStore(data_dir + "May_16.csv")
df = tweets.getTweets()
idx = sorted(df["date"].unique())
sentiments_per_day = pd.DataFrame(0, index=idx, columns=sentiments)

printTweetStats(df, sentiments_per_day)

# Remove tweets containing keywords mapped to a fixed sentiment
count_for_set(df, sentiments_per_day["leave"], keywords["leave"])
count_for_set(df, sentiments_per_day["undecided"], keywords["undecided"])
count_for_set(df, sentiments_per_day["stay"], keywords["stay"])

printTweetStats(df, sentiments_per_day)

# Sentiment analysis for remaining tweets
threshold_leave = -0.00661286
threshold_stay = 0.00830461
def scoreToSentiment(score):
    if score <= threshold_leave:
        return "leave"
    elif score >= threshold_stay:
        return "stay"
    else:
        return "undecided"
df["score"] = df["text"].apply(ssix.getTweetScore)
df["sentiment"] = df["score"].apply(scoreToSentiment)
#df["sentiment"] = "undecided"
#df["sentiment"][df["score"] <= threshold_leave] = "leave"
#df["sentiment"][df["score"] >= threshold_stay] = "stay"

for day in df["date"].unique():
    day_df = df[df["date"] == day]
    sentiments_per_day["leave"][day] += sum(day_df["sentiment"] == "leave")
    sentiments_per_day["stay"][day] += sum(day_df["sentiment"] == "stay")
    sentiments_per_day["undecided"][day] += sum(day_df["sentiment"] == "undecided")

printTweetStats(df, sentiments_per_day)


loc = MultipleLocator(base=1.0)
xfmt = DateFormatter('%d %b')

fig = plt.figure(figsize=(6,6))
ax = plt.axes()
ax.xaxis.set_major_formatter(xfmt)
ax.xaxis.set_major_locator(loc)
ax.set_title("Tweet count for leave / stay")
w = 0.2

counts_leave = np.array([sentiments_per_day["leave"][day] for day in df["date"]])
counts_stay = np.array([sentiments_per_day["stay"][day] for day in df["date"]])
counts_other = np.array([sentiments_per_day["undecided"][day] for day in df["date"]])
np_days = date2num(df["date"])
ax.bar(np_days, counts_leave, width=w, color="r", label="leave")
ax.bar(np_days+w, counts_stay, width=w, color="b", label="stay")
ax.set_xlabel("Dates")
ax.set_ylabel("Tweet count")
plt.savefig("total_daycount_ls.pdf")

tot = counts_leave + counts_stay + counts_other
tot = np.max(np.vstack((tot, np.ones_like(tot))), axis=0)
counts_leave_normalised = 1.0*counts_leave/tot
counts_other_normalised = 1.0*counts_other/tot
counts_stay_normalised = 1.0*counts_stay/tot

fig = plt.figure(figsize=(6,6))
ax = plt.axes()
ax.xaxis.set_major_formatter(xfmt)
ax.xaxis.set_major_locator(loc)
ax.set_title("Tweet count for leave / other / stay")
w = 0.6
ax.bar(np_days, counts_leave_normalised, width=w, color="r", label="leave")
ax.bar(np_days, counts_stay_normalised, width=w, bottom=counts_leave_normalised, color="b", label="stay")
ax.bar(np_days, counts_other_normalised, width=w, bottom=1-counts_other_normalised, color="g", label="other")
ax.set_xlabel("Dates")
ax.set_ylabel("Tweet count")
plt.savefig("relative_daycount.pdf")