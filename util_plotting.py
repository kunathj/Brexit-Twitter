import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter
from matplotlib.ticker import MultipleLocator

def dailySentimentPlots(daily_sent, save_path="./"):
    def plotTemplate():
        loc = MultipleLocator(base=1.0)
        xfmt = DateFormatter('%d %b')
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(1, 1, 1)
        ax.xaxis.set_major_formatter(xfmt)
        ax.xaxis.set_major_locator(loc)
        ax.set_xlabel("Dates")
        ax.set_ylabel("Tweet count")

        return ax

    num_days = date2num(daily_sent.index)

    ax = plotTemplate()
    w = 0.2
    ax.bar(num_days,   daily_sent["leave"], width=w, color="r", label="leave")
    ax.bar(num_days+w, daily_sent["stay"],  width=w, color="b", label="stay")
    ax.set_title("Tweet count for leave / stay")
    plt.savefig(save_path+"total_daycount_ls.pdf")

    daily_rel = daily_sent.copy()
    daily_rel["total"] = daily_rel.sum(axis=1)
    daily_rel["total"] = daily_rel["total"].replace(0, 1).astype(float)
    daily_rel = daily_rel.div(daily_rel["total"], axis=0)

    ax = plotTemplate()
    w = 0.6
    ax.bar(num_days, daily_rel["leave"],     label="leave", width=w, color="r")
    ax.bar(num_days, daily_rel["stay"],      label="stay",  width=w, color="b",
            bottom=daily_rel["leave"])
    ax.bar(num_days, daily_rel["undecided"], label="other", width=w, color="g",
            bottom=1-daily_rel["undecided"])
    ax.set_title("Tweet count for leave / other / stay")
    plt.savefig(save_path+"relative_daycount.pdf")