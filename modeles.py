import json
import os
from datetime import datetime, date


class Joueur:
    def __init__(self, nom, prenom, date_naissance, id_joueur):
        self.nom = nom
        self.prenom = prenom
        if isinstance(date_naissance, datetime):
            self.date_naissance = date_naissance.strftime('%d/%m/%Y')
        elif isinstance(date_naissance, str):
            self.date_naissance = (
                datetime.strptime(date_naissance, '%Y-%m-%d')
                .strftime('%d/%m/%Y')
            )
        elif isinstance(date_naissance, date):
            self.date_naissance = date_naissance.strftime('%d/%m/%Y')
        else:
            raise TypeError(
                "date_naissance doit être soit une chaîne de caractères, "
                "soit un objet datetime")
        self.id_joueur = id_joueur
        self.points = 0

    def trier_joueurs(joueurs):
        return sorted(joueurs, key=lambda x: (-x.points, x.nom, x.prenom))

    def to_dict(self):
        return {
            'nom': self.nom,
            'prenom': self.prenom,
            'date_naissance': self.date_naissance,
            'id_joueur': self.id_joueur,
            'points': self.points,
        }

    @staticmethod
    def from_dict(data):
        date_naissance_str = data['date_naissance']
        date_naissance = (
            datetime.strptime(date_naissance_str, '%d/%m/%Y').date()
        )
        joueur = Joueur(
            nom=data['nom'],
            prenom=data['prenom'],
            date_naissance=date_naissance,
            id_joueur=data['id_joueur']
        )
        joueur.points = data.get('points', 0)
        joueur.classement_joueur = data.get('classement_joueur', 0)
        return joueur

    def __repr__(self):
        return (
            f"{self.nom} {self.prenom}, Né(e) le {self.date_naissance}, "
            f"ID: {self.id_joueur}, Points: {self.points}"
        )


class Tour:
    def __init__(self, nom, matchs, joueur_exempt=None):
        self.nom = nom
        self.matchs = matchs
        self.joueur_exempt = joueur_exempt

    def to_dict(self):
        return {
            'nom': self.nom,
            'matchs': [match.to_dict() for match in self.matchs],
            'joueur_exempt': (
                self.joueur_exempt.id_joueur if self.joueur_exempt
                else None
            )
        }

    @staticmethod
    def from_dict(data, joueurs, db):
        tour = Tour(data['nom'], [])
        tour.matchs = [
            Match.from_dict(match_data, joueurs, db)
            for match_data in data['matchs']
        ]
        return tour

    def __repr__(self):
        return f"Tour(nom={self.nom}, matchs={self.matchs})"

    def __str__(self):
        result = f"--- {self.nom} ---\n"
        if self.joueur_exempt:
            result += (
                f"{self.joueur_exempt.prenom} {self.joueur_exempt.nom} "
                "est exempté ce tour.\n"
            )
        result += "Matchs pour {self.nom} :\n"
        for match in self.matchs:
            joueur1 = match.joueur1
            joueur2 = match.joueur2
            result += (
                f"{joueur1.prenom} {joueur1.nom} (ID: {joueur1.id_joueur}) vs"
                f" {joueur2.prenom} {joueur2.nom} (ID: {joueur2.id_joueur})\n"
            )
        if self.joueur_exempt:
            result += (
                f"Joueur exempté ce tour: {self.joueur_exempt.id_joueur}\n")
        return result


