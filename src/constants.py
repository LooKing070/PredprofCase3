import csv

RESOLUTION = {"832": (832, 896), "416": (416, 448)}


def account_pull():
    with open(f"../data/login.csv", "r", encoding="utf-8") as account:
        my_account = list(csv.reader(account, delimiter=";", quotechar="\n"))
    return my_account


myAccount = account_pull()
