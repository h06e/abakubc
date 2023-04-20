import matplotlib.pyplot as plt

"""
BROUILLON
Permet de ploter les erreurs en matrice de couleur
"""

fig, ax = plt.subplots(figsize=(3, 3))
im = plt.imshow(global_deviation, cmap='OrRd')
plt.xticks(np.arange(len(labs)), labels=labs)
plt.yticks(np.arange(len(labs)), labels=labs)
plt.xticks(rotation=45, ha="right", rotation_mode="anchor")
# plt.setp(ax, rotation=45, ha="right",
#          rotation_mode="anchor")
# Loop over data dimensions and create text annotations.
for i in range(len(labs)):
    for j in range(len(labs)):
        text = plt.text(j, i, '{:.2f}'.format(global_deviation[i, j]) if not np.isnan(global_deviation[i, j]) else '',
                        ha="center", va="center", color="black")
plt.title("Err. Glob.")
fig.tight_layout()
plt.savefig(os.path.abspath(os.getcwd())[
            :-4]+'/results/' + folder_name+'/error_'+TEST_ID+'.pdf')
plt.savefig(os.path.abspath(os.getcwd())[
            :-4]+'/results/' + folder_name+'/error_'+TEST_ID+'.png', dpi=300)
# plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)


plt.show()