# initialize project

all terminal commands must be executed from the root of the project directory, i.e. in `simulation/`.

## requirements
python needs to be installed on the system

tested with python 3.14

all 

## create virtual environment
```bash
python -m venv .venv
```

## activate virtual environment
on linux/mac:
```bash
source .venv/bin/activate
```
or on windows using powershell:
```bash
.venv\Scripts\activate
```
or using cmd on windows:
```cmd
.venv\Scripts\activate.bat
```

## install dependencies (with activated virtual environment, otherwise dependencies will be installed globally)
```bash
pip install -r requirements.txt
```

## run the application (with activated virtual environment)
```bash
python main.py
```

### use of the application
- to open a saved track, click on "Datei" and then "Datei öffnen"
- to add rail-segments, left-click on an open segment end and choose the desired segment and connection end
- to remove rail-segments, right-click on the segment and choose "Segment entfernen"
- to save the track, click on "Datei" and then "Datei speichern"
- to set start or end point, right-click on the desired segment and choose "Startpunkt setzen" or "Endpunkt setzen"
- to place a train, right-click on the desired segment and choose "Fahrzeug platzieren" - make sure that enough rail-segments are available at the disired location to fit the train in its entirety (currently hardcoded to contain locomotive and 3 wagons behind that need approximately 2 segments)
  - when a train is placed and the track contains one ore many segments, marked as "is_allowed_destination" ("Zielpunkt"), the train will automatically start progressing towards one randomly chosen allowed destination - if no allowed destination is set in the track, the train will choose a random segment within the track as its destination
- switches are set automatically when a train approaches them, however it is possible to toggle switches manually by right-clicking on the switch and choosing "Weiche umstellen"

for a demonstration of the application, please open "analysis-tracks/UmkehrkurveC.json". Then place a train on the single origin segment (marked by a small, filled black circle) and see how the train starts its journey towards the destination segment (marked by a slightly larger, non-filled black circle). This scenario demonstrates the ability of the DijkstraRail algorithm to find a path when it is necessary to inverse the trains wagon-order in order to reach the destination that is constained by a short remaining track length and thus not able to fit the train wagons-first.
To demonstrate the difference, simply add a few more segments behind the destination segment, place a new train and see how the train progresses towards the destination without inverting.
