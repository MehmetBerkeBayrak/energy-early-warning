import csv
from datetime import date, timedelta
from getpass import getpass

import psycopg

def referans_hesapla(gun, gunluk_toplamlar):
    gecmis = []

    for hafta in range(1, 5):
        onceki_gun = gun - timedelta(weeks=hafta)
        if onceki_gun in gunluk_toplamlar:
            gecmis.append(gunluk_toplamlar[onceki_gun])

    if len(gecmis) < 3:
        return None

    return sum(gecmis) / len(gecmis)


sorgu = """
SELECT olcum_zamani::date, SUM(tuketim_kwh)
FROM public.enerji_analiz
WHERE olcum_zamani >= TIMESTAMP '2018-01-01'
  AND olcum_zamani <  TIMESTAMP '2019-01-01'
GROUP BY 1
HAVING COUNT(*) = 96
   AND COUNT(DISTINCT olcum_zamani) = 96
   AND COUNT(tuketim_kwh) = 96
"""

with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="daewoo_energy",
    user=input("Kullanici adi: "),
    password=getpass("PostgreSQL sifresi: "),
    connect_timeout=5,
) as baglanti:
    toplamlar = dict(baglanti.execute(sorgu).fetchall())

uyari = normal = referans_yok = 0

for gun, toplam in toplamlar.items():
    referans = referans_hesapla(gun, toplamlar)
    if referans is None or referans == 0:
        referans_yok += 1
    elif (toplam - referans) / referans * 100 >= 20:
        uyari += 1
    else:
        normal += 1

print("SQL kontrollerini gecen gun:", len(toplamlar))
print("Incele:", uyari)
print("Normal:", normal)
print("Referans yok veya sifir:", referans_yok)
print("\nYalnizca %20 esiginde isaretlenen gunler:")

for gun, toplam in sorted(toplamlar.items()):
    referans = referans_hesapla(gun, toplamlar)
    if referans is None or referans == 0:
        continue

    fark = (toplam - referans) / referans * 100
    if 20 <= fark < 30:
        print(f"{gun}: %{fark:.2f}")
with open("gunluk_uyarilar.csv", "w", encoding="utf-8-sig", newline="") as dosya:
    yazici = csv.writer(dosya)
    yazici.writerow(["gun", "toplam_kwh", "referans_kwh", "fark_yuzde", "karar"])

    for gun, toplam in sorted(toplamlar.items()):
        referans = referans_hesapla(gun, toplamlar)
        if referans is None or referans == 0:
            yazici.writerow([gun, f"{toplam:.2f}", "", "", "Referans yok veya sifir"])
        else:
            fark = (toplam - referans) / referans * 100
            karar = "İncele" if fark >= 20 else "Normal"
            yazici.writerow([gun, f"{toplam:.2f}", f"{referans:.2f}", f"{fark:.2f}", karar])

print("CSV olusturuldu: gunluk_uyarilar.csv")