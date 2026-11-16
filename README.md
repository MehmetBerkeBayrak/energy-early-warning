# Energy Consumption Early Warning System

A local web app that simulates a steel plant energy team's morning review.
This independent portfolio prototype uses public DAEWOO Steel data from 2018.

## How it works

Select a date in the browser. The Python API reads PostgreSQL and checks for
96 expected quarter-hour readings, with no duplicate timestamps or missing values.

The baseline averages eligible days with the same day of the week in the previous
four weeks. It excludes the selected date and all future dates. A decision requires
at least three eligible reference days and a nonzero baseline.

The app flags consumption at least **20% above baseline**. A flag prompts
investigation; it does not prove a fault. Low consumption does not trigger an alert.

## Verified examples

| Date | Result |
| --- | --- |
| 2018-01-26 | Flagged: 7,069.29 kWh vs. 5,688.23 kWh, up 24.28%. |
| 2018-01-19 | Consumption available; insufficient baseline data. |
| 2018-02-16 | No alert; consumption was 94.32% below baseline. |

The 2018 backtest flagged **81 of 344 evaluable days (23.5%)**.
Another 263 days were below the threshold; 21 had no decision.

## Run locally

1. Prepare the `daewoo_energy` database on `localhost:5432`. The app reads
   `olcum_zamani` and `tuketim_kwh` from `public.enerji_analiz`.
2. Create a virtual environment: `python -m venv .venv`
3. Install dependencies: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
4. Start the app: `.\.venv\Scripts\python.exe enerji_api.py`
5. Enter your PostgreSQL credentials in the terminal and open
   [the local app](http://127.0.0.1:8000/). The JSON endpoint is `/api/gunluk/YYYY-MM-DD`.

Run `gecmis_test.py` to regenerate `gunluk_uyarilar.csv`.
Open `Enerji_Erken_Uyari.pbix` to explore the results in Power BI Desktop.
To refresh on another computer, update the CSV source path in Power Query.

This prototype runs locally on historical data and does not send live alerts.

Data source: [UCI Steel Industry Energy Consumption](https://doi.org/10.24432/C52G8C),
CC BY 4.0.
