# BinanceTradeAlert

Bu proje, Binance borsasında belirli bir stratejiye dayalı al-sat işlemleri yapmak ve yüksek hacimli ticaret sinyallerini Telegram üzerinden göndermek için yazılmıştır. Ayrıca, bu işlemleri bir SQL sunucusunda depolamak için strategybot.py ve whalebot.py adında iki Python betiği ve SQL verilerini çeken, web sitesinde gösteren ve bot ayarlarını yapmanızı sağlayan bir Golang sunucusu olan start_server.go dosyasını içermektedir.

## Kurulum
Aşağıdaki adımları izleyerek projeyi yerel makinenize kurabilirsiniz.

#### Gereksinimler
* Python 3.x
* Golang
* SQL Sunucusu (ör. MySQL, PostgreSQL)

### Kurulum Adımları
1. Bu depoyu yerel makinenize klonlayın:
```
git clone https://github.com/mustafagl/BinanceTradeAlert.git
```
2. Python bağımlılıklarını yükleyin:
```
pip install -r requirements.txt
```
3. Golang sunucusunu başlatmak için aşağıdaki komutu çalıştırın:
```
go run start_server.go
```

4. SQL sunucusunda gerekli veritabanını oluşturun ve bağlantı bilgilerini config.py dosyasında yapılandırın.

5. strategybot.py ve whalebot.py dosyalarında stratejilerinizi, API anahtarlarınızı, TOKEN ve SQL verilerinizi yapılandırın.

6. strategybot.py ve whalebot.py dosyalarını çalıştırarak botları başlatın:
```
python strategybot.py
python whalebot.py
```
Botlar çalışırken, Golang sunucusu verileri çekecek ve web sitesinde gösterecektir.

## Kullanım

- Web Sitesinin Ana Sayfasından Kapalı ve Açık tradelerinizi görebilirsiniz.

<img width="720" alt="home-closed_trades" src="https://github.com/mustafagl/BinanceTradeAlert/assets/69797446/d821551e-3bd4-450a-906d-5c7899b0a8a1"><img width="720" alt="home-open_trades" src="https://github.com/mustafagl/BinanceTradeAlert/assets/69797446/650db902-3333-4b45-97b7-4cbd8f648ec8">

- Alerts kısmında alarmlarnızı oluşturup silebilirsiniz.
<img width="720" alt="alerts-WhaleAlerts" src="https://github.com/mustafagl/BinanceTradeAlert/assets/69797446/69e34a0e-8d61-48d0-8481-0018afb9f9ce">
<img width="720" alt="alerts-PriceAlerts" src="https://github.com/mustafagl/BinanceTradeAlert/assets/69797446/c31c131d-4a24-4814-a0af-f175b5f9df01">
<img width="720" alt="alers_PercentChangeAlerts" src="https://github.com/mustafagl/BinanceTradeAlert/assets/69797446/3e3a76d5-0f7d-4c42-b05e-ec7567e8d518">

- Ayarlar kısmında botunuzun ayarlarını yapılandırabilirsiniz.
<img width="720" alt="bot_settings" src="https://github.com/mustafagl/BinanceTradeAlert/assets/69797446/8f17d796-a8da-4d3b-a943-228b5aa65773">








