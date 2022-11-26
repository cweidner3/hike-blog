#!/bin/bash

FLASK_APP=src.main /venv/bin/flask db upgrade

exec "${@}"