class Tournoi:
    def __init__(
        self, nom_tournoi, lieu, date_debut, date_fin, id_tournoi,
        description=""
    ):
        self.nom_tournoi = nom_tournoi
        self.lieu = lieu
        if isinstance(date_debut, str):
            self.date_debut = datetime.strptime(date_debut, '%d/%m/%Y').date()
        else:
            self.date_debut = date_debut
        if isinstance(date_fin, str):
            self.date_fin = datetime.strptime(date_fin, '%d/%m/%Y').date()
        else:
            self.date_fin = date_fin
        self.id_tournoi = id_tournoi
        self.tours = []
        self.tour_actuel = 0
        self.description = description
        self.participants = []
        self.db = None
        self.joueur_exempt = None
        self.resultats = {}
        self.paires_deja_jouees = set()
        self.joueurs_exempts = set()

    def classement_tournoi(self):
        scores_tournoi = {id_joueur: 0 for id_joueur in self.participants}

        for tour in self.tours:
            for match in tour.matchs:
                scores_tournoi[match.joueur1.id_joueur] += match.joueur1_score
                scores_tournoi[match.joueur2.id_joueur] += match.joueur2_score

        classement = sorted(
            scores_tournoi.items(), key=lambda x: x[1], reverse=True
        )
        print("\nClassement du tournoi :\n")
        for rang, (id_joueur, points) in enumerate(classement, start=1):
            joueur = self.db.joueurs_dict[id_joueur]
            print(f"{rang}. {joueur.prenom} {joueur.nom} - {points} points")

        self.db.save()

    def trier_participants(self, db):
        participants = [
            db.joueurs_dict[participant_id]
            for participant_id in self.participants
        ]
        participants.sort(key=lambda joueur: joueur.points, reverse=True)
        return participants

    def tous_les_resultats_sont_remplis(self):
        for tour in self.tours:
            for match in tour.matchs:
                if match.resultat == "0 - 0":
                    return False
                if match.resultat is None:
                    return False
                if match.resultat == "En attente":
                    return False
        return True

    def generer_un_tour(self, db):

        if len(self.tours) >= 4:
            print(
                "\nLe tournoi a déjà 4 tours. "
                "Aucun nouveau tour ne peut être créé."
            )
            return

        if len(self.participants) < 2:
            print("\nPas assez de participants pour générer un match")
            return

        if not self.tous_les_resultats_sont_remplis():
            print(
                "\nTous les résultats des matchs précédents doivent "
                "être entrés avant de générer un nouveau tour."
            )
            return

        joueurs = self.trier_participants(db)

        matchs = []
        joueur_exempt = None

        if len(joueurs) % 2 != 0:
            for joueur in joueurs:
                if joueur.id_joueur not in self.joueurs_exempts:
                    joueur_exempt = joueur
                    self.joueurs_exempts.add(joueur.id_joueur)
                    joueurs.remove(joueur)
                    break

        joueurs_disponibles = joueurs[:]
        paires_deja_jouees_local = set(self.paires_deja_jouees)

        while len(joueurs_disponibles) >= 2:
            match_ajoute = False

            for i in range(len(joueurs_disponibles)):
                joueur1 = joueurs_disponibles[i]

                for j in range(i + 1, len(joueurs_disponibles)):
                    joueur2 = joueurs_disponibles[j]
                    paire = (joueur1.id_joueur, joueur2.id_joueur)
                    paire_inverse = (joueur2.id_joueur, joueur1.id_joueur)

                    if (
                        paire not in self.paires_deja_jouees and
                        paire_inverse not in self.paires_deja_jouees
                    ):
                        matchs.append(Match(joueur1, joueur2, db))
                        self.paires_deja_jouees.add(paire)
                        joueurs_disponibles.pop(j)
                        joueurs_disponibles.pop(i)
                        match_ajoute = True
                        break

                if match_ajoute:
                    break

            if not match_ajoute:
                print(
                    "Impossible de trouver une paire valide "
                    "pour les joueurs restants."
                )
                break

        numero_tour = len(self.tours) + 1
        tour = Tour(
            nom=f"Tour {numero_tour}",
            matchs=matchs, joueur_exempt=joueur_exempt
        )
        self.tours.append(tour)

        self.paires_deja_jouees.update(paires_deja_jouees_local)

        print(f"\n--- {tour.nom} ---\n")
        for match in tour.matchs:
            joueur1 = match.joueur1
            joueur2 = match.joueur2
            print(
                f"- {joueur1.prenom} {joueur1.nom} (ID: {joueur1.id_joueur}) "
                f"vs {joueur2.prenom} {joueur2.nom} (ID: {joueur2.id_joueur})"
            )

        if tour.joueur_exempt:
            print(
                f"\nJoueur exempté ce tour: {tour.joueur_exempt.id_joueur} "
                f"({tour.joueur_exempt.nom} {tour.joueur_exempt.prenom}) \n"
            )

        db.save()

    def ajouter_participant(self, joueur):
        if joueur.id_joueur not in self.participants:
            self.participants.append(joueur.id_joueur)
            self.resultats[joueur.id_joueur] = 0
            return (
                f"\nJoueur {joueur.prenom} {joueur.nom} "
                "ajouté au tournoi avec succès !"
            )
        else:
            return (
                f"\nLe joueur {joueur.prenom} {joueur.nom} "
                "est déjà inscrit à ce tournoi."
            )

    def to_dict(self):
        return {
            'nom_tournoi': self.nom_tournoi,
            'lieu': self.lieu,
            'date_debut': self.date_debut.strftime('%d/%m/%Y'),
            'date_fin': self.date_fin.strftime('%d/%m/%Y'),
            'id_tournoi': self.id_tournoi,
            'tours': [tour.to_dict() for tour in self.tours],
            'participants': self.participants,
            'joueur_exempt': self.joueur_exempt,
            'description': self.description,
        }

    @staticmethod
    def from_dict(data, db):
        tournoi = Tournoi(
            nom_tournoi=data['nom_tournoi'],
            lieu=data['lieu'],
            date_debut=(
                datetime.strptime(data['date_debut'], '%d/%m/%Y').date()
            ),
            date_fin=(
                datetime.strptime(data['date_fin'], '%d/%m/%Y').date()
            ),
            id_tournoi=data['id_tournoi'],
            description=data.get('description', '')
        )

        participants = data.get('participants', [])
        tournoi.participants = participants
        tournoi.joueur_exempt = data.get('joueur_exempt', None)

        tournoi.db = db
        tournoi.tours = (
            [
                Tour.from_dict(tour_data, tournoi.db.joueurs, db)
                for tour_data in data.get('tours', [])
            ]
        )

        return tournoi

    def __repr__(self):
        return (
            f"Tournoi(nom_tournoi={self.nom_tournoi}, lieu={self.lieu}, "
            f"date_debut={self.date_debut}, date_fin={self.date_fin})"
        )


