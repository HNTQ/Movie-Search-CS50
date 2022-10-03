# Movie-Search-CS50

Final project for CS50 Introduction to computer Sciences.

Movie-Search is an application using flask.

## Installation

First, you need to clone this repository:

```bash
git clone https://github.com/HNTQ/Movie-Search-CS50.git
```
Then change into the `Movie-Search-CS50` folder:
```bash
cd Movie-Search-CS50
```

Now, we will need to create a virtual environment and install all the dependencies:
```bash
python3 -m venv venv  # on Windows, use "python -m venv venv" instead
. venv/bin/activate  # on Windows, use "venv\Scripts\activate" instead
pip install -r requirements.txt
```
Before start the app, generate css file:
```bash
npx tailwindcss -i ./static/src/style.css -o ./static/css/main.css
```
then run application
```bash
python app.py
```

## Database

Versions of the database are stored [here](https://drive.google.com/drive/folders/1HBSa8qETHNVWOOtPGPnlrb54g0_1akBr?usp=sharing). (Only accessible for authorized members)
