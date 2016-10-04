# dota2league-tracker
[![Code Climate](https://codeclimate.com/github/Daerdemandt/dota2league-tracker/badges/gpa.svg)](https://codeclimate.com/github/Daerdemandt/dota2league-tracker)
[![Test Coverage](https://codeclimate.com/github/Daerdemandt/dota2league-tracker/badges/coverage.svg)](https://codeclimate.com/github/Daerdemandt/dota2league-tracker/coverage)
[![Issue Count](https://codeclimate.com/github/Daerdemandt/dota2league-tracker/badges/issue_count.svg)](https://codeclimate.com/github/Daerdemandt/dota2league-tracker)

Simple webservice to track ongoing matches in dota2leagues

###Quickstart:

+ `cp dota2league-tracker/config.yml.example dota2league-tracker/config.yml`

+ Edit `dota2league-tracker/config.yml` - add your Steam API key and hooks you need

+ `docker-compose up`

You should now have an instance running and listening on 5000 port for leagues to track.