class Match:
    def __init__(self, joueur1, joueur2, db, joueur1_score=0, joueur2_score=0):
        self.joueur1 = joueur1
        self.joueur2 = joueur2
        self.joueur1_score = joueur1_score
        self.joueur2_score = joueur2_score
        self.db = db
        self.resultat = None

    def retirer_score(self, match):

        if match.joueur1.id_joueur in self.db.joueurs_dict:
            joueur1 = self.db.joueurs_dict[match.joueur1.id_joueur]
            if match.joueur1_score == 1:
                joueur1.points -= 1
            elif match.joueur1_score == 0.5:
                joueur1.points -= 0.5

        if match.joueur2.id_joueur in self.db.joueurs_dict:
            joueur2 = self.db.joueurs_dict[match.joueur2.id_joueur]
            if match.joueur2_score == 1:
                joueur2.points -= 1
            elif match.joueur2_score == 0.5:
                joueur2.points -= 0.5

        for tournoi in self.db.tournois:

            if self.joueur1.id_joueur in tournoi.resultats:
                if self.joueur1_score == 1:
                    tournoi.resultats[self.joueur1.id_joueur] -= 1
                elif self.joueur1_score == 0.5:
                    tournoi.resultats[self.joueur1.id_joueur] -= 0.5

            if self.joueur2.id_joueur in tournoi.resultats:
                if self.joueur2_score == 1:
                    tournoi.resultats[self.joueur2.id_joueur] -= 1
                elif self.joueur2_score == 0.5:
                    tournoi.resultats[self.joueur2.id_joueur] -= 0.5

    def set_scores(self, joueur1_score, joueur2_score):
        self.retirer_score(self)
        self.joueur1_score = joueur1_score
        self.joueur2_score = joueur2_score
        score1 = self.format_score(joueur1_score)
        score2 = self.format_score(joueur2_score)

        self.resultat = f"{score1} - {score2}"

        if joueur1_score == 1:
            self.joueur1.points += 1
        elif joueur2_score == 1:
            self.joueur2.points += 1
        else:
            self.joueur1.points += 0.5
            self.joueur2.points += 0.5

    def format_score(self, score):
        return f"{int(score)}" if score.is_integer() else f"{score:.1f}"

    def to_dict(self):
        return {
            'joueur1': self.joueur1.id_joueur,
            'joueur2': self.joueur2.id_joueur,
            'joueur1_score': self.joueur1_score,
            'joueur2_score': self.joueur2_score
        }

    @staticmethod
    def from_dict(data, joueurs, db):
        joueur1 = next(
            (joueur for joueur in joueurs
             if joueur.id_joueur == data['joueur1']),
            None
        )
        joueur2 = next(
            (joueur for joueur in joueurs if
             joueur.id_joueur == data['joueur2']), None
        )
        if joueur1 and joueur2:
            match = Match(joueur1, joueur2, db)
            match.set_scores(data['joueur1_score'], data['joueur2_score'])
            return match
        return None

    def __repr__(self):
        return (
            f"Match(joueur1={self.joueur1}, joueur2={self.joueur2}, "
            f"joueur1_score={self.joueur1_score},"
            f"joueur2_score={self.joueur2_score}"
        )

    def __str__(self):
        return (
            f"{self.joueur1} vs {self.joueur2} - "
            f"Résultat: {self.resultat if self.resultat else 'N/A'}"
        )


