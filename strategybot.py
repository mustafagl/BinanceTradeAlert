#get data
import pandas as pd
import json
import numpy as np
import datetime as dt
from binance.client import Client
import pandas_ta as ta
import time
import requests
import pandas as pd
import json
import numpy as np
import datetime as dt
from binance.client import Client
import pandas_ta as ta
import mysql.connector
import time

client = Client("$PUBLIC_KEY", "$SECRET_KEY")

TOKEN = "$TG_TOKEN"

class DB_Helper:

    def db_connect(self):
        
        self.mydb = mysql.connector.connect(
          host="$SQL_SERVER_ADDRESS",
          user="$USER",
          password="$PASS",
          database="ORDERS"
        )
        self.mycursor = self.mydb.cursor()

        
    def insert(self,open_time,entry_price):
        self.db_connect()        
        sql = "INSERT INTO open_orders (open_time, entry_price) VALUES (%s, %s)"
        val = (open_time, entry_price)
        self.mycursor.execute(sql,val)
        self.mydb.commit()
        self.mycursor.close()        
        self.mydb.close()
        
    
    def insert2_closed(self,u_id,open_time,close_time,entry_price,profit):
        self.db_connect()        
        sql = "INSERT INTO closed_orders (ID ,open_time, close_time, entry_price, profit) VALUES (%s ,%s, %s ,%s, %s)"
        val = (u_id,open_time,close_time, entry_price, profit)
        self.mycursor.execute(sql,val)
        self.mydb.commit()
        self.mycursor.close()        
        self.mydb.close()

    def update_perc_alert(self,time,u_id):
        self.db_connect()        
        sql = "UPDATE PercAlert SET last_trig_time=%s WHERE id = %s"
        val = (time,u_id)
        self.mycursor.execute(sql,val)
        self.mydb.commit()
        self.mycursor.close()        
        self.mydb.close()
        
    def select(self):
        self.db_connect()
        self.mycursor.execute("SELECT * FROM open_orders")
        self.myresult = self.mycursor.fetchall()
        self.mycursor.close()
        self.mydb.close()        
        
        return self.myresult   
    
    def select_alerts(self):
        self.db_connect()
        self.mycursor.execute("SELECT * FROM Alerts")
        self.myresult = self.mycursor.fetchall()
        self.mycursor.close()
        self.mydb.close()        
        
        return self.myresult  
    

    def select_perc_alerts(self):
        self.db_connect()
        self.mycursor.execute("SELECT * FROM PercAlert")
        self.myresult = self.mycursor.fetchall()
        self.mycursor.close()
        self.mydb.close()        
        
        return self.myresult   



    def select_settings(self):
        self.db_connect()
        self.mycursor.execute("SELECT * FROM Bot_settings")
        self.myresult = self.mycursor.fetchall()
        self.mycursor.close()
        self.mydb.close()        
        
        return self.myresult  



    def delete(self,u_id):
        self.db_connect()        
        sql = "DELETE FROM open_orders WHERE ID = '{}'".format(u_id)
        self.mycursor.execute(sql)
        self.mydb.commit()
        self.mycursor.close()        
        self.mydb.close()
        
    def delete_alert(self,u_id):
        self.db_connect()        
        sql = "DELETE FROM Alerts WHERE Alertid = '{}'".format(u_id)
        self.mycursor.execute(sql)
        self.mydb.commit()
        self.mycursor.close()        
        self.mydb.close()        
        
        
    def last_id(self):
        self.db_connect()        
        sql = "SELECT * FROM open_orders ORDER BY ID DESC LIMIT 1"
        self.mycursor.execute(sql)
        self.myresult = self.mycursor.fetchall()
        self.mycursor.close()        
        self.mydb.close()
        
        return self.myresult         
        
dbh=DB_Helper()

