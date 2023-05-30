import time
import requests
import pandas as pd
import numpy as np
from binance.client import Client
import mysql.connector


class DB_Helper:

    def db_connect(self):
        
        self.mydb = mysql.connector.connect(
          host="$SQL_SERVER_ADDRESS",
          user="$USER",
          password="$PASS",
          database="ORDERS"
        )
        self.mycursor = self.mydb.cursor()
        
        
    def select(self):
        self.db_connect()
        self.mycursor.execute("SELECT * FROM WhaleAlert")
        self.myresult = self.mycursor.fetchall()
        self.mycursor.close()
        self.mydb.close()            
        return self.myresult   
        
        
dbh=DB_Helper()
client = Client("$PUBLIC_KEY", "$SECRET_KEY")
TOKEN = "$TG_TOKEN"
latest_whales=[]
start = time.time()

last_id={}

while(True):
    #s=time.time()
    
    time.sleep(3)
    
    last_sy=None

    for x in dbh.select():  
                   

                try:

                        if last_sy != x[3] : 
                            #print(last_id)
                            if x[3] in last_id:
                                #print("aaaaa")
                                trades = client.futures_aggregate_trades(symbol=x[3],limit=1000, fromId=last_id[x[3]])
                            else:
                                trades = client.futures_aggregate_trades(symbol=x[3],limit=1000)
                            trades=pd.DataFrame(trades)






                            trades["q"]=trades["q"].astype(float)
                            buy_trades = trades[trades.m == 0]
                            sell_trades = trades[trades.m == 1]
                            n=int(x[5])



                            buy_compressed = pd.DataFrame([buy_trades.rolling(n)["q"].sum().iloc[n-1::n],buy_trades.rolling(n)["p"].mean().iloc[n-1::n]]).T
                            buy_compressed["m"]=False
                            #display(buy_compressed)

                            sell_compressed = pd.DataFrame([sell_trades.rolling(n)["q"].sum().iloc[n-1::n],sell_trades.rolling(n)["p"].mean().iloc[n-1::n]]).T
                            sell_compressed["m"]=True
                            #display(sell_compressed)

                            trades2 = pd.concat([buy_compressed, sell_compressed], ignore_index=True)
                        #
                            #print(trades)
                        last_sy=x[3]


                        e_trade=None
                        if x[2] == "buy":
                            e_trade=trades2[(trades2.q >=x[4]) & (trades2["m"] == False )]
                        else:
                            e_trade= trades2[(trades2.q >=x[4]) & (trades2["m"] == True )]


                        if(x[5]>len(buy_trades) or x[5]>len(sell_trades)):
                            continue

                        last_id[x[3]]=trades.tail(1).values[0][0]

                        for i in e_trade.values:
                                        currency_string = "${:,.2f}".format(float(i[0])*float(i[1]))
                                        em=""
                                        if(x[2] == "buy"):
                                            em="🟢"
                                        else:
                                            em="🔴"
                                        message="{} 🐳 {} paritesinde {} fiyatından {}( {} USDT ) {} işlemi yapıldı 🐳".format(em,x[3], round(i[1],2),round(i[0],2), currency_string ,x[2].upper())
                                        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=$CHAT_ID&text="+message
                                        
                                        re=requests.get(url).json()
                except:
                        print("binance bağlantısı sağlanamadı")                        
        

    #print(time.time()-s)