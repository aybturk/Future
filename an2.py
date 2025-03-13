import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint
from scipy.signal import periodogram

# Hugging Face üzerinden Bitcoin verisini çekmek için
from datasets import load_dataset

# -------------------------------------------
# 1. USD/EUR Verisini Lokal Olarak Tanımlama
# -------------------------------------------
# Aşağıda paylaştığınız örnek satırları, bir list of dict yapısında topladık.
# (Gerçekte daha fazla satırınız olabilir, hepsini ekleyebilirsiniz.)
usd_eur_data = [
    {"DATE": "2020-03-25", "TIME PERIOD": "25 Mar 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0827"},
    {"DATE": "2020-03-26", "TIME PERIOD": "26 Mar 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0981"},
    {"DATE": "2020-03-27", "TIME PERIOD": "27 Mar 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0977"},
    {"DATE": "2020-03-30", "TIME PERIOD": "30 Mar 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.1034"},
    {"DATE": "2020-03-31", "TIME PERIOD": "31 Mar 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0956"},
    {"DATE": "2020-04-01", "TIME PERIOD": "01 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0936"},
    {"DATE": "2020-04-02", "TIME PERIOD": "02 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0906"},
    {"DATE": "2020-04-03", "TIME PERIOD": "03 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0785"},
    {"DATE": "2020-04-06", "TIME PERIOD": "06 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0791"},
    {"DATE": "2020-04-07", "TIME PERIOD": "07 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0885"},
    {"DATE": "2020-04-08", "TIME PERIOD": "08 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0871"},
    {"DATE": "2020-04-09", "TIME PERIOD": "09 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0867"},
    {"DATE": "2020-04-14", "TIME PERIOD": "14 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0963"},
    {"DATE": "2020-04-15", "TIME PERIOD": "15 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0903"},
    {"DATE": "2020-04-16", "TIME PERIOD": "16 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0888"},
    {"DATE": "2020-04-17", "TIME PERIOD": "17 Apr 2020", "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "1.0860"}
]

# DataFrame'e dönüştürelim
df_euro = pd.DataFrame(usd_eur_data)
print("USD/EUR DataFrame sütunları:", df_euro.columns)

# Sütunları yeniden isimlendirelim (DATE -> date, US dollar/Euro... -> close_eur)
df_euro = df_euro.rename(columns={
    "DATE": "date",
    "US dollar/Euro (EXR.D.USD.EUR.SP00.A)": "close_eur"
})

# Dönüşüm: close_eur string görünüyor, float'a çevirelim
df_euro["close_eur"] = df_euro["close_eur"].astype(float)

# Tarih sütununu datetime formatına çevirip indeks olarak ayarlayalım
df_euro["date"] = pd.to_datetime(df_euro["date"])
df_euro.set_index("date", inplace=True)
df_euro = df_euro.sort_index()

print("\nUSD/EUR verisinden örnek satırlar:")
print(df_euro.head())

# --------------------------------------------
# 2. Bitcoin Verisini Hugging Face'ten Çekme (ibchitel/bitcoin_dataset_1221)
# --------------------------------------------
print("\nBitcoin verisi 'ibchitel/bitcoin_dataset_1221' üzerinden yükleniyor...")

ds = load_dataset("ibchitel/bitcoin_dataset_1221")  # Tüm split'leri indirecektir
df_btc = ds["train"].to_pandas()  # train kısmını DataFrame'e dönüştür

print("\nBitcoin veri seti sütunları:", df_btc.columns)
# Görselde: timestamp, open, high, low, close, volume, vb.

# Beklenen sütunlar: "timestamp" ve "close"
if "timestamp" not in df_btc.columns or "close" not in df_btc.columns:
    raise Exception("Bitcoin verisinde 'timestamp' veya 'close' sütunu bulunamadı!")

# timestamp -> date, close -> close_btc
df_btc = df_btc.rename(columns={"timestamp": "date", "close": "close_btc"})

# Tarih sütununu datetime formatına çevirip indeks olarak ayarlayalım
df_btc["date"] = pd.to_datetime(df_btc["date"])
df_btc.set_index("date", inplace=True)
df_btc = df_btc.sort_index()

print("\nBitcoin verisinden örnek satırlar:")
print(df_btc.head())

# --------------------------------------------
# 3. Veri Setlerini Birleştirme (Inner Join)
# --------------------------------------------
df_merged = pd.merge(df_euro, df_btc, left_index=True, right_index=True, how="inner")
df_merged.dropna(inplace=True)

print("\nBirleşik veri seti (ilk 5 satır):")
print(df_merged.head())

# --------------------------------------------
# 4. Temel İstatistiksel Analiz: Kovaryans ve Korelasyon
# --------------------------------------------
cov_matrix = np.cov(df_merged["close_eur"], df_merged["close_btc"])
corr_coef = df_merged["close_eur"].corr(df_merged["close_btc"])

print("\nKovaryans Matrisi:")
print(cov_matrix)
print("\nPearson Korelasyon Katsayısı:", corr_coef)

# --------------------------------------------
# 5. Cointegration (Eşbütünleşme) Testi
# --------------------------------------------
score, pvalue, _ = coint(df_merged["close_eur"], df_merged["close_btc"])
print("\nCointegration Test Skoru:", score)
print("Cointegration Test p-değeri:", pvalue)

# --------------------------------------------
# 6. Spektral Analiz
# --------------------------------------------
f_eur, Pxx_eur = periodogram(df_merged["close_eur"])
f_btc, Pxx_btc = periodogram(df_merged["close_btc"])

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.semilogy(f_eur, Pxx_eur)
plt.title("USD/EUR Spektral Yoğunluğu")
plt.xlabel("Frekans")
plt.ylabel("Yoğunluk")

plt.subplot(1, 2, 2)
plt.semilogy(f_btc, Pxx_btc)
plt.title("Bitcoin Spektral Yoğunluğu")
plt.xlabel("Frekans")
plt.ylabel("Yoğunluk")

plt.tight_layout()
plt.show()