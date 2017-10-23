# I-Gaming Platform with Flask and MongoEngine

[![asciicast](https://asciinema.org/a/143039.png)](https://asciinema.org/a/143039)

This is a simple igaming platform, made with flask and mongodb. The idea was to keep it simple and have all the game logic under one class (Game class). This configuration enables a lot of possible deploy architectures, it could be runing behind an http api (as the example here), with ZeroMQ or run serverles on AWS with Api Gateway + AWS Lambda. Also the data model design was made having in mind that every transaction in the wallet must be immutable. This improves the data consistency and also enables the possibility of having a cron process (with Celery), that every day collects all the data for every user, moves that rows to a 'historical' db and writes a resume of the latest user account status. This way will be super easy to scale, even with out cache.

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
py.test -v
```

## Deployment

Currently is deployed using Gunicorn and Nginx on the url sent on the mail.


## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used
* [MongoEngine](http://mongoengine.org/) - Mongo Lib for Python
* [Flask App Builder](https://github.com/dpgaspar/Flask-AppBuilder) - Used to generate the skeleton


## Authors

* **Matias Bastos** - [LinkedIn](http://ar.linkedin.com/in/matiasbastos)
