#%%
import sys
import datetime
import pandas as pd
import pandas_ta as ta
import time
import threading
import pytrader as pyt
from app import getData

api_key='' # 請修改此處
secret_key='' # 請修改此處
id_strategy = "109034011_nightshort" # 自行修改

# 讀取歷史資料(台指期+指標資料)
df_5min = pd.read_csv(f"TXF_1T.csv", index_col=0)   # 第一行設為 index (datetime)
df_5min.index = pd.to_datetime(df_5min.index)       # 將 index 調整成 datetime 形式

# 調整歷史資料要用幾分K
df_5min = df_5min.resample('5T', label='right', closed='right').agg(
    {   'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
        '大戶買進' : 'sum',
        '散戶買進' : 'sum',
        '大戶掛單' : 'sum',
        '散戶掛單' : 'mean'
    })
df_5min.dropna(axis=0, inplace=True)   # 將含有 missing value 的 rows 刪掉 

# print()
# print("調整完分K後的完整數據\n")
# print(df_1min)

df_TXF = pd.DataFrame(df_5min.iloc[:,:5])
# print()
# print("調整完分K後的台指期數據\n")
# print(df_TXF)

record = pd.DataFrame(df_5min.iloc[:, -4:])
# record_cumsum = pd.DataFrame([record.iloc[-1]])   # record_cumsum 是為了跨日的夜盤做準備
# print()
# print("調整完分K後的指標數據\n")
# print(record)
# print()
# print("調整完分K後的最後一筆指標數據\n")
# print(record_cumsum)

def change_time():

    global begin_time
    global end_time
    global morning_start
    global morning_end
    global evening_start1
    global evening_end1
    global evening_start2
    global evening_end2

    # 抓4個指標的及時資料做準備
    morning_start = datetime.time(8, 45)
    morning_end = datetime.time(13, 45) 
    evening_start1 = datetime.time(15, 00)
    evening_end1 = datetime.time(23, 59)
    evening_start2 = datetime.time(0, 00)
    evening_end2 = datetime.time(5, 00)

    # 預設為日盤
    begin_time = morning_start
    end_time = morning_end

    # 即時4個指標資料更新
    now = datetime.datetime.now().time()
    now = now.replace(second=0,microsecond=0)
    print(now)
    if (morning_start <= now <= morning_end):
        begin_time = morning_start
        end_time = morning_end
        print("日盤")
    elif(evening_start1 <= now <= evening_end1):
        begin_time = evening_start1
        end_time=evening_end1
        print("夜盤1")
    elif(evening_start2 <= now <= evening_end2):
        begin_time = evening_start2
        end_time = evening_end2
        print("夜盤2")

    # print(begin_time)
    # print(end_time)

def wait_for_n_minute(n):

    global current_minute
    global after_wait_n_minute
    # print("現在時間分鐘")
    # print(current_minute.minute)
    # print()
    # print("等待至")
    # print(after_wait_n_minute)
    # print("更新資料")

    while True:
        if datetime.datetime.now() < after_wait_n_minute:
            print("抓取資料中...\n")
            return True
        else:
            # 下次要更新資料的時間
            current_minute = datetime.datetime.now()
            after_wait_n_minute = current_minute + datetime.timedelta(minutes=n)
            print("下次更新時間")           
            print(after_wait_n_minute)
            return False

