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

# TODO list

Liste de choses à faire (27.06.2023) :
- Convergence de KUBC vers PBC : Quid de la croute?
- Outils de comparaison pour l'article : erreur avec les normes, comparaison coef par coef, les invariants, et distance par rapport aux symétrie (distance par rapport à l'orthotropie, ...)
- Tirage des éprouvettes au hasard : tester différents condition pour les prendre. Par exemple, rotation fixée, translation (0,0), puis (0,L/2). Puis (0,0), puis (0,L/3) et (0,2L/3)...
- Faire un github avec la machine (faire du tri, beaucoup)
- Faire un github pour processus de génération des éprouvettes
- Verifier le script de la croute KUBC
- Faire le losange complet
- Faire le ménage dans le gitignore, c'est le bordel
- Refaire des notebook propres dans trop de md pour être générique (un par mésoS ou un commun?)
- Faire un  notebook dédié au R0 (et ce qui en rapproche avec le losange et le composite)
- Essayer de comprendre ce qui se passe avec le carré à 45°
- ajouter utilities/image dans le gitignore

<!-- # * Calcul d'un composite 0/45 
# * Dans la base du pli
K_pli_0=np.array([[100,3,0.0], [3,10,0], [0,0,5]])

angle = pi/4
c, s = cos(angle), sin(angle)
T = np.array([[c**2, s**2, c*s],
                [s**2, c**2, -c*s],
                [-2*s*c, 2*c*s, (c**2-s**2)]])
K_pli_45 = np.dot(np.dot(np.transpose(T), K_pli_0), T)

K_empilement=0.5*(K_pli_0+K_pli_45)

K_list = []
theta_list = np.arange(0, 2*pi, pi/1000)

for t in theta_list:
    angle = t
    c, s = cos(angle), sin(angle)
    T = np.array([[c**2, s**2, c*s],
                  [s**2, c**2, -c*s],
                  [-2*s*c, 2*c*s, (c**2-s**2)]])
    K = np.dot(np.dot(np.transpose(T), K_empilement), T)
    K_list.append(K)


K_list = np.array(K_list)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.plot(theta_list, K_list[:, 0, 0], 'r', label=r'$K_{11}$')
ax.plot(theta_list, K_list[:, 1, 1], 'g', label=r'$K_{22}$')
ax.plot(theta_list, K_list[:, 0, 1], 'b', label=r'$K_{12}$')
ax.plot(theta_list, K_list[:, 2, 2], 'k', label=r'$K_{33}$')

ax.grid(True)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax.set_title("Exemple d'un composite 0/45", va='bottom')
plt.draw()


K_list=K_list
# * Cf equation 2 de vannucci terme avec R0
res_Re = K_list[:, 0, 0]-2*K_list[:, 1, 0]-4*K_list[:, 2, 2]+K_list[:, 1, 1]
res_Im = K_list[:, 0, 2]-K_list[:, 1, 2]
plt.figure()
plt.plot(theta_list, res_Re, 'r', label='Partie réelle')
plt.plot(theta_list, res_Im, 'b', label='Partie imaginaire')
plt.plot(theta_list, K_list[:, 2, 2], 'k', label=r'$K_{33}$')
plt.legend()
plt.show()
-->


<!--
# discussion snub square avec nico

Salut Nico, J'ai une petite Q rapide sur le snub square. Est-ce que c'est un matériau lattice comme j'ai trouvé dans quelques articles ? ou est-ce que c'est un monolithique hétérogène composé de deux matériaux différents ?
image.png 
image.png
:bulle_de_parole:  9 h 55
Tout d'abord ca depend de ce que tu qualifie de lattice, si lattice => réseau de poutres ou assimilé c'est mort
Aujourd’hui à 10 h 03Afficher le fil de discussion
:bulle_de_parole:  9 h 55
Aprés tu peux mettre deux phases differentes dans les site bleu et rouge
9 h 56
ou mettre du vide dans le rouge (cf. these de Batpiste Durand)
9 h 56
si tu met du vide dans le rouge, attention au jonction entre les phases de matière bleu
9 h 56
mais ca se comportera comme un milieu a cinématique du second gradient
9 h 57
en bref un mecanisme car les carrés bleu vont se comporter en solides rigides articulés au jonction
9 h 59
Si dans l'homogenisation KUBC tu centre ton échantillon sur un element rouge ton échantillon possédera les symétries par mirroir que contient les 2 traingel rouge =>D2
9 h 59
Mais tu peux aussi centré ton echantillon sur le carré bleu, le centre du carré est un axe d'invaraince par rotation d'ordre 4
10 h
Le gag dans ce pavage c'est qu'il n'existe pas 1 point dans lequel s'exprime toute les symétries
10 h
de fait selon le centrage tu en favorise certaines au detriment des autres
10 h 05
Le pavage est dit non-symmorphe
10 h 05
p4g est son petit nom
10 h 06
l'ideal c'est de faire la moyenne d'un KUBC centré sur le losange D2 + d'une KUBC centré sur le carré Z4
  10 h 06
Ok, dans le cas où je choisis de mettre du vide dans les zones rouges, je n'aurais pas de raideur de premier gradient à priori. Il faudrait que je rajoute une relation aux jonctions donc...

si tu veux un second gradient parfait faut mettre des pivots aux jonctions
  il y a 18 minutes
Oui mais je verrai rien en premier gradient :perplexe: je vais faire un bi-phasé.
:bulle_de_parole:  il y a 17 minutes
Pas dans la direction des modes mous
:bulle_de_parole:  il y a 16 minutes
mais tous les modes ne sont pas degeneré
:bulle_de_parole:  il y a 15 minutes
dans ce cas tu peux tourner ton echantilon, pour obtenir des rigidité de partout, et dans un deuxième temps faire l'analyse spectrale du tensuer d'élasticité reconstruit

 10 h 06
pour restaurer la symétrie sans avoir a augmenter la sépartion des echelles
  10 h 08
Ok, en tout cas merci !

-->
