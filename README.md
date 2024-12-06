# Steam Recommendation App
The Steam Recommendation App will assist users in finding video game titles that they may like based on the preferences of similar users. 
The user will enter their 17-digit steam ID and using the data provided by Steam API, the app will train data using PySpark. The top 10 
recommended items will be displayed to the users. 


## Set Up and Installation

Install Python 3.x in order to run Flask

```bash
git clone https://github.com/kevquat/Steam-Recommendation-App
```

```bash
cd Steam-Recommendation-App
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Running PySpark 
When working with PySpark, you might encounter issues with configuring the PYSPARK_PYTHON environmental variable. 

### Windows
1) Open System Properties -> Environmental Variables
2) Under "User Variables for...", click New and set:
        - Variable name:PYSPARK_PYTHON
        - Variable value: The full path to your python executable file
3) Click OK to save changes
4) Restart the terminal or IDE 

# Running the app

```bash
python app.py
```

## Viewing the App

Go to http://127.0.0.1:5000
