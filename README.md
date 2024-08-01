# Application de Tournoi d'Échecs

Bienvenue dans l'Application de Tournoi d'Échecs ! Cette application facilite la gestion complète de tournois d'échecs, en vous permettant de créer, gérer et suivre les tournois avec une interface intuitive.


## Prérequis


Avant de pouvoir exécuter ce projet, assurez-vous d'avoir installé Python 3.12 ou version ulterieure. Vous pouvez vérifier que le logiciel est bien installé avec la commande suivante :

**Pour Windows :**
```
python --version
```
**Pour macOS et Linux :**
```
python3 --version
```


### Installation des Dépendances


Clonez le repository GitHub et installez les dépendances :

```
git clone https://github.com/Kudzu86/OpenclassroomsProjects/tree/p4-27/07
cd OpenclassroomsProjects/p4-27/07
pip install -r requirements.txt
```
La première commande clone le repertoire avec tous les fichiers sur votre machine locale, la deuxième vous place dans le répertoire du projet pour acceder à ces fichiers, et la troisième installe toutes les dépendances nécessaires pour exécuter l'application.


### Exécution de l'Application


Pour lancer l'application, créez un environnement virtuel avant d'exécuter le programme qui vous donnera directement accès au menu principal :

**Pour Windows :**
```
.\env\Scripts\activate
python controllers.py
```
**Pour macOS et Linux :**
```
source env/bin/activate
python3 controllers.py
```


## Fonctionnalités

### Menu Principal

Le menu principal de l'application offre plusieurs onglets permettant différentes actions :

- Ajouter/modifier des joueurs et des tournois à la base de données
- Voir le classement des joueurs et les tournois de la base de données
- Inscrire des joueurs aux tournois, générer les matchs et saisir les résultats
- Possibilité de réinitialiser la totalité des scores en fin de saison

### Fichiers du Projet

#### Contrôleurs (`controllers.py`)
- Contient la logique de gestion des interactions entre le modèle et la vue.
- Gère les actions de l'utilisateur et met à jour les vues en conséquence.
- Classe ApplicationController

#### Modèles (`modeles.py`)
- Définit les structures de données et les opérations de manipulation des données.
- Modélise les entités principales comme les joueurs et les tournois.
- Principales classes :
  - `Tournoi`
  - `Joueur`
  - `Tour`
  - `Match`

#### Vues (`vues.py`)
- Gère l'affichage et la présentation des données à l'utilisateur.
- Fournit les interfaces utilisateur pour les différentes actions.
- Classe View


### Utilisation


#### Gestion des Joueurs

1. Sélectionnez l'option "1. Ajouter/Modifier un joueur".
2. Ajoutez ou modifiez les joueurs via les options disponibles.
3. Sélectionnez l'option "3. Voir le classement général", pour afficher tous les joueurs de la base de données classés en fonction de leur classement général (tous les scores de tournois cumulés).

   
#### Gestion d'un Nouveau Tournoi

1. Sélectionnez l'option "2. Ajouter/Modifier un tournoi" dans le menu principal.
2. Entrez les informations requises : nom, lieu, date, nombre de tours, etc.
3. Vous pouvez voir la totalité des tournois de la base de données en sélectionant l'option "4. Voir les tournois".
4. Ajoutez les joueurs au tournoi en sélectionnant l'option "5. Inscrire un joueur à un tournoi".


#### Démarrage et Suivi des Tournois

1. Sélectionnez l'option "6. Générer les matchs et tours pour un tournoi" lorsque tous les participants sont inscrits.
2. Sélectionnez le tournoi correspondant, cette action vous génèrera un seul tour.
3. Sélectionnez l'option "7. Saisir/Modifier les résultats" pour rentrer les scores des matchs terminés.
4. Une fois tous les résultats du premier tour rentrés, vous pourrez à nouveau générer un tour via l'option "6. Générer les matchs et tours pour un tournoi". etc.
5. La fin d'un tournoi est actée a la fin de 4ème tour, vous ne pourrez donc pas créer de 5ème tour.
6. Possibilité de réinitialiser la totalité des scores en fin de saison en sélectionnant l'option "8. Réinitialiser scores".


### Auteur

AUER Eric



### Licence

Ce projet est sous licence TATOUTI. Voir le fichier LICENSE pour plus de détails.
