\# Energy Consumption Early Warning System



A local web application for reviewing daily electricity consumption at a

steel plant. This independent portfolio prototype uses public DAEWOO Steel

data from 2018 to simulate a plant energy team's morning review.



\## What the application does



Select a date in the browser. The Python API queries PostgreSQL, checks

that all 96 expected 15-minute readings are present without duplicates or

blank values, and calculates daily consumption.



The baseline is the average of eligible days that fall on the same day of

the week over the prior four weeks. The selected date and future dates

are excluded. At least three eligible reference days and a nonzero

baseline are required.



The application flags increases of \*\*20% or more\*\* for review. Lower

consumption does not trigger an alert. A flag is a prompt to investigate,

not evidence of an equipment fault.



\## Verified examples



| Date | Result |

| --- | --- |

| 2018-01-26 | Flagged: 7,069.29 kWh vs. 5,688.23 kWh, up 24.28% |

| 2018-01-19 | Consumption available, but insufficient baseline data |

| 2018-02-16 | Below the alert threshold: consumption was 94.32% below baseline |



The 2018 backtest flagged \*\*81 of 344 evaluable days (23.5%)\*\*.

Another 263 days were below the threshold and 21 had no decision.

The Power BI report summarizes these historical results.



\## Run locally



The application expects PostgreSQL on `localhost:5432`, with a database

named `daewoo\_energy` and a prepared `public.enerji\_analiz` table containing

`olcum\_zamani` and `tuketim\_kwh`.



From PowerShell in the project folder:



```powershell

python -m venv .venv

.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt

.\\.venv\\Scripts\\python.exe enerji\_api.py

```



Enter your PostgreSQL credentials in the terminal, then open

\[the local application](http://127.0.0.1:8000/). The JSON endpoint is

`/api/gunluk/YYYY-MM-DD`.



To regenerate `gunluk\_uyarilar.csv`, run `gecmis\_test.py` with the same

Python environment. Open `Enerji\_Erken\_Uyari.pbix` in Power BI Desktop. To

refresh it on another computer, update the CSV source path in Power Query.



This prototype runs locally on historical data and does not send live alerts.



Data source: \[UCI Steel Industry Energy Consumption](https://doi.org/10.24432/C52G8C),

CC BY 4.0.

