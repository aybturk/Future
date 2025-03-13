import requests

# Alpha Vantage API ayarları
api_key = "X5H5PW3ZSZ8HATP9"
symbol = "AAPL"  # Apple hissesi
interval = "5min"  # Verileri 5 dakikalık zaman diliminde al
outputsize = "compact"  # Yalnızca en son verileri almak için

# API URL'sini oluştur
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}&outputsize={outputsize}"

# API isteği gönder
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    # Verileri işle (örneğin, gün içindeki en son fiyat değişimini yazdır)
    time_series = data.get("Time Series (5min)", {})
    if time_series:
        # En son güncelleme zamanını ve fiyat verisini al
        latest_time = next(iter(time_series))  # JSON'daki ilk anahtar en son zamandır
        latest_data = time_series[latest_time]
        print(f"En son güncelleme zamanı: {latest_time}")
        print(f"Açılış fiyatı: {latest_data['1. open']}")
        print(f"Yüksek fiyat: {latest_data['2. high']}")
        print(f"Düşük fiyat: {latest_data['3. low']}")
        print(f"Kapanış fiyatı: {latest_data['4. close']}")
        print(f"İşlem hacmi: {latest_data['5. volume']}")
    else:
        print("Veri bulunamadı.")
else:
    print(f"API isteği başarısız oldu. Durum kodu: {response.status_code}")