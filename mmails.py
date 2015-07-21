#!/usr/bin/env python3
"""
    analyze mbox

    author: Steve Göring
    contact: stg7@gmx.de
    2015
"""
"""
    This file is part of mmails.

    mmails is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    mmails is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with mmails.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import argparse
import mailbox
import email.utils
import datetime
import time
import shelve

def histo(data, caption=""):
    """
    build up a small tikz bar chart
    :data dictionary of x-> y values
    :caption bar chart caption
    """
    maxK = max(data.keys())
    maxY = max(data.values())
    xmin = min(data.keys())
    xmax = max(data.keys())

    width = 14
    bar_width = round(0.5 * width / len(data.keys()), 2)

    res = r"""
\documentclass{article}
\usepackage[x11names, rg]{xcolor}
\usepackage[utf8]{inputenc}
\usepackage{tikz}
\usetikzlibrary{snakes,arrows,shapes}
\usepackage{amsmath}
\usepackage{pgfplots}

\usepackage[active,tightpage]{preview}
\PreviewEnvironment{tikzpicture}
\setlength\PreviewBorder{0pt}%

\pgfplotsset{compat=newest}
\begin{document}
\pgfplotsset{small}

\begin{tikzpicture}
  \centering
  \begin{axis}[
    ymax=""" + str(round(110 * maxY)) + r""",
    ymin=0,
    ylabel={\% freq },
    xlabel={""" + caption + r"""},
    bar width=""" + str(bar_width) + r"""cm,
    height=8cm,
    width=""" + str(width) + r"""cm,
    xmin=""" + str(xmin - 0.75) + r""",
    xmax=""" + str(xmax + 1) + r""",
    xtick=data
    ]

    \addplot [smooth,gray, fill=gray!10] coordinates {"""

    for k in sorted(data.keys()):
        v = data[k]
        res += "(" + str(k) + ", " + str(100 * v) + ") " + "\n"


    res += "(" + str(maxK) + ", " + str(100 * 0) + ") " + "\n"

    res += r"""} \closedcycle;
    \addplot [ybar,fill=orange!75,draw=orange!50!black] coordinates {""" + "\n"

    for k in sorted(data.keys()):
        v = data[k]
        res += "(" + str(k) + ", " + str(100 * v) + ") "

    res += r"""};

  \end{axis}
\end{tikzpicture}

\end{document}""" + "\n"
    return res

def main(params):
    # argument parsing
    parser = argparse.ArgumentParser(description='analyze mbox file', epilog="stg7 2015")
    parser.add_argument('mbox',type=str, help='mbox input file')
    parser.add_argument('--suffix',default="", type=str, help='optinal output suffix')
    argsdict = vars(parser.parse_args())

    mbox = mailbox.mbox(argsdict["mbox"])

    _cache = shelve.open("_cache")

    send_time_histo = {}
    week_day_histo = {}

    if not "send_time_histo" in _cache or not "week_day_histo" in _cache or _cache["file"] != argsdict["mbox"]:
        print("analyze messages")
        _cache["file"] = argsdict["mbox"]
        for message in mbox:
            print(".", end="")
            sys.stdout.flush()
            try:
                mtime = time.strptime(message['date'], "%a, %d %b %Y %X %z")
            except Exception as e:
                date = " ".join(message['date'].split(" ")[0:5])
                mtime = time.strptime(date, "%a, %d %b %Y %X")
            hour = mtime.tm_hour
            wday = mtime.tm_wday

            send_time_histo[hour] = send_time_histo.get(mtime.tm_hour, 0) + 1
            week_day_histo[wday] = week_day_histo.get(wday, 0) + 1
            _cache["send_time_histo"] = send_time_histo
            _cache["week_day_histo"] = week_day_histo

    else:
        print("results are cached")
        send_time_histo = _cache["send_time_histo"]
        week_day_histo = _cache["week_day_histo"]

    print()
    all_msg = sum([send_time_histo[x] for x in send_time_histo])
    print("messages: {}".format(all_msg))

    print("per hour:")
    for h in sorted(send_time_histo.keys()):
        print("{}: {}".format(h, send_time_histo[h]))

    week_day_name = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]
    print("per weekday")
    for wd in sorted(week_day_histo.keys()):
        print("{}: {}".format(week_day_name[wd], week_day_histo[wd]))

    print("{}: {}".format("not working time", sum([send_time_histo.get(x, 0) for x in [18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7]])))

    _cache.close()

    data = {x: 0 for x in range(0, 25)}
    all_msg = sum([send_time_histo[x] for x in send_time_histo])
    data = {x: send_time_histo[x] / all_msg for x in send_time_histo}

    f = open("emails_per_hour_" + argsdict["suffix"] + ".tex", "w")
    f.write(histo(data, "emails sent per hour: " + argsdict["suffix"]))
    f.close()

    data = {x: 0 for x in range(0, 6)}
    all_msg = sum([week_day_histo[x] for x in week_day_histo])
    data = {x: week_day_histo[x] / all_msg for x in week_day_histo}

    f = open("emails_per_weekday_" + argsdict["suffix"] + ".tex", "w")
    f.write(histo(data, "emails send per weekday: " + argsdict["suffix"]))
    f.close()

if __name__ == "__main__":
    main(sys.argv[1:])