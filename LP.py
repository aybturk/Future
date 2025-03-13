import requests
import json
import time

def get_realtime_stock_data(symbol, api_key):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Tüm yanıtı incelemek için yazdırabilirsiniz
        print(f"{symbol} için tam yanıt:")
        print(json.dumps(data, indent=4))
        
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            return data["Global Quote"]
        else:
            print(f"Hata: {symbol} için beklenen veri alınamadı.")
            return None
    except requests.RequestException as e:
        print(f"HTTP isteği sırasında hata oluştu: {e}")
        return None
    except ValueError as e:
        print(f"JSON parse edilirken hata oluştu: {e}")
        return None

api_key = "X5H5PW3ZSZ8HATP9"
symbols = ["Brent OIL", "GOLD"]

while True:
    print("----- Anlık Fiyat Bilgileri -----")
    for symbol in symbols:
        quote_data = get_realtime_stock_data(symbol, api_key)
        if quote_data is not None:
            price = float(quote_data.get("05. price", 0))
            trading_day = quote_data.get("07. latest trading day", "Bilinmiyor")
            print(f"{symbol} fiyatı: {price} (En son güncelleme: {trading_day})")
        else:
            print(f"{symbol} için veri alınamadı.")
    print("---------------------------------")
    
    # API limitleri ve güncellik açısından bekleme süresi ayarlanabilir
    time.sleep(60)