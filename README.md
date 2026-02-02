<table align="center"><tr><td align="center" width="9999">

# Vibrana

Analyzing large vibration signals progressively through visual fingerprints.

<img alt="Demo" src="./teaser.png" align="center" width="600" />

</td></tr></table>

## Setup
Vibrana is a web application designed to run locally, 
ensuring that your data will never be stored in the cloud. 
Due to its complex architecture, we provide a Docker setup 
that can be run on any common operating system capable of 
running Docker. Below you will find two ways of setting up Vibrana:
Either via Docker (easy, but not suitable for development) or manually (hard, but suitable for development).
In both cases, the data folder must be initiated first.

### Setting up the data folder

Vibrana does not feature uploading data through the UI, instead data is supplied to the prototype by placing it in a folder "data" within the project root.
The application will automatically recognize valid files and make them available for exploration. There is no need to register them in any way in a database,
however, to make this level of flexibility possible, a specific folder structure must be adhered.

[TODO: Precise description of data folder]

### Docker Setup

1. Windows and Mac: Install [Docker Desktop](https://docs.docker.com/desktop/), Linux: Install [Docker Engine](https://docs.docker.com/engine/install/)
2. Clone this repository.
3. Open a terminal (PowerShell on Windows) within the Vibrana source code folder.
4. Execute the command `docker compose up`  
  _We kindly ask for your patience as the initial setup might take a few minutes._
5. Your local Vibrana instance is available at [http://localhost:5000](http://localhost:5000).

### Manual Setup

In case you do not want to use docker, we provide a manual installation procedure below. First, ensure that the following prerequisites are met:

* [**MongoDB**](https://www.mongodb.com/)
* [**Redis**](https://redis.io/docs/latest/get-started/): Only available directly on Linux, Windows & Mac users need to use a [Docker container](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/).
* [**NodeJS**](https://nodejs.org/en): Required to build the frontend.
* [**Python 3.13**](https://www.python.org/): Required to run the backend. 
* [**Poetry**](https://python-poetry.org/): Used to manage the Python dependencies within this project.

Next, follow the subsequent steps to install Vibrana:

1. Start MongoDB and Redis, such that these services are running in the background.
2. Clone this repository and open a terminal or PowerShell within the project folder.
3. Switch to `./vibrana/frontend` and run `npm i` followed by `npm run build`.
4. Switch back to the project root folder.
5. Install the Python packages via `poetry install --no-root`.
6. Set the `PYTHONPATH` environment variable to the project root folder.
7. Start Vibrana via `poetry run python3 vibrana/backend/main.py` (Replace `python3` with `py` if on Windows).
8. Open a new terminal window / PowerShell instance within the same folder.
9. Start the coordinator thread via `poetry run python3 vibrana/backend/threads/coordinatorThread.py` (Replace `python3` with `py` if on Windows).
10. Your local Vibrana instance is available at [http://localhost:5000](http://localhost:5000).
