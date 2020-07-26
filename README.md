# Make plots of COVID-19 latest data from Johns Hopkins database

To use:

* Download/clone the two python source codes to the same folder
* Edit `makeplots_auto.py`, add more or fewer countries/provinces
* Run `makeplots_auto.py` with python3:
```
$ python makeplots_auto.py
```

Note: Sometimes Johns Hopkins updates the github csv files retrospectively. In this case
just delete all files from the automatically created `data` subfolder and the code will 
redownload them fresh.
