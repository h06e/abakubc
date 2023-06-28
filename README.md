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

# Check-list

Dans le slurm :
- répertoires
- nom de campagne
- --nodelist
- Mémoire
- Nombre de task

# TODO

Liste de choses à faire (27.06.2023) :
- Convergence de KUBC vers PBC : Quid de la croute?
- Outils de comparaison pour l'article : erreur avec les normes, comparaison coef par coef, les invariants, et distance par rapport aux symétrie (distance par rapport à l'orthotropie, ...)
- Tirage des éprouvettes au hasard : tester différents condition pour les prendre. Par exemple, rotation fixée, translation (0,0), puis (0,L/2). Oui (0,0), puis (0,L/3) et (0,2L/3)...
- Faire le tetrachiral
- Faire un snub square
- Faire un github avec la machine (faire du tri, beaucoup)
- Faire un github pour processus de génération des éprouvettes