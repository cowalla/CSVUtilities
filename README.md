# CSV Utilities

### Everyone needs some really basic CSV utilities in Python.

Every once in a while I find I need to write a script in Python to parse a CSV.
This could be for taxes, ingesting raw data into a database, or fixing messed-up data.

I needed a way to manipulate CSVs in Python, so I made this library after reinventing the wheel several times. It makes editing and processing CSV data a lot simpler.

### Installation
```shell
pip install csv-utilites
```

### Basic Usage
```python
from csv_utilities import open_csv


CSV_PATH = '~/Documents/transactions.csv'


transactions = open_csv(CSV_PATH)  # Reads the file and creates a CSV object. 
transactions.echo()  # Prints the CSV to STDOUT
```

