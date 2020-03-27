# FleetMan

API server for a fleet management system aided by digital twins

The companion Android app's source code is available [here](https://github.com/Aayushjn/FleetMan-Android).

___
#### Setup
Clone this repo `git clone https://github.com/Aayushjn/FleetMan.git`.

Ensure that you have a MySQL server set up.

Once set up, create a new Python3 virtualenv with `python3 -m virtualenv <path/to/virtualenv/name>` and activate it 
with `source <path/to/virtualenv/name>/bin/activate`. Install all dependencies using `
pip install -r requirements.txt`.

Create a `.flaskenv` file with the following contents:
```.env
FLASK_APP=api_server.py
FLASK_ENV=development
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=8000
```

Also set up a `.env` file with the following environment variables: `DATABASE_URL`, `DITTO_USERNAME`, `DITTO_PASSWORD`, 
and `DITTO_NAMESPACE`.

##### Eclipse Ditto Setup
As of now, the server connects to an Eclipse Ditto instance (running in a Docker container) to fetch twin data.
Ensure that **Docker** and **Docker Compose** are installed on your system. 

Clone into the Eclipse Ditto repo with `git clone https://github.com/eclipse/ditto.git`. Run the Ditto container with 
`docker-compose -f <path/to/ditto/repo>/deployment/docker/docker-compose.yml up -d`.

Before running the container, a new username and password must be registered with Nginx. To do that, run the following:
`openssl passwd -quiet` for the password _fleetman_. Open `<path/to/ditto/repo>/deployment/docker/nginx.htpasswd` and append the line 
`fleetman-dev:<output of command>`.

The initial policies and twins can be set up by running [`./setup_ditto.sh`](setup_ditto.sh). It requires 
[HTTPie](https://httpie.org/doc#installation).
 
___
#### Running the server
The server will run on `0.0.0.0:8000` with the command `flask run`.

If any changes are made to the models defined in [models.py](app/models.py), stop the server and run `flask db migrate`.
This creates a DB migration script which is executed with `flask db upgrade`. After this point, simply run the server.

After the server has been run, the database tables are created and then the vehicle data can be loaded from 
[cars.sql](cars.sql).