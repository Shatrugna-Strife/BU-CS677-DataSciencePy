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

ticker='SPY'
input_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir))
ticker_file = os.path.join(input_dir, ticker + '.csv')

ticker_data = []

try:   
    with open(ticker_file) as f:
        ticker_data = [x.rstrip('\n').split(',') for x in f.readlines()]
        # print(ticker_data)
    
except Exception as e:
    print(e)
    print('failed to read stock data for ticker: ', ticker)
    exit(0)

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

col = {x:ticker_data[0].index(x) for x in ["Year","Weekday","Close"]}

dicPerYear = defaultdict(lambda : defaultdict(lambda:defaultdict(lambda:[]))) #d={'2016':{'monday':{'pos':[R+],'neg':[R-]}}}

for i in range(2,len(ticker_data)):
    r = ((float(ticker_data[i][col["Close"]]) - float(ticker_data[i-1][col["Close"]]))/float(ticker_data[i-1][col["Close"]]))*100
    if r<0:
        dicPerYear[ticker_data[i][col["Year"]]][ticker_data[i][col["Weekday"]]]["neg"].append(r) 
    else:
        dicPerYear[ticker_data[i][col["Year"]]][ticker_data[i][col["Weekday"]]]["pos"].append(r)
# print(d)

for i in dicPerYear.keys():
    for j in dicPerYear[i]:
        y = dicPerYear[i][j]
        y["meanpos"] = len(y["pos"]) and sum(y["pos"])/len(y["pos"]) or 0
        y["meanneg"] = len(y["neg"]) and sum(y["neg"])/len(y["neg"]) or 0
        y["mean"] = (len(y["pos"])+len(y["neg"])) and (sum(y["pos"])+sum(y["neg"]))/(len(y["pos"])+len(y["neg"])) or 0
        y["variationpos"] = len(y["pos"]) and (sum(i*i for i in y["pos"])/ len(y["pos"])) or 0 - y["meanpos"] * y["meanpos"]
        y["variationneg"] = len(y["neg"]) and (sum(i*i for i in y["neg"])/ len(y["neg"])) or 0 - y["meanneg"] * y["meanneg"]
        y["variation"]  = (len(y["pos"])+len(y["neg"])) and (sum(i*i for i in y["neg"]+y["pos"])/(len(y["pos"])+len(y["neg"]))) or 0 - y["mean"] * y["mean"]
# print(dicPerYear)

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
# print(dicAggregate)

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

print(money)

profit = [[profit[i],i] for i in range(len(profit))]
loss = [[loss[i],i] for i in range(len(loss))]

profit.sort(key=lambda x : x[0], reverse=True)
loss.sort(key=lambda x : x[0])

best_ten_days = [profit[i][0] for i in range(10)]

print(best_ten_days)

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


print(money)


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

print(money)

worst_ten_days = worst_ten_days[:6]
best_ten_days = best_ten_days[:6]

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

print(money)