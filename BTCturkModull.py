import base64
import hashlib
import hmac
import time
import requests
import datetime

class CustomError(Exception):
    def __init__(self, message):
        print(message)

class BTCturkProperty:
    apiAdr = "https://api.btcturk.com"
    userBalanceAdr = "/api/v1/users/balances"
    serverTimeAdr = "/api/v2/server/time"
    userTransactionAdr = "/api/v1/users/transactions/trade"
    openOrderAdr = "/api/v1/openOrders"
    cancelOrderAdr = "/api/v1/order"
    submitOrderAdr = "/api/v1/order"
    allOrderAdr = "/api/v1/allOrders"
    ticker = "/api/v2/ticker"
    publicKey = "BTCtürk Public Key"
    privateKey = "BTCtürk Private Key"
class BTCturk(BTCturkProperty):

    def __init__(self):
        self.public_key = self.publicKey
        self.private_key = base64.b64decode(self.privateKey)

    def getUserBalance(self, method="GET"):
        """
        Kullanıcı Bakiyesini List olarak döner
        """
        uri = self.apiAdr + self.userBalanceAdr
        params = ""
        json = ""
        headers = self.setRequestHeaders()
        return (self.getResponseList(uri, params , json, headers, method))

    def getUserTransactions\
                    (self, action={"buy","sell"}, currency={"btc","try","xrp"}, startdate="",enddate="", method="GET"):
        """
        kullanıcı trade işlemleri raporu,startdate,eddate boş veirlirse defaul 30 günlük işlem dönr
        """
        startDate = str(int(startdate.timestamp())*1000)
        endDate = str(int(enddate.timestamp()) * 1000)
        uri = self.apiAdr + self.userTransactionAdr
        params = {"type":action, "symbol":currency, "startDate":startDate,"endDate":endDate }
        json=""
        headers = self.setRequestHeaders()
        return (self.getResponseList(uri, params, json, headers, method))

    def getOpenOrder(self, currency="", method="GET"):
        """
        satış emirleri(bids = satış emiri, asks=alış)
        currency boş ise tüm order döner
        """
        uri = self.apiAdr + self.openOrderAdr
        params = {"pairSymbol":currency}
        json=""
        headers = self.setRequestHeaders()
        return (self.getResponseList(uri, params, json, headers, method))

    def cancelOrder(self, orderid, method="GET"):
        """
        OrderId ile emir iptal edilir,dönüş değeri True/False olur
        """
        uri = self.apiAdr + self.cancelOrderAdr
        params = {"id":orderid}
        json = ""
        headers = self.setRequestHeaders()
        return (self.getResponseBool(uri, params, json, headers, method))

    def submitOrder(self, quantity, price, action, currency, method="GET"):
        """
        Yeni emir oluşturulur
        """

        uri = self.apiAdr + self.submitOrderAdr
        json={"quantity":float(quantity), "price":float(price),
                  "stopPrice":0, "newOrderClientId":"", "orderMethod":"limit",
                  "orderType":action, "pairSymbol":currency}
        params = {}
        headers = self.setRequestHeaders()
        return (self.getResponseList(uri, params, json, headers, method))

    def getAllOrder(self,currency="", method="GET"):
        """
        tüm emirleri döner,id gönderirsen tek döner
        """
        uri = self.apiAdr + self.allOrderAdr
        params = {"pairSymbol":currency}

        json = {}
        headers = self.setRequestHeaders()
        return (self.getResponseList(uri, params, json, headers, method))

    ################Public Endpoint#########################################
    def getlastPrice(self, currency, method="GET"):
        """
        Güncel fiyat dönüşü yapılır
        """
        uri = self.apiAdr + self.ticker
        if (currency != None):
            params = {"pairSymbol": currency}
        else:
            params = {}

        json = {}
        headers = self.setRequestHeaders()
        return (self.getResponseList(uri, params, json, headers, method))
    ################Yardımcı fonksiyonlar###################################
    def getResponseList(self, url, params, json, headers, method):
        """
        BTCtürk API sinden dönen datayı,List olarak return e verir
        """
        result = requests.request(method=method, url=url, params=params, json=json, headers=headers)

        if (str(result.status_code) != "200") and (str(result.status_code) != "400"):
            message = "Servis Hata:" + str(result.text) +"::"+result.raise_for_status()
            raise CustomError(message)

        resultDict = result.json()
        ######Servis dönüş Data kontrol edilir
        self.contralResponseList(resultDict)

        #######bazı methodlarda sadece success bakmak yeterli
        DataList = resultDict["data"]

        return DataList

    def getResponseBool(self, url, params, json, headers, method):
        """
           BTCtürk API sinden ile yapılan işlem başarılı mı? sonucu döner
        """
        result = requests.request(method=method, url=url, params=params,  json=json, headers=headers)

        if (str(result.status_code) != "200") and (str(result.status_code) != "400"):
            message = "Servis Hata:" + str(result.text) + "::" + result.raise_for_status()
            raise CustomError(message)

        resultDict = result.json()
        ######Servis dönüş Data kontrol edilir
        self.contralResponseList(resultDict)

        #######bazı methodlarda sadece success bakmak yeterli
        DataBool = resultDict["success"]
        return DataBool

    def contralResponseList(self,resultDict):
        """
        Servisten dönen data kontrol edilir
        """
        if (str(resultDict["success"]) != "True"):
            #####API den true dönmezse
            # str(resultDict["message"])
           message = "Servis Hata:"+str(resultDict["message"])
           print(message)
           # raise CustomError(message)

        try:
            if(resultDict["data"]["asks"] == [] and resultDict["data"]["bids"] == []):
                message = "Servis Hata:Veri bulunamadı:asks ya da bids listesinden biri boş"
                print(message)
                # raise CustomError(message)
            ######BTCtürk Methodları data Listesinin içinde asks,bids Listeleri de olabilir
            ######Varsa değişkenler bakılır, yoksa hatasız devam etsin
        except TypeError:
            pass
        except KeyError:
            pass

        try:
            if(resultDict["data"] == None):
                message = "Servis Hata:Veri bulunamadı"
                print(message)
                # raise CustomError(message)
        except TypeError:
            pass
        except KeyError:
            pass
        print("Kontrol veri hata yok")

    def getTime(self):
        """
        BTCtürk saati ile destop saati arasındaki farktan dolayı,
        BTCtürk saati kullanılır
        BTCtürk Result:
        {'serverTime': 1610809962794, 'serverTime2': '2021-01-16T15:12:42.7937437+00:00'}
        ServerTime okunur
        """

        resultDict = {}
        timeMethodName = self.apiAdr + self.serverTimeAdr
        serverTime = requests.get(url = timeMethodName)
        resultDict = dict(serverTime.json())


        time = str(resultDict["serverTime"])
        return time

    def getSignature(self,time):
         """"
         API call da kullanılan headers için BTCtürk formatına uygun signature oluşturulur
         """
         time1 = time
         data = "{}{}".format(self.public_key, time1).encode("utf-8")
         signature = hmac.new(self.private_key, data, hashlib.sha256).digest()
         signature = base64.b64encode(signature)
         return signature

    def setRequestHeaders(self):
        """
        private methodları çağırmak içn headers oluşturulur
        """
        time = self.getTime()
        signature = self.getSignature(time=time)
        headers = { "X-PCK": self.public_key,
                    "X-Stamp": time,
                    "X-Signature": signature,
                    "Content-Type" : "application/json"}
        return headers






