# Plugin for CraftBeerPi 3.0 to send Tilt sensors to BrewFather
Send tilt information from CraftBeerPi3 to the BrewFather website for tracking fermantation.

## Pre-requisites
Brewfather https://web.brewfather.app
CraftBeerPi 3.0 https://github.com/Manuel83/craftbeerpi3
---- add the tilt plugin

## Configuration for CraftBeerPi
1. In CraftBeerPi3 set up each Tilt as a pair of sensors, one for Temperature immediately followed by the same Tilt for Gravity
2. Make sure the devices are reporting data to CraftBeerPi3
3. Download this plugin into the craftbeerpi3/modules/plugins directory and restart CraftBeerPi3

## CraftBeerPi3 Parameters
1. Set brewfather_comment to the text you would like to appear along with the reading details (e.g. "Posted from CraftBeerPi 3.0")
2. Set the brewfather_id to the text that follows the ?id= text in the Cloud URL on the Brewfather / Settings / Utility / Tilt Hydrometer
   It will look something like "4ZXbnm8TY7asdf"

## Results
1. Logging occurs every 15 minutes. Wait a while for some values to log.
2. Go to the Fermenting tab of the Brewfather Batches for the relevant batch. The graph will show logged temperature and Gravity values
3. The Edit button will show individual logged results and the comment.

## Improvements