class PercAlert:
    
    def new_alert(self,u_id,c_time,symbol,perc,direction,lasttime):
        self.id=u_id
        self.creation_time=c_time
        self.symbol=symbol
        self.perc=perc
        self.direction=direction
        self.lasttime=lasttime
        
    def check_alert(self):
        try:
            klines = client.futures_klines(symbol=self.symbol, interval=Client.KLINE_INTERVAL_5MINUTE,limit=25)   
            columns=["open time","Open price","High price","Low price","Close price","Volume","Kline close time","Quote asset volume","Number of trades","Taker buy base asset volume","Taker buy quote asset volume","Unused field."]
            df = pd.DataFrame(klines,columns=columns)        

            current=df["Close price"].astype(float).tail(1).values[0]
            
            
            if self.lasttime!=None:
                last = dt.datetime.strptime(self.lasttime, "%d/%m/%Y %H:%M:%S")
                now  = dt.datetime.now()                        
                duration = now - last                         
                global duration_in_s 
                duration_in_s = duration.total_seconds()
            
            
            if self.lasttime==None or duration_in_s >= 7200:
                if (self.direction=="increase"):
                    min_val = df["Close price"].astype(float).min()
                    if ( (current - min_val) / min_val *100 >= self.perc ):
                        dbh.update_perc_alert(dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),self.id)
                        
                        message="ID: "+ str(self.id) + " ⚠️  {} paritesi %{} yükseldi ⚠️".format(self.symbol,self.perc)
                        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=$CHAT_ID&text="+message
                        re=requests.get(url).json()     
                        
                elif (self.direction=="decrease"):
                    max_val = df["Close price"].astype(float).max()
                    if ( (max_val - current) / current *100 >= self.perc ):
                        dbh.update_perc_alert(dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),self.id)
                        message="ID: "+ str(self.id) + " ⚠️  {} paritesi %{} düştü ⚠️".format(self.symbol,self.perc)
                        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=$CHAT_ID&text="+message
                        re=requests.get(url).json()     

        except:
                self.check_alert()         
                    
class Alert:
    
    def new_alert(self,u_id,c_time,direction,trig_price):
        self.id=u_id
        self.creation_time=c_time
        self.direction=direction
        self.trig_price=trig_price
        
    def check_alert(self,current_price):
        if(self.direction=="greater"):
            if(self.trig_price <= current_price):  
                self.send_alert()
                
        if(self.direction=="lower"):
            if(self.trig_price >= current_price):  
                self.send_alert()                
                
    def send_alert(self):
        if(self.direction=="greater"):
            dbh.delete_alert(self.id)
            text="🔔Alert: Fiyat {} değerinin {} 🔔".format(self.trig_price,"üzerinde")
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=-807313366&text="+text
            re=requests.get(url).json()

        if(self.direction=="lower"):
            dbh.delete_alert(self.id)
            text="🔔Alert: Fiyat {} değerinin {} 🔔".format(self.trig_price,"altında")
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=-807313366&text="+text
            re=requests.get(url).json()


