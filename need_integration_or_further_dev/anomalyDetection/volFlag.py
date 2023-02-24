# import vectorbtpro as vbt
import pandas as pd
import numpy as np
import vectorbtpro as vbt


def volConv(input, tick):
  volRatio = []
  avgVolRatio = []

  for input in tick:
    count = tick  # tick should be array of vals
    nShares = input
    nTrades = sum(count)
    calcRatio = nTrades / nShares
    volRatio.push(calcRatio)

  avgVolRatio = np.average(volRatio)


def vol_anomaly(volRatio, Optimalfilter, time):
  """
  Function should just accumulate the important big trades in an array
  i.e trades larger than 0.5 volume ratio is arbitary it can be 0-1.0
  """
  flagTrade = []
  if volRatio > 0.02:
    flagTrade = flagTrade.push(volRatio)  # FLAG TO ACCUMULATE"
  else:
    print("no interesting trades")
  

def main():
  """
  fetch the ticker of interest, track the real-time quotes or ticks and follow up with statistical analysis
    1. missing links to nautilus trader
    2. adaptive optimal filter may be a statistical regression problem
    3. correlation of large trades with price movement 
    4. automatic trading -> take from the binance bot ruben has generated.
  """
  # testData = vbt.NDLData.fetch("NSE/OIL")  # double check w/ docs
  testData = pd.read_csv("btcusdt_1m.csv")
  print(testData.columns)
  print(testData.head())
  

  filter = "Some value greater than some threshold" ">1million"  # -> maybe this also into regression model/backtest -> Vectorbt label to Autogluon
  # two sweeps 1. just analyze the data (skew, kurtosis, std dev) 2. after training phase, now lets go live (make it auto pulls data)

  time = " Number of years "

  # -> call the function to check volAnomaly and store in some data/file set
  # -> store this volAnomaly data and use as the input to the ML model
  # pretty dashboard -> top 5 biggest trades ever recorded. top 5 biggest weekly trade. then chart volume anomaly per day and vol vs outstanding ratio per day


if __name__ == '__main__':
  main()
