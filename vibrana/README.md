# React Flask Template

This repository offers a skeleton to create a React app with Flask in the backend.
Additionally, the React part offers an architecture for query calling.

## Requirements

This setup assumes Linux, but should work fine on Windows and MacOS too.
Important:
* Python 3.11 or later
* NodeJS >= v21.6.2

## Setup

* In the `frontend` folder:
  * Execute `npm i && npm run dev`
* In the `backend` folder:
  * Create a venv using `python3 -m venv venv && source ./venv/bin/activate`
  * Install all packages `pip3 install -r requirements.txt`
  * Run the backend `python3 main.py`