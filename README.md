## Environment Setup / Running

Before running any of the code in this project, make sure to set up the environment.

```
pipenv --python 3.7.3 shell
pipenv install
```

To anonymize your own data, [download your data from Facebook](https://www.facebook.com/help/1701730696756992) as a JSON and move the `facebook-data` folder you get into this directory. Your own anonymized data should appear in the `facebook-data-anonymous` folder after running:

```
cd scripts
python anonymize_data.py
```