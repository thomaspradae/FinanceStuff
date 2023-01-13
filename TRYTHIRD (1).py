import pandas as pd 
import numpy as np 
import yfinance as yf 
import datetime as dt 

print("Please use the EXACT excel conventions for your inputs")

#Ask for the users ticker symbol, sector and industry 
ticker = input("Please enter your ticker in the format ('Ticker' US Equity): ")
sector = input("Please enter your stocks sector: ")
industry = input("Please enter your stocks industry: ")
start_date = input("Please enter your start date: ")
end_date = input("Please enter your end date: ")
print()

#Format the date in the right syntax 
start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')

#Load the data by accessing the excel file on the computer 
df = pd.read_excel("~/Desktop/Screener.xlsm", sheet_name = "Screener", usecols = "A:J", header = 9)

#Filter the excel file data by sector and industry 

df = df[(df["GICS Sector"] == sector) & (df["GICS Ind Name"] == industry)]

#Select the data for the stocks peers 
input_stock = df[df["Ticker"] == ticker]
peers = df[df["Ticker"] != ticker]

#Print the users selection
print("Your selection was: ")
print("Ticker: " + ticker + ", Sector: " + sector + ", Industry: " + industry)
print()

#Print the peers ticker symbols 
print("These are " + ticker.replace('US Equity' , '').strip() + " peers: ")

#Delete the US Equity from each peer for printing 
for i, peer in peers.iterrows(): 
    print(peer["Ticker"].replace('US Equity' , '').strip())

#Calculate the returns for the inputed stock 
ticker_data = yf.Ticker(ticker.replace('US Equity' , '').strip()).history(start = start_date, end = end_date)
ticker_returns = ticker_data["Close"].pct_change().dropna()

#Calculate the returns for each of the peers 

results = []

#Iterate through the peers dataframe
for i, peer in peers.iterrows():
    peer_ticker = (peer["Ticker"].replace('US Equity' , '').strip())

    peer_data = yf.Ticker(peer_ticker).history(start = start_date, end = end_date)

    peer_returns = (peer_data["Close"].pct_change().dropna())

    #Align the indices of both dataframes 
    ticker_returns_aligned, peer_returns_aligned = ticker_returns.align(peer_returns, join = 'inner')

    #Calculate the corrlation between the peers and the inputed stock 
    corr = np.corrcoef(ticker_returns_aligned, peer_returns_aligned) [0][1]

    results.append({"ticker": peer_ticker, "correlation": corr})

#Filter the results to only store results with a high correlation 
relatated_peers = [result for result in results if result ["correlation"] > 0.7]

print()

for result in relatated_peers:
    print(f"Ticker: {result['ticker']} - Correlation: {result['correlation']:.2f}")

print()
print("Correlated stocks found!")
print("Calculating stop loss alert...")



#Stop loss alert starts here 
ticker_returns_14 = ticker_returns[-14:]

peer_returns_14 = []
for i, peer in peers.iterrows():
    peer_ticker = peer["Ticker"].replace('US Equity ' , '').strip()
    peer_data = yf.Ticker(peer_ticker).history(start = start_date, end = end_date)
    peer_returns = (peer_data["Close"].pct_change().dropna())
    peer_returns_14.append(peer_returns[-14])
    average_peer_returns_14 = sum(peer_returns_14) / len(peer_returns_14)

    stv_peer_returns_14 = np.std(average_peer_returns_14)

    print(peer_ticker)

    alert_prompted = False
    for i in range(len(ticker_returns_14)):
        if abs(ticker_returns_14[i] - average_peer_returns_14[i]) > 2 * stv_peer_returns_14:
            alert_date = ticker_returns_14.index[i]
            deviation = ticker_returns_14.index[i] - average_peer_returns_14[i]
            print("Alert, on " + str(alert_date) + ", your stocks return = " + str(ticker_returns_14[i]) + " - Peers average = " + str(peer_returns_14[i]))
            alert_prompted = True 
            break 
    if not alert_prompted:
        print("No alert prompted during the time period")

print("Code finished")

    