class Order:
    def new_order(self, entry_price,open_time, name, stop_perc, tp_perc):
        self.open_time=open_time
        self.entry_price = entry_price
        self.status = "Open"
        self.stop_perc=stop_perc
        self.parite_name = name
        self.stop_loss_price = entry_price * (1 + 0.01 * stop_perc)
        self.take_profit_price = entry_price * (1 - 0.01 * tp_perc)
        self.t_stop_step=0
        
    
    def close(self):
        self.status = "Closed"

    
    def check_stop(self,current_price):

        A=dbh.select_settings()[0]


        if self.t_stop_step == 0:
            if  (self.entry_price + (self.entry_price * A[0] * 0.01)) < current_price:
                self.close()
                message="ID: "+ str(self.id) + " 🔴 Exit Sinyal 🔴"
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=$CHAT_ID&text="+message
                re=requests.get(url).json()
            elif  (self.entry_price - (self.entry_price * A[1] * 0.01)) > current_price:
                self.t_stop_step+=1

        if self.t_stop_step == 1:
            if  (self.entry_price - (self.entry_price * A[2] * 0.01)) < current_price:
                message="ID: "+ str(self.id) + " 🟢 Exit Sinyal 🟢"
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=$CHAT_ID&text="+message
                re=requests.get(url).json()            
                self.close()                 

            elif  (self.entry_price - (self.entry_price * A[3] * 0.01)) > current_price:
                self.t_stop_step+=1

        if self.t_stop_step == 2:
            if  (self.entry_price - (self.entry_price * A[4] * 0.01)) < current_price:

                message="ID: "+ str(self.id) + " 🟢🟢 Exit Sinyal 🟢🟢"
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=$CHAT_ID&text="+message
                re=requests.get(url).json()            
                self.close() 

            elif  (self.entry_price - (self.entry_price * A[5] * 0.01)) > current_price:
                self.t_stop_step+=1

        if self.t_stop_step == 3:
            if  (self.entry_price - (self.entry_price * A[6] * 0.01)) < current_price:

                message="ID: "+ str(self.id) + " 🟢🟢🟢 Exit Sinyal 🟢🟢🟢"
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=$CHAT_ID&text="+message
                re=requests.get(url).json()            
                self.close() 

            elif  (self.entry_price - (self.entry_price * A[7] * 0.01)) > current_price:
                self.t_stop_step+=1

        if self.t_stop_step == 4:
            if  (self.entry_price - (self.entry_price * A[8] * 0.01)) < current_price:

                message="ID: "+ str(self.id) + " 🟢🟢🟢🟢 Exit Sinyal 🟢🟢🟢🟢"
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=$CHAT_ID&text="+message
                re=requests.get(url).json()            
                self.close() 

            elif  (self.entry_price - (self.entry_price * A[9] * 0.01)) > current_price:
                self.t_stop_step+=1                                

       
    
    def get_profit(self, current_price):
        return -((current_price - self.entry_price) / self.entry_price) * 100
    
    def set_id(self,u_id):
        self.id=u_id
        
class StrategyHelper:
    def __init__(self,df):
        self.df=df
        
    def getBB(self,source):
        self.BBANDS = ta.bbands(source.astype(float), length=19,std=1.9)
        
        return self.BBANDS
    
    def getRSI(self):
        self.RSI = pd.DataFrame(ta.rsi(self.df["Close price"].astype(float), length=12))
        self.BB_RSI=self.getBB(source=self.RSI["RSI_12"])
        return self.BB_RSI
        
    def getRSI_BB(self):
        RSI_BB = ta.bbands(self.RSI["RSI_12"].astype(float), length=19,std=1.9)
        return RSI_BB
    def getIFTSTOCH(self):
        lowest_low = df["Low price"].astype(float).rolling(21).min()
        highest_high = df["High price"].astype(float).rolling(21).max()
        stoch = 100*(df["Close price"].astype(float) - lowest_low) / (highest_high-lowest_low)
        v1=0.1*(stoch-50)
        v2=ta.wma(v1, 9)
        v2=pd.DataFrame(v2)
        self.INV=(np.exp(2*v2)-1)/(np.exp(2*v2)+1) 
        return self.INV
    def RSIcondition(self):
        self.RSI.loc[(self.RSI['RSI_12'] >= 60.0) | (self.BB_RSI["BBU_19_1.9"]<self.RSI['RSI_12']),"RSI_Condition"]=True
        self.RSI["RSI_Condition"]=self.RSI["RSI_Condition"].fillna(False)
        self.RSI["con"] = self.RSI['RSI_Condition'] | self.RSI['RSI_Condition'].shift(1) | self.RSI['RSI_Condition'].shift(2)
        return self.RSI
    def BB_condition(self):
        self.BBANDS.loc[(self.df["Close price"].astype(float) >= self.BBANDS["BBU_19_1.9"]),"BB_Condition" ]=True
        self.BBANDS["BB_Condition"]=self.BBANDS["BB_Condition"].fillna(False)        
        self.BBANDS["con"] = self.BBANDS['BB_Condition'] | self.BBANDS['BB_Condition'].shift(1) | self.BBANDS['BB_Condition'].shift(2)
        
        return self.BBANDS
    
    def IFTSTOCH_condition(self):
        self.INV.loc[(self.INV["WMA_9"].astype(float) >= 0.8),"INV_Condition" ]=True
        self.INV["INV_Condition"]=self.INV["INV_Condition"].fillna(False)
        self.INV["con"] = self.INV['INV_Condition'] | self.INV['INV_Condition'].shift(1) | self.INV['INV_Condition'].shift(2)
        
        return self.INV
    
    def patienced(self,data):
        
        data.loc[(data.astype(float) == 1) | (data.shift(1).astype(float) == 1) | (data.shift(2).astype(float) == 1),"INV_Condition" ]=1
        return self.INV
    
    def all_condition(self):
        self.df.loc[(self.RSI["con"]==1) & (self.BBANDS["con"]==1) & (self.INV["con"]==1) & (self.df["Close price"].astype(float) <= self.df["Open price"].astype(float)) ,"Condition"]=1
        return self.df   
      




        
        
