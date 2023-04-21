# Abakubc

A tool to compare PBC, KUBC and descret KUBC.

By Robin Valmalette

# Add a new geometry:

- Create the main file and place it in /src/geometries/
- update the constants file if PBC and KUBC are required
- make KUBC and PBC gen file
- update operation.py to tell how to compute the porosity

Help for geo generation : `session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)`