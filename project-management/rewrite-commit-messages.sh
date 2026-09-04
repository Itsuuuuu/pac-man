#!/usr/bin/env bash
# Reecrit UNIQUEMENT les messages des 51 commits de l'historique.
# Les auteurs, les dates et le contenu des commits ne sont pas touches.
#
# Chaque message a ete ecrit a partir du diff reel du commit concerne.
#
# ATTENTION : cette operation change tous les hash de commits. Le depot est
# partage entre 4 personnes : prevenez tout le monde AVANT, et chacun devra
# re-cloner ou faire `git fetch && git reset --hard origin/main` apres le push.
#
#   usage :  bash project-management/rewrite-commit-messages.sh
#   puis  :  git push --force-with-lease origin main
#
# Une branche de sauvegarde est creee automatiquement. Pour tout annuler :
#   git reset --hard backup-avant-reecriture-messages

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Erreur : le working tree n'est pas propre. Commitez ou stashez d'abord." >&2
    exit 1
fi

git branch -f backup-avant-reecriture-messages
echo "Sauvegarde creee : backup-avant-reecriture-messages"

MAP_FILE="$(mktemp)"
cat > "$MAP_FILE" <<'MAPEOF'
e259391 chore: initialise le depot (gitignore, README)
286f4e4 feat(config): squelette du projet, Makefile et parser de config
a5cd6e8 feat(config): chargement du fichier JSON et point d'entree src/__main__
28caa73 docs: complete le README
e688771 feat(maze): integre le paquet mazegenerator et ebauche GameSetting
b328abe chore: fusion des branches locales
2097304 feat(config): make run fonctionne, config validee par Pydantic
2c1b744 refactor(config): extrait width/height/seed de la config et retire les prints de debug
f6c14e6 feat(engine): prepare GameSetting pour l'affichage Pygame
7c682e9 feat(engine): ajoute characters.py et tile.py
4fe740b feat(engine): ajoute l'enum Pacgum et le drapeau de fin de partie
a8782d7 feat(engine): lit vies, pacgums et score depuis la config
d08d0ae feat(ghosts): premiere version du deplacement par BFS
97f5fb9 docs(ghosts): commente l'algorithme de parcours en largeur
003d667 docs(ghosts): note les cibles par fantome pour l'algo unique
8eab07e feat(engine): construit la map et place les pacgums
cb8ee97 chore: integre le travail de Ryan sur ghost_algo
dd89d52 fix(engine): corrige les erreurs de construction de la map
2e78e20 feat(ghosts): deplacement autonome des fantomes
d77d28e feat(engine): logique de jeu complete, reste l'affichage
a167cb4 refactor(main): nettoie le point d'entree
2968d15 feat(ui): systeme de highscore persiste dans highscore.json
f5c6d91 feat(ui): menu cheat (invincibilite, vies infinies, fantomes comestibles)
3bfeec5 feat(ui): menu options avec choix de resolution et centrage relatif
93bf959 refactor(ui): deplace le code Pygame dans un package ui/ dedie
2065708 refactor(config): isole le nettoyage des commentaires dans load_json
4cc10d8 fix(engine): corrige le spawn des fantomes dans les coins
cf90dba assets: ajoute les sprites de pacman et des fantomes
cf2a215 refactor: architecture src/ + src/ui/ et integration des assets
15cb14a feat(ui): ecran de saisie du pseudo apres la perte des 3 vies
d76ae97 feat(game): timers separes pacman/fantomes et ralentissement en fuite
869f29f feat(ui): repetition de touche pour regler les valeurs du menu cheat
8525b8c feat(ui): HUD complet (score, vies, niveau, timer) et bonus de points
5d24379 feat(ui): ajoute le menu pause
751340b revert(ui): retire le menu pause ajoute par erreur
259e237 fix(ui): restaure la saisie de valeur du menu cheat
bcd910f feat(ui): reintroduit le menu pause
70e7ffd feat(ui): option de theme avec 4 palettes de couleurs
0c2a664 feat(ui): couleur des murs selon le theme choisi
cc33117 assets: ajoute le son de lancement de partie
2281cad feat(game): fluidite des deplacements et progression des niveaux
7e929db feat(ui): retire l'option Volume non implementee et joue le son au lancement
4027b1d fix(ui): corrige l'indexation du menu options apres le retrait de Volume
be8e6e6 feat(ghosts): sprite des yeux a la mort et trajectoire de fuite
4b7f12a feat(ui): menu cliquable a la souris et son au lancement
52044d1 refactor: indentation 4 espaces, docstrings et annotations de type
fcc7553 build: corrige la regle lint du Makefile et factorise les flags mypy
9f4de0f docs: redige le README et complete la regle install
aa3f82e revert(ui): restaure la version precedente de app.py (perd annotations et 4 espaces)
31ef0b1 feat(ui): remplace le menu Options par un ecran Instructions
6a7ad13 style(ui): uniformise les separateurs de commentaires
MAPEOF

export MAP_FILE
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter '
    short=$(git rev-parse --short "$GIT_COMMIT")
    line=$(grep "^$short " "$MAP_FILE" || true)
    if [ -n "$line" ]; then
        echo "${line#* }"
    else
        cat
    fi
' -- --all

rm -f "$MAP_FILE"

echo
echo "Termine. Verifiez avec :  git log --oneline"
echo "Si tout est bon        :  git push --force-with-lease origin main"
echo "Pour annuler           :  git reset --hard backup-avant-reecriture-messages"
