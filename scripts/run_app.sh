#!/bin/bash

APP_DIR="src"

uvicorn ${APP_DIR}.event:app --reload 