def fetch_data(api,n):

    global df_new_TXF
    global df_new_indicator

    print("fetch_data\n")  

    while True:
        if(datetime.datetime.now().time().replace(second=0,microsecond=0)  <= end_time and wait_for_n_minute(n)):    # 確保還在開盤時間 & 在K棒更新前

            # # 更新台指期數據
            # df_new_TXF = pd.DataFrame().from_records(
            #         [x.to_dict() for x in list(trader.tick)])
            # df_new_TXF.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close',
            #                     'volume': 'Volume'}, inplace=True)
            # df_new_TXF = df_new_TXF.set_index('datetime')
            # # df_new_TXF = df_new_TXF[df_new_TXF.index.time >= begin_time]
            # df_new_TXF = df_new_TXF[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
            # # print("要新加入的台指期數據\n")
            # # print(df_new_TXF)
            # # print()

            # # 更新指標數據
            # api.concatData()                               
            # df_new_indicator = pd.DataFrame(api.data)     
            # if(len(df_new_indicator)==0):
            #     print("沒有指標數據")
            # df_new_indicator["datetime"] = pd.to_datetime(df_new_indicator["datetime"])
            # df_new_indicator = df_new_indicator.set_index("datetime")  
            # # print("要新加入的指標數據\n")
            # # print(df_new_indicator)  
            # # print()

            time.sleep(1)

        else:
            # print("要新加入的台指期數據\n")
            # print(df_new_TXF)
            # print()
            # print("要新加入的指標數據\n")
            # print(df_new_indicator)  
            # print()
            # 更新台指期數據
            df_new_TXF = pd.DataFrame().from_records(
                    [x.to_dict() for x in list(trader.tick)])
            df_new_TXF.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close',
                                'volume': 'Volume'}, inplace=True)
            df_new_TXF = df_new_TXF.set_index('datetime')
            # df_new_TXF = df_new_TXF[df_new_TXF.index.time >= begin_time]
            df_new_TXF = df_new_TXF[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
            # print("要新加入的台指期數據\n")
            # print(df_new_TXF)
            # print()

            # 更新指標數據
            api.concatData()                               
            df_new_indicator = pd.DataFrame(api.data)     
            if(len(df_new_indicator)==0):
                print("沒有指標數據")
            df_new_indicator["datetime"] = pd.to_datetime(df_new_indicator["datetime"])
            df_new_indicator = df_new_indicator.set_index("datetime")  
            # print("要新加入的指標數據\n")
            # print(df_new_indicator)  
            # print()
            
            print("結束這階段的抓取資料")
            return
   
def running(api):
    api.main()

def strategy():

    global df_new_TXF
    global df_new_indicator
    global df_TXF
    global record

    time.sleep(1)

    # 調整抓到台指期數據分K
    df_new_TXF = df_new_TXF.resample('5T', label='right', closed='right').agg(
    {   'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    df_new_TXF.dropna(axis=0, inplace=True)
    df_TXF.update(df_new_TXF)
    to_be_added = df_new_TXF.loc[df_new_TXF.index.difference(df_TXF.index)]
    df_TXF = pd.concat([df_TXF, to_be_added])
    print("更新後的台指期資料\n")
    print(df_TXF)

    # 調整抓到指標數據分K
    df_new_indicator = df_new_indicator.resample('5T', label='right', closed='right').agg( 
    {
        '大戶買進' : 'sum',
        '散戶買進' : 'sum',
        '大戶掛單' : 'sum',
        '散戶掛單' : 'mean'
    })

    df_new_indicator["大戶買進"]=df_new_indicator["大戶買進"].cumsum()
    df_new_indicator["散戶買進"]=df_new_indicator["散戶買進"].cumsum()
    df_new_indicator["大戶掛單"]=df_new_indicator["大戶掛單"].cumsum()
    record.update(df_new_indicator)
    to_be_added = df_new_indicator.loc[df_new_indicator.index.difference(record.index)]
    record = pd.concat([record, to_be_added])
    print("更新後的指標數據資料\n")
    print(record)

    time.sleep(1)

    # 開始策略
    print("開始執行策略...")

    self_var6 = [0]
    maxProfit = 0

    self_var15 = [sys.maxsize]

    # this place can add stop or limit order
    profitpct = 1.5  # 多單止盈
    stoppct = 0.9    # 多單止損

    profitpct_short = 0.9  # 空單止盈
    stoppct_short = 0.5    # 空單止損

    maxProfitThres = 0.5
    returnPercent = 16

    if (len(trader.position()) == 0):
        self_position = 'None'
    else:
        self_position = 'Buy' if trader.position()['is_long'] else 'Sell'

    # if self_position == 'Buy':
    #     # self_tp = trader.trades[-1]['entry_price'] * (1+profitpct/100)   # 最後一列的資料，也就是未實現損益的那筆，用其entry price計算止盈
    #     self_sl = max(trader.trades[-1]['entry_price']
    #                 * (1-stoppct/100), self_var6[-1])                  # 計算止損
    #     # if (trader.tick[-1]['close'] > self_tp):
    #     #     trader.sell(size=1)

    #     if (trader.tick[-1]['close'] < self_sl):
    #         trader.sell(size=1)

    if self_position == 'Sell':

        # maxProfit = max(maxProfit, trader.position()['pnl']/200)      

        self_sl = min(trader.trades[-1]['entry_price']
                    * (1+stoppct_short/100), self_var15[-1])
        # self_tp = trader.trades[-1]['entry_price'] * (1-profitpct_short/100)
        # if (trader.tick[-1]['close'] < self_tp):
        #     trader.buy(size=1)
        #     maxProfit = 0

        # elif (maxProfit/trader.trades[-1]['entry_price'] >= maxProfitThres/100):
        #     self_sl = min(
        #         self_sl, trader.trades[-1]['entry_price'] - maxProfit*(1-returnPercent/100))

        if (trader.tick[-1]['close'] > self_sl):
            trader.buy(size=1)
            maxProfit = 0

    def Pivot(numericseries, Len, LeftStrength, RightStrength, Instance, HiLo, oPivotPriceValue, oPivotBar):
            var0 = 0
            var1 = 0
            var2 = 0
            var3 = 0
            var4 = False
            var5 = False

            var3 = 0
            var5 = False
            var1 = RightStrength
            while var1 < Len and var5 == False:
                var0 = numericseries[-var1-1]
                var4 = True
                var2 = var1 + 1
                while var4 == True and var2 - var1 <= LeftStrength:
                    condition1 = (HiLo == 1 and var0 < numericseries[-var2-1]) or (
                        HiLo == -1 and var0 > numericseries[-var2-1])
                    if condition1:
                        var4 = False
                    else:
                        var2 = var2 + 1

                var2 = var1 - 1
                while var4 == True and var1 - var2 <= RightStrength:
                    condition1 = (HiLo == 1 and var0 <= numericseries[-var2-1]) or (
                        HiLo == -1 and var0 >= numericseries[-var2-1])
                    if condition1:
                        var4 = False
                    else:
                        var2 = var2 - 1

                if var4 == True:
                    var3 = var3 + 1

                if var3 == Instance:
                    var5 = True
                else:
                    var1 = var1 + 1

            if var5 == True:
                oPivotPriceValue[0] = var0
                oPivotBar[0] = var1
                return 1
            else:
                oPivotPriceValue[0] = -1
                oPivotBar[0] = -1
                return -1

    def PivotLowVSBar(Instance, PriceValue, LeftStrength, RightStrength, Len):
        return pd.Series((PriceValue).rolling(window=Len+LeftStrength).apply(Pivot, raw=True, args=(Len, LeftStrength, RightStrength, Instance, -1, [0], [0])))

    def CountIfRC(Close, Open, test_len, len):  # Red Candlesticks
        return pd.Series((Close > Open).rolling(window=test_len).sum() < len)

    def Lowest(Close, len):
        return pd.Series(Close.rolling(window=len).min())

    def Highest(Close, len):
        return pd.Series(Close.rolling(window=len).max())

    # CountIf(close < highest(close, hl_len), short_test_len) > short_len;

    def CountIfCH(Close, High, test_len, len):
        return pd.Series((Close < High).rolling(window=test_len).sum() > len)

    # CountIf(close > lowest(close, hl_len), short_test_len) > short_len;
    def CountIfCL(Close, Low, test_len, len):
        return pd.Series((Close > Low).rolling(window=test_len).sum() > len)

    Length = 15
    NumDevsUp = 1
    NumDevsDn = -2
    low_Length = 15
    Strength = 32
    Len = 8
    test_len = 10

    Short_Length = 14
    Short_Length2 = 2
    high_Length = 8
    hl_len = 7
    short_test_len = 14
    short_len = 6
    ratio = 0.2

    self_var0 = ta.linreg(close=df_TXF['Close'], length=Length)
    self_var1 = ta.stdev(close=self_var0, length=Length)
    self_var3 = ta.linreg(
        close=df_TXF['Close'], length=Length, angle=True)
    self_var4 = PivotLowVSBar(
        1, df_TXF['Close'], Strength, Strength, Len=Strength+1)
    self_var4.index = df_TXF.index
    self_var5 = CountIfRC(
        df_TXF['Close'], df_TXF['Open'], test_len, Len)
    self_var5.index = df_TXF.index
    self_var6 = Lowest(df_TXF['Low'], low_Length)
    self_var6.index = df_TXF.index

    self_var7 = ta.linreg(close=df_TXF['Close'], length=Short_Length)
    self_var8 = ta.stdev(close=self_var7, length=Length)
    self_var10 = ta.linreg(
        close=df_TXF['Close'], length=Short_Length2)

    self_var11 = Highest(df_TXF['Close'], hl_len)
    self_var11.index = df_TXF.index
    self_var12 = CountIfCH(
        df_TXF['Close'], self_var11, short_test_len, short_len)
    self_var12.index = df_TXF.index
    self_var13 = Lowest(df_TXF['Close'], hl_len)
    self_var13.index = df_TXF.index
    self_var14 = CountIfCL(
        df_TXF['Close'], self_var13, short_test_len, short_len)
    self_var14.index = df_TXF.index

    self_var15 = Highest(df_TXF['High'], high_Length)
    self_var15.index = df_TXF.index

    var2 = self_var0[-1] + self_var1[-1] * NumDevsUp

    var9 = self_var8[-1] + self_var8[-1] * NumDevsDn

    condition1 = (self_var4[-1] != -1)
    condition2 = (self_var5[-1] == True)

    condition3 = (self_var12[-1] == True)
    condition4 = (self_var14[-1] == True)
    condition5 = df_TXF['High'][-1] - \
        df_TXF['Low'][-1] > (self_var11[-1] - self_var13[-1]) * ratio
    
    ema280 = ta.ema(close=df_TXF['Close'], length=280)

    if (len(trader.position()) == 0):
        self_position = 'None'
    else:
        self_position = 'Buy' if trader.position()[
            'is_long'] else 'Sell'

    if self_position == 'None':

        if (record['大戶買進'][-1] <= -3400) and (record['散戶買進'][-1] <= -2600) and (df_TXF['Volume'][-1] >= 1200):
            if self_position == 'None':
                trader.sell(size=1)
        # elif condition1 and df_TXF['Close'][-1] > df_TXF['Open'][-1]:
        #     if self_position == 'None':
        #         trader.buy(size=1)
        #     else:
        #         trader.buy(size=2)
        #         maxProfit = 0

    # if self_position == 'Buy':

    #     if record['大戶買進'][-1] - record['大戶買進'][-2] <= 330:
    #         trader.sell(size=1)
    #     elif datetime.datetime.now().time() > datetime.time(4, 25) and datetime.datetime.now().time() < datetime.time(4, 40):
    #         trader.sell(size=1)

    # if self_position == 'None':

    #     if (self_var10[-2] < self_var7[-2]) and (self_var10[-1] > self_var7[-1]) and self_var3[-1] < 0 and condition3 and condition4 and condition5:
    #         trader.sell(size=1)
    #         maxProfit = 0

    #     if (df_TXF['Close'][-1] < ema280[-1]) and (df_TXF['大戶買進'][-1] < -520) and (df_TXF['大戶買進'][-1] - df_TXF['大戶買進'][-2] <= -270):
    #         trader.sell(size=1)

    if self_position == 'Sell':
        if(record['大戶買進'][-1] >= 3600) and (record['散戶買進'][-1] >= 4000):
            trader.buy(size=1)
        elif datetime.datetime.now().time() > datetime.time(4, 25) and datetime.datetime.now().time() < datetime.time(4, 40): # 當沖
            trader.buy(size=1)
            maxProfit = 0

        # if (var9 < df_TXF['Close'][-2]) and (var9 > df_TXF['Close'][-1]):
        #     trader.buy(size=1)
        #     maxProfit = 0
        # elif (self_var7[-2] < self_var10[-2]) and (self_var7[-1] > self_var10[-1]):
        #     trader.buy(size=1)
        #     maxProfit = 0

        # if df_TXF['大戶買進'][-1] - df_TXF['大戶買進'][-2] >= 460:
        #     trader.buy(size=1)
        #     maxProfit = 0



logged_in = False
change_time()

# 根據日夜盤改動 
# while (datetime.datetime.now().time().replace(second=0,microsecond=0) < morning_start): 
while (datetime.datetime.now().time().replace(second=0,microsecond=0) < evening_start1):

    global api

    # 先登入等待開盤
    if logged_in:
        print("已登入 等待開盤")
    else:
        trader = pyt.pytrader(strategy=id_strategy, 
                    api_key=api_key, secret_key=secret_key)
        api = getData(apiKey=api_key, secretKey=secret_key, beginTime=begin_time, endTime=end_time)
        logged_in = True
        print("登入")

    time.sleep(1)

# 若現在是開盤時間則登入進場 (調整日夜盤時間)
if  (morning_start <= datetime.datetime.now().time().replace(second=0,microsecond=0) <= morning_end) or \
    (evening_start1 <= datetime.datetime.now().time().replace(second=0,microsecond=0) <= evening_end1) or \
    (evening_start2 <= datetime.datetime.now().time().replace(second=0,microsecond=0) <= evening_end2):

    if logged_in:
        print("已登入")
    else:
        trader = pyt.pytrader(strategy=id_strategy, 
                    api_key=api_key, secret_key=secret_key)
        api = getData(apiKey=api_key, secretKey=secret_key, beginTime=begin_time, endTime=end_time)
        logged_in = True
        print("登入")

    # 定義第一次的更新資料時間
    current_minute = datetime.datetime.now()
    after_wait_n_minute = current_minute + datetime.timedelta(minutes=5)  # n 分鐘後更新資料

    while (morning_start <= datetime.datetime.now().time().replace(second=0,microsecond=0) <= morning_end) or \
          (evening_start1 <= datetime.datetime.now().time().replace(second=0,microsecond=0) <= evening_end1) or \
          (evening_start2 <= datetime.datetime.now().time().replace(second=0,microsecond=0) <= evening_end2):

        # print(api.api.usage()) 
        # print(datetime.datetime.now.time())

        # global api

        change_time()
        api.begin_time = begin_time
        api.end_time = end_time
        
        global df_new_TXF
        global df_new_indicator

        # 進行抓資料
        thread1 = threading.Thread(target=fetch_data, args=(api,5))   # n 分鐘後更新資料
        thread2 = threading.Thread(target=running, args=(api,))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # 開始策略
        strategy()
    
    # 離開開盤時間
    api.logout()
    trader.logout()
    logged_in = False
    time.sleep(1)  

print("等待下次開盤...")
   


# %%
