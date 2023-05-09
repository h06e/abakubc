# Abakubc

A tool to compare PBC, KUBC and descret KUBC.

By Robin Valmalette

# Add a new geometry:

- Create the main file and place it in /src/geometries/
- in `make_inp.py`, add `from geometry import <geo_name>`
- update the constants file if PBC and KUBC are required
- make KUBC and PBC gen file
- update operation.py to tell how to compute the porosity
- update `extract_th.py` :)

Help for geo generation : `session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)`

Pour le PBC, il est fortement conseillé de suivre exactement les commandes (avec les bounding box etc...) après la génération de la pièce sinon ca ne marche pas. Cela est causé par un phénomène relevant de la sorcellerie et la documentation oublira volontairement ce point.