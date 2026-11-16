from datetime import datetime, timedelta
from getpass import getpass

import psycopg

baslangic = datetime.strptime(input("Tarih (YYYY-AA-GG): ").strip(), "%Y-%m-%d")
bitis = baslangic + timedelta(days=1)

sorgu = """
SELECT olcum_zamani, tuketim_kwh
FROM public.enerji_analiz
WHERE olcum_zamani >= %s
  AND olcum_zamani < %s
ORDER BY olcum_zamani;
"""

with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="daewoo_energy",
    user=input("Kullanici adi: "),
    password=getpass("PostgreSQL sifresi: "),
    connect_timeout=5,
) as baglanti:
    kayitlar = baglanti.execute(sorgu, (baslangic, bitis)).fetchall()
    gecmis = baglanti.execute(
        """
        SELECT SUM(tuketim_kwh)
        FROM public.enerji_analiz
        WHERE olcum_zamani >= %s AND olcum_zamani < %s
          AND EXTRACT(ISODOW FROM olcum_zamani) = %s
        GROUP BY olcum_zamani::date
        HAVING COUNT(*) = 96
           AND COUNT(DISTINCT olcum_zamani) = 96
           AND COUNT(tuketim_kwh) = 96
        """,
        (baslangic - timedelta(weeks=4), baslangic, baslangic.isoweekday()),
    ).fetchall()
    

print("Olcum sayisi:", len(kayitlar))

beklenen = {baslangic + timedelta(minutes=15 * i) for i in range(96)}
gelen = {zaman for zaman, tuketim in kayitlar}

if beklenen - gelen:
    print("Eksik olcum zamani var")
elif gelen - beklenen:
    print("Beklenmeyen olcum zamani var")
elif len(kayitlar) != len(gelen):
    print("Tekrarli olcum var")
elif any(tuketim is None for zaman, tuketim in kayitlar):
    print("Bos tuketim degeri var")
else:
    toplam = sum(tuketim for zaman, tuketim in kayitlar)
    print(f"Gunluk toplam: {toplam:.2f} kWh")

    if len(gecmis) < 3:
        print("Yeterli referans verisi yok")
    else:
        referans = sum(satir[0] for satir in gecmis) / len(gecmis)
        print(f"Referans: {referans:.2f} kWh ({len(gecmis)} gun)")

        if referans == 0:
            print("Referans sifir; yuzde fark hesaplanamadi")
        else:
            fark_yuzde = (toplam - referans) / referans * 100
            karar = "İncele" if fark_yuzde >= 20 else "Normal"
            print(f"Referansa gore fark: %{fark_yuzde:.2f}")
            print(f"Karar: {karar}")

 