lasttime=None


open_order_list=[]
closed_order_list=[]


    
        
for x in dbh.select():
    order=Order()
    order.new_order(x[2],dt.datetime.strptime(x[1], "%d/%m/%Y %H:%M:%S"),"ETHUSDT",1,5)
    order.set_id(x[0])  
    open_order_list.append(order)

   


while(True):
              

       
    
    try:
        klines = client.futures_klines(symbol='ETHUSDT', interval=Client.KLINE_INTERVAL_5MINUTE,limit=125)
    except:
        print("Binance Bağlantısı Sağlanamadı")
        
    columns=["open time","Open price","High price","Low price","Close price","Volume","Kline close time","Quote asset volume","Number of trades","Taker buy base asset volume","Taker buy quote asset volume","Unused field."]
    df = pd.DataFrame(klines,columns=columns)
    df['open time'] = pd.to_datetime(df['open time'], unit='ms')
    

    sh = StrategyHelper(df)
    _=sh.getIFTSTOCH()
    _=sh.getBB(df["Close price"])
    _=sh.getRSI()
    _=sh.IFTSTOCH_condition()
    _=sh.BB_condition()
    _=sh.RSIcondition()
        
    
    if(sh.all_condition().tail(1)["Condition"].values[0]==1 and lasttime != sh.all_condition().tail(1)["open time"].values[0] and sh.all_condition().tail(12)["Condition"].fillna(0).values.sum() == 1):
        lasttime=sh.all_condition().tail(1)["open time"].values[0]

        order=Order()
        order.new_order(df.tail(1)["Close price"].astype(float).values[0],dt.datetime.now(),"ETHUSDT",1,5)
        dbh.insert(order.open_time.strftime("%d/%m/%Y %H:%M:%S"),float(order.entry_price))
        order.set_id(dbh.last_id()[0][0])  
        open_order_list.append(order)

        message="ID: "+ str(order.id) + " 🔻 Short Sinyal 🔻"

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=$CHAT_ID&text="+message
        re=requests.get(url).json()
        
   

    clone_open_order_list = open_order_list

    for order in clone_open_order_list:
        order.check_stop(df.tail(1)["Close price"].astype(float).values[0])
        if(order.status=="Closed"):
            dbh.delete(order.id)
            dbh.insert2_closed(order.id,order.open_time.strftime("%d/%m/%Y %H:%M:%S"),dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), float(order.entry_price), float(order.get_profit(df.tail(1)["Close price"].astype(float).values[0])))
            
            closed_order_list.append(order)
            open_order_list.remove(order)

    del clone_open_order_list    
    
    for x in dbh.select_alerts():
        alert=Alert()
        alert.new_alert(x[0],x[1],x[2],x[3])      
        alert.check_alert(df.tail(1)["Close price"].astype(float).values[0])
        

    for x in dbh.select_perc_alerts():
        alert=PercAlert()
        alert.new_alert(x[0],x[1],x[2],x[3],x[4],x[5])      
        alert.check_alert()
    
        
    time.sleep(5)   

