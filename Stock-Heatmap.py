import bs4 as bs
import datetime as dt 
import matplotlib.pyplot as plt
from matplotlib import style
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
import requests
import seaborn as sns

style.use('bmh')
start = dt.datetime(2019, 1, 1)
end = dt.datetime.now()
font = {'family': 'monospace','color': 'tomato'}

def Save_SP500_Tickers():
    resp = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = bs.BeautifulSoup(resp.text,"lxml")
    table = soup.find('table',{'id':'constituents'})
    tickers = []

    for row in table.findAll('tr')[1:]:
        ticker = row.find_all('td') [0].text.replace('\n','')
        tickers.append(ticker)

    with open("sp500tickers.pick","wb") as f: 
        pickle.dump(tickers, f)

    print(tickers)
    return tickers

def Get_Data_From_Yahoo(reload_sp500=False):
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open("sp500tickers.pick", "rb") as f:
            tickers = pickle.load(f)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    for ticker in tickers:
        print(ticker)
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)): 
            df = web.DataReader(ticker.replace('.','-'), 'yahoo', start, end)
            df.reset_index(inplace=True)
            df.set_index("Date", inplace=True)
            df.to_csv('stock_dfs/{}.csv'.format(ticker))
        else:
            print('Already have {}'.format(ticker))

def Compile_Data():
    with open ("sp500tickers.pick","rb") as f:
        tickers = pickle.load(f)
    
    main_df = pd.DataFrame()

    for count, ticker in enumerate(tickers):  
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        df.set_index('Date',inplace=True)

        df.rename(columns = {'Adj Close': ticker}, inplace=True)
        df.drop(['Open','High','Low','Close','Volume'], 1, inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how= 'outer') 

        print(count)

    print(main_df.tail())
    main_df.to_csv('sp500_joined_closes.csv')

def Visualize_Data():
    df=pd.read_csv('sp500_joined_closes.csv')
    df_corr = df.corr()
    
    sns.heatmap(df_corr,cmap='RdYlGn',xticklabels=True,yticklabels=True)
    plt.suptitle('S&P 500 Correlation', fontdict=font,fontsize=24)
    plt.show()
