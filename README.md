# Grocery Search

Search the following shops for any items:

- Tesco
- Morrisons
- Waitrose
- Aldi
- Sainsburys
- Asda

## Installation

Use Python 3 and the package manager [pip](https://pip.pypa.io/en/stable/) to install.

Written/tested on Python 3.8.5 installed through [pyenv](https://github.com/pyenv/pyenv).

```bash
pyenv install 3.8.5
pyenv shell 3.8.5
python --version # Check Python version is now `Python 3.8.5`
pip install requirements.txt 
```

You will also need [chromedriver](https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver) installed.

## Usage

```bash
python main.py "baked beans"
```

### Flags

```
--number-of-items, -n: The maximum number of items to return
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)