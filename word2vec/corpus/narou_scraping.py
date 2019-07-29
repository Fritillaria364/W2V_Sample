import os
import csv
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

def get_BS_obj(url):
    html = urlopen(url)
    return BeautifulSoup(html, "html.parser")

def get_main_text(bs_obj):
    text_htmls = bs_obj.findAll("div",{"id":"novel_honbun"})[0].findAll("p")
    text = "".join([ t.get_text() for t in text_htmls ])
    return text

def save_csv(stories, title):
    directory_name = "narou"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    csv_name = os.path.join(directory_name,"{}.csv".format(title))

    col_name = ["ID", "Subtitle", "Text"]
    with open(csv_name, "w") as output_csv:
        csv_writer = csv.writer(output_csv)
        csv_writer.writerow(col_name)

        for story in stories:
            row_items = [story["ID"], story["Title"], story["Text"]]
            csv_writer.writerow(row_items)
    print(".csv saved")

def main():
    rank_url = "https://yomou.syosetu.com/rank/genrelist/type/quarter_302/"
    rank_bs = get_BS_obj(rank_url)
    novels = rank_bs.findAll("div",{"class":"ranking_list"})
    novel_ranking = []

    for i in range(len(novels)):
        novel_ranking.append({
            "No": i+1,
            "novel_title": novels[i].find("a").get_text(),
            "novel_url": novels[i].find("a").attrs["href"],
            "novel_point": novels[i].find("span",{"class":"point"}).get_text()
        })

    url_list = [ novel["novel_url"] for novel in novel_ranking ]

    for url in url_list:
        stories = []
        bs = get_BS_obj(url)

        story_list = [ "https://ncode.syosetu.com" + a_bs_obj.find("a").attrs["href"] \
                      for a_bs_obj in bs.findAll("dl", {"class": "novel_sublist2"}) ]
        data_list = bs.findAll("dt", {"class":"long_update"})
        novel_title = bs.find("p", {"class":"novel_title"}).get_text()

        print("Now Processing")
        for j in range(len(story_list)):
            sub_url = story_list[j]
            print("- ",sub_url)
            sub_bs = get_BS_obj(sub_url)

            stories.append({
                "ID": j+1,
                "Title": sub_bs.find("p", {"class": "novel_subtitle"}).get_text(),
                "Text": get_main_text(sub_bs)
            })

        save_csv(stories, novel_title)

if __name__ == "__main__":
    main()