# I-Gaming Platform with Flask and MongoEngine

[![asciicast](https://asciinema.org/a/143039.png)](https://asciinema.org/a/143039)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

MongoDB, Python 2.7


### Installing

Clone the project, create the env and install the requirements
```
git clone https://github.com/matiasbastos/igaming.git
cd igaming
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

Create admin:

```
fabmanager create-admin
```

Run it:

```
python run.py
```

## Running the tests

To run the tests execute:

```
python run.py
```

## Deployment

Currently is deployed using Gunicorn and Nginx on the url sent on the mail.


## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used
* [MongoEngine](http://mongoengine.org/) - Mongo Lib for Python
* [Flask App Builder](https://github.com/dpgaspar/Flask-AppBuilder) - Used to generate the skeleton


## Authors

* **Matias Bastos** - [LinkedIn](http://ar.linkedin.com/in/matiasbastos)
