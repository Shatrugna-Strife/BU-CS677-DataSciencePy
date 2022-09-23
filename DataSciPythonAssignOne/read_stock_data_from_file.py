# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 14:37:29 2018

@author: epinsky
this scripts reads your ticker file (e.g. MSFT.csv) and
constructs a list of lines
"""
from collections import defaultdict
import os
from re import S
import pandas as pd



def isfloat(num:str)->bool:
    try:
        float(num)
        return True
    except ValueError:
        return False

def ticker_file_read(ticker : str)->list[list[str]]:
    # ticker='SPY'
    input_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir))
    ticker_file = os.path.join(input_dir, ticker + '.csv')

    ticker_data = []

    try:   
        with open(ticker_file) as f:
            ticker_data = [x.rstrip('\n').split(',') for x in f.readlines()]
            # print(ticker_data)
        return ticker_data
    except Exception as e:
        print(e)
        print('failed to read stock data for ticker: ', ticker)
        exit(0)


def generate_table_per_year(ticker_data : list[list[str]], ticker:str) -> None:
    
    col = {x:ticker_data[0].index(x) for x in ["Year","Weekday","Close"]}

    dicPerYear = defaultdict(lambda : defaultdict(lambda:defaultdict(lambda:[]))) #d={'2016':{'monday':{'pos':[R+],'neg':[R-]}}}

    for i in range(2,len(ticker_data)):
        r = ((float(ticker_data[i][col["Close"]]) - float(ticker_data[i-1][col["Close"]]))/float(ticker_data[i-1][col["Close"]]))*100
        if r<0:
            dicPerYear[ticker_data[i][col["Year"]]][ticker_data[i][col["Weekday"]]]["neg"].append(r) 
        else:
            dicPerYear[ticker_data[i][col["Year"]]][ticker_data[i][col["Weekday"]]]["pos"].append(r)

    for i in dicPerYear.keys():
        for j in dicPerYear[i]:
            y = dicPerYear[i][j]
            y["meanpos"] = len(y["pos"]) and sum(y["pos"])/len(y["pos"]) or 0
            y["meanneg"] = len(y["neg"]) and sum(y["neg"])/len(y["neg"]) or 0
            y["mean"] = (len(y["pos"])+len(y["neg"])) and (sum(y["pos"])+sum(y["neg"]))/(len(y["pos"])+len(y["neg"])) or 0
            y["variationpos"] = len(y["pos"]) and (sum(i*i for i in y["pos"])/ len(y["pos"])) or 0 - y["meanpos"] * y["meanpos"]
            y["variationneg"] = len(y["neg"]) and (sum(i*i for i in y["neg"])/ len(y["neg"])) or 0 - y["meanneg"] * y["meanneg"]
            y["variation"]  = (len(y["pos"])+len(y["neg"])) and (sum(i*i for i in y["neg"]+y["pos"])/(len(y["pos"])+len(y["neg"]))) or 0 - y["mean"] * y["mean"]
    

    print("Ticker:",ticker,"\n")
    for x in dicPerYear.keys():
        keys = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        tmp = pd.DataFrame({"µ(R)":[dicPerYear[x][i]["mean"] for i in keys],"σ(R)":[dicPerYear[x][i]["variation"] for i in keys],"|R−|":[len(dicPerYear[x][i]["neg"]) for i in keys], "µ(R−)":[dicPerYear[x][i]["meanneg"] for i in keys], "σ(R−)":[dicPerYear[x][i]["variationneg"] for i in keys], "|R+|":[len(dicPerYear[x][i]["pos"]) for i in keys], "µ(R+)":[dicPerYear[x][i]["meanpos"] for i in keys], "σ(R+)":[dicPerYear[x][i]["variationpos"] for i in keys]})
        tmp.index=keys
        print("\nYear:", x)
        print(tmp)
    
    

def generate_aggregrate_table(ticker_data : list[list[str]], ticker:str) -> None:

    col = {x:ticker_data[0].index(x) for x in ["Year","Weekday","Close"]}

    dicAggregate = defaultdict(lambda:defaultdict(lambda:[])) #d={'monday':{'pos':[R+],'neg':[R-]}}

    for i in range(2,len(ticker_data)):
        r = ((float(ticker_data[i][col["Close"]]) - float(ticker_data[i-1][col["Close"]]))/float(ticker_data[i-1][col["Close"]]))*100
        if r<0:
            dicAggregate[ticker_data[i][col["Weekday"]]]["neg"].append(r) 
        else:
            dicAggregate[ticker_data[i][col["Weekday"]]]["pos"].append(r)

    for i in dicAggregate.keys():
        y = dicAggregate[i]
        y["meanpos"] = len(y["pos"]) and sum(y["pos"])/len(y["pos"]) or 0
        y["meanneg"] = len(y["neg"]) and sum(y["neg"])/len(y["neg"]) or 0
        y["mean"] = (len(y["pos"])+len(y["neg"])) and (sum(y["pos"])+sum(y["neg"]))/(len(y["pos"])+len(y["neg"])) or 0
        y["variationpos"] = len(y["pos"]) and (sum(i*i for i in y["pos"])/ len(y["pos"])) or 0 - y["meanpos"] * y["meanpos"]
        y["variationneg"] = len(y["neg"]) and (sum(i*i for i in y["neg"])/ len(y["neg"])) or 0 - y["meanneg"] * y["meanneg"]
        y["variation"]  = (len(y["pos"])+len(y["neg"])) and (sum(i*i for i in y["neg"]+y["pos"])/(len(y["pos"])+len(y["neg"]))) or 0 - y["mean"] * y["mean"]

    print("\nTicker:",ticker,"Aggregate Result","\n")
    # for x in dicAggregate.keys():
    keys = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    tmp = pd.DataFrame({"µ(R)":[dicAggregate[i]["mean"] for i in keys],"σ(R)":[dicAggregate[i]["variation"] for i in keys],"|R−|":[len(dicAggregate[i]["neg"]) for i in keys], "µ(R−)":[dicAggregate[i]["meanneg"] for i in keys], "σ(R−)":[dicAggregate[i]["variationneg"] for i in keys], "|R+|":[len(dicAggregate[i]["pos"]) for i in keys], "µ(R+)":[dicAggregate[i]["meanpos"] for i in keys], "σ(R+)":[dicAggregate[i]["variationpos"] for i in keys]})
    tmp.index=keys
    # print("\nYear:", x)
    print(tmp)


def oracle_profit_generate(ticker_data : list[list[str]])->list[any]:

    col = {x:ticker_data[0].index(x) for x in ["Year","Weekday","Close"]}

    closingPriceList = [[float(ticker_data[i][col["Close"]]), float(ticker_data[i][col["Close"]]) - (isfloat(ticker_data[i-1][col["Close"]]) and float(ticker_data[i-1][col["Close"]]) or float(ticker_data[i][col["Close"]]))] for i in range(1,len(ticker_data))]

    # print(closingPriceList)

    initial_money = 100
    tmp_money = 0
    money = 100
    tmp = 0
    buy = 0
    stock_quantity = 0
    profit = []
    loss = []
    for i in range(len(closingPriceList)-1):
        if closingPriceList[i+1][1]>=0 and buy ==0:
            buy = closingPriceList[i][0]
            stock_quantity = money/buy
            tmp_money = money
        elif closingPriceList[i+1][1]<0 and buy!=0:
            money = stock_quantity*closingPriceList[i][0]
            buy = 0
            stock_quantity = 0
            # profit = money - tmp_money
            # print(profit)
        if stock_quantity!=0:
            profit.append(stock_quantity*closingPriceList[i+1][1])
            loss.append(0)
        else:
            loss.append((money/closingPriceList[i][0])*closingPriceList[i+1][1])
            profit.append(0)

    if buy!=0:
        money = stock_quantity*closingPriceList[i][0]
        buy = 0
        stock_quantity = 0
    
    profit = [[profit[i],i] for i in range(len(profit))]
    loss = [[loss[i],i] for i in range(len(loss))]

    return [money, profit, loss]


def oracle_profit_generate_best_ten_days_loss(profit, loss, ticker_data : list[list[str]]):

    col = {x:ticker_data[0].index(x) for x in ["Year","Weekday","Close"]}

    closingPriceList = [[float(ticker_data[i][col["Close"]]), float(ticker_data[i][col["Close"]]) - (isfloat(ticker_data[i-1][col["Close"]]) and float(ticker_data[i-1][col["Close"]]) or float(ticker_data[i][col["Close"]]))] for i in range(1,len(ticker_data))]
    
    best_ten_days = [profit[i][1] for i in range(10)]


    initial_money = 100
    tmp_money = 0
    money = 100
    tmp = 0
    buy = 0
    stock_quantity = 0
    for i in range(len(closingPriceList)-1):
        if buy!=0 and best_ten_days.__contains__(i):
            money = stock_quantity*closingPriceList[i][0]
            buy = 0
            stock_quantity = 0
            continue
        if closingPriceList[i+1][1]>=0 and buy ==0:
            buy = closingPriceList[i][0]
            stock_quantity = money/buy
            tmp_money = money
            continue
        elif closingPriceList[i+1][1]<0 and buy!=0:
            money = stock_quantity*closingPriceList[i][0]
            buy = 0
            stock_quantity = 0
            continue

        if buy!=0:
            money = stock_quantity*closingPriceList[i][0]
            buy = 0
            stock_quantity = 0


    return money

def oracle_profit_generate_worst_ten_days_loss(profit, loss, ticker_data : list[list[str]]):

    col = {x:ticker_data[0].index(x) for x in ["Year","Weekday","Close"]}

    closingPriceList = [[float(ticker_data[i][col["Close"]]), float(ticker_data[i][col["Close"]]) - (isfloat(ticker_data[i-1][col["Close"]]) and float(ticker_data[i-1][col["Close"]]) or float(ticker_data[i][col["Close"]]))] for i in range(1,len(ticker_data))]


    worst_ten_days = [loss[i][1] for i in range(10)]

    initial_money = 100
    tmp_money = 0
    money = 100
    tmp = 0
    buy = 0
    stock_quantity = 0
    for i in range(len(closingPriceList)-1):
        if buy==0 and worst_ten_days.__contains__(i):
            buy = closingPriceList[i][0]
            stock_quantity = money/buy
            tmp_money = money
            continue
        if closingPriceList[i+1][1]>=0 and buy ==0:
            buy = closingPriceList[i][0]
            stock_quantity = money/buy
            tmp_money = money
            continue
        elif closingPriceList[i+1][1]<0 and buy!=0:
            money = stock_quantity*closingPriceList[i][0]
            buy = 0
            stock_quantity = 0
            continue

    if buy!=0:
        money = stock_quantity*closingPriceList[i][0]
        buy = 0
        stock_quantity = 0

    return money

def oracle_profit_generate_best_five_worst_five_days_loss(profit, loss, ticker_data : list[list[str]]):

    col = {x:ticker_data[0].index(x) for x in ["Year","Weekday","Close"]}

    closingPriceList = [[float(ticker_data[i][col["Close"]]), float(ticker_data[i][col["Close"]]) - (isfloat(ticker_data[i-1][col["Close"]]) and float(ticker_data[i-1][col["Close"]]) or float(ticker_data[i][col["Close"]]))] for i in range(1,len(ticker_data))]

    worst_ten_days = [loss[i][1] for i in range(10)][:6]
    best_ten_days = [profit[i][1] for i in range(10)][:6]

    initial_money = 100
    tmp_money = 0
    money = 100
    tmp = 0
    buy = 0
    stock_quantity = 0
    for i in range(len(closingPriceList)-1):
        if buy==0 and worst_ten_days.__contains__(i):
            buy = closingPriceList[i][0]
            stock_quantity = money/buy
            tmp_money = money
            continue
        if buy!=0 and best_ten_days.__contains__(i):
            money = stock_quantity*closingPriceList[i][0]
            buy = 0
            stock_quantity = 0
            continue
        if closingPriceList[i+1][1]>=0 and buy ==0:
            buy = closingPriceList[i][0]
            stock_quantity = money/buy
            tmp_money = money
            continue
        elif closingPriceList[i+1][1]<0 and buy!=0:
            money = stock_quantity*closingPriceList[i][0]
            buy = 0
            stock_quantity = 0
            continue

    if buy!=0:
        money = stock_quantity*closingPriceList[i][0]
        buy = 0
        stock_quantity = 0

    return money

def buy_and_hold(ticker_data : list[list[str]])->float:

    col = {x:ticker_data[0].index(x) for x in ["Year","Weekday","Close"]}

    stockBuy = float(100)/float(ticker_data[1][col["Close"]])

    return stockBuy*float(ticker_data[len(ticker_data)-1][col["Close"]])


def main():
    generate_table_per_year(ticker_file_read("SPY"), "SPY")
    # generate_table_per_year(ticker_file_read("KO"), "KO")
    generate_aggregrate_table(ticker_file_read("SPY"), "SPY")
    generate_aggregrate_table(ticker_file_read("KO"), "KO")
    [moneyProfitSPY,profitSPY,lossSPY] = oracle_profit_generate(ticker_file_read("SPY"))
    [moneyProfitKO,profitKO,lossKO] = oracle_profit_generate(ticker_file_read("KO"))

    profitSPY.sort(key=lambda x : x[0], reverse=True)
    lossSPY.sort(key=lambda x : x[0])

    profitKO.sort(key=lambda x : x[0], reverse=True)
    lossKO.sort(key=lambda x : x[0])
    print("")
    print("SPY Stock Last trading day remaining amount:", moneyProfitSPY)
    print("KO Stock Last trading day remaining amount:", moneyProfitKO)
    print("")
    print("SPY Stock buy and hold strategy remaining amount:", buy_and_hold(ticker_file_read("SPY")))
    print("KO Stock buy and hold strategy remaining amount:", buy_and_hold(ticker_file_read("KO")))
    print("")
    print("SPY Stock best ten days loss remaining amount:", oracle_profit_generate_best_ten_days_loss(profitSPY,lossSPY,ticker_file_read("SPY")))
    print("KO Stock best ten days loss remaining amount:", oracle_profit_generate_best_ten_days_loss(profitKO,lossKO,ticker_file_read("KO")))
    print("")
    print("SPY Stock worst ten days loss remaining amount:", oracle_profit_generate_worst_ten_days_loss(profitSPY,lossSPY,ticker_file_read("SPY")))
    print("KO Stock worst ten days loss remaining amount:", oracle_profit_generate_worst_ten_days_loss(profitKO,lossKO,ticker_file_read("KO")))
    print("")
    print("SPY Stock best five days and worst five days loss remaining amount:", oracle_profit_generate_best_five_worst_five_days_loss(profitSPY,lossSPY,ticker_file_read("SPY")))
    print("KO Stock best five days and worst five days loss remaining amount:", oracle_profit_generate_best_five_worst_five_days_loss(profitKO,lossKO,ticker_file_read("KO")))


main()