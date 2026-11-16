import json 
from pathlib import Path
from datetime import datetime, timedelta
from getpass import getpass
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg 
from pathlib import Path

kullanici = input("PostgreSQL kullanici adi: ")
sifre = getpass("PostgreSQL sifresi: ")

sorgu = """
SELECT olcum_zamani, tuketim_kwh
FROM public.enerji_analiz
WHERE olcum_zamani >= %s AND olcum_zamani < %s
"""


class EnerjiAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            sayfa = Path(__file__).with_name("index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(sayfa)
            return
        on_ek = "/api/gunluk/"
        if not self.path.startswith(on_ek):
            return self.json_gonder(404, {"hata": "Adres bulunamadı."})

        try:
            baslangic = datetime.strptime(self.path[len(on_ek):], "%Y-%m-%d")
            bitis = baslangic + timedelta(days=1)
        except (ValueError, OverflowError):
            return self.json_gonder(400, {"hata": "Geçerli bir tarih gir: YYYY-AA-GG."})

        try:
            with psycopg.connect(
                host="localhost", port=5432, dbname="daewoo_energy",
                user=kullanici, password=sifre, connect_timeout=5,
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
        except psycopg.Error:
            return self.json_gonder(503, {"hata": "Veritabanı sorgusu çalışmadı."})

        beklenen = {baslangic + timedelta(minutes=15 * i) for i in range(96)}
        gelen = {zaman for zaman, _ in kayitlar}
        sonuc = {"gun": baslangic.date().isoformat(), "olcum_sayisi": len(kayitlar)}

        if gelen != beklenen or len(kayitlar) != len(gelen):
            sonuc.update(toplam_kwh=None, veri_durumu="Ölçüm zamanları eksik veya hatalı")
        elif any(kwh is None for _, kwh in kayitlar):
            sonuc.update(toplam_kwh=None, veri_durumu="Boş tüketim değeri var")
        else:
            toplam = sum(kwh for _, kwh in kayitlar)
            sonuc.update(toplam_kwh=float(round(toplam, 2)), veri_durumu="Tam")

            referans = sum(satir[0] for satir in gecmis) / len(gecmis) if len(gecmis) >= 3 else None

            if referans is None or referans == 0:
                sonuc.update(karar="Yeterli referans yok", referans_kwh=None, fark_yuzde=None)
            else:
                fark = (toplam - referans) / referans * 100
                sonuc.update(
                    referans_kwh=float(round(referans, 2)),
                    fark_yuzde=float(round(fark, 2)),
                    karar="İncele" if fark >= 20 else "Normal",
                )
        self.json_gonder(200, sonuc)

    def json_gonder(self, durum, veri):
        govde = json.dumps(veri, ensure_ascii=False).encode("utf-8")
        self.send_response(durum)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(govde)


print("API hazır: http://127.0.0.1:8000/api/gunluk/2018-01-19")
HTTPServer(("127.0.0.1", 8000), EnerjiAPI).serve_forever()