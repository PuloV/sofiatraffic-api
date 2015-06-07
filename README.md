# sofiatraffic-api
## Third party API that gives you info for the urbon transport in Sofia Bulgaria
This is a server that will serve a json info for the transport in Sofia.
The information will be in the form of a JSON.
- ``` GET /trolley/1/ ``` will return the information about the trolley №1 for the current day
- ```GET /trolley/1/2015-01-01 ``` will return the information about the trolley №1. for the 1st January 2015

Also supported transports are autobuses and tramways