#!/usr/bin/env bash

conda config --add channels conda-forge
conda config --set channel_priority

conda install google-api-python-client
conda install youtube-transcript-api