class Database:
    def __init__(self):
        self.joueurs_file = 'joueurs.json'
        self.tournois_file = 'tournois.json'
        self.joueurs_dict = {}
        self.joueurs = []
        self.tournois = []
        self.participants = []
        self.load_data()

    def load_data(self):
        self.joueurs = self.load_joueurs()
        self.joueurs_dict = {j.id_joueur: j for j in self.joueurs}
        self.tournois = self.load_tournois()

    def load_joueurs(self):
        joueurs = []
        if os.path.exists(self.joueurs_file):
            with open(self.joueurs_file, 'r', encoding='utf-8') as file:
                joueurs_data = json.load(file)
                joueurs = [Joueur.from_dict(joueur) for joueur in joueurs_data]
        return joueurs

    def load_tournois(self):
        tournois = []
        if os.path.exists(self.tournois_file):
            with open(self.tournois_file, 'r', encoding='utf-8') as file:
                tournois_data = json.load(file)
            for tournoi_data in tournois_data:
                tournoi = Tournoi.from_dict(tournoi_data, self)
                tournois.append(tournoi)
        return tournois

    def ajouter_joueur(self, joueur):
        if joueur.id_joueur not in [j.id_joueur for j in self.joueurs]:
            self.joueurs.append(joueur)
            self.joueurs_dict[joueur.id_joueur] = joueur
            self.save()
            print(
                f"Joueur {joueur.prenom} {joueur.nom} ajouté à la base de "
                "données avec succès !")
        else:
            print(
                f"Le joueur {joueur.prenom} {joueur.nom} est déjà inscrit "
                "dans la base de données.")

    def ajouter_tournoi(self, tournoi):
        if tournoi.id_tournoi not in [t.id_tournoi for t in self.tournois]:
            self.tournois.append(tournoi)
            self.save()

    def save(self):
        if (len(self.tournois) == 0):
            print("LISTE DE TOURNOIS VIDE")

        with open(self.joueurs_file, 'w', encoding='utf-8') as file:
            json.dump(
                [joueur.to_dict() for joueur in self.joueurs],
                file,
                indent=4,
                default=self.default
            )

        with open(self.tournois_file, 'w', encoding='utf-8') as file:
            json.dump(
                [tournoi.to_dict() for tournoi in self.tournois],
                file,
                indent=4,
                default=self.default
            )

    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime('%d/%m/%Y')
        raise TypeError(
            f"Object of type {obj.__class__.__name__} "
            "is not JSON serializable")
