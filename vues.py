import re
from modeles import Joueur, Tournoi
from datetime import datetime


class View:
    @staticmethod
    def afficher_menu():
        print("\n\nMenu Principal\n")
        print("1. Ajouter/Modifier un joueur")
        print("2. Ajouter/Modifier un tournoi")
        print("3. Voir le classement général")
        print("4. Voir les tournois")
        print("5. Inscrire un joueur à un tournoi")
        print("6. Générer les matchs et tours pour un tournoi")
        print("7. Saisir/Modifier les résultats")
        print("8. Réinitialiser scores")
        print("9. Quitter\n")

    @staticmethod
    def choisir_action_joueur():
        print("1. Ajouter un joueur")
        print("2. Modifier un joueur")
        choix = input("\nChoisissez une option: ")
        return choix

    @staticmethod
    def choisir_action_tournoi():
        print("1. Ajouter un tournoi")
        print("2. Modifier un tournoi")
        choix = input("\nChoisissez une option: ")
        return choix

    @staticmethod
    def afficher_joueurs(joueurs):
        joueurs_tri = Joueur.trier_joueurs(joueurs)
        print("\n\nListe des joueurs:\n")
        for joueur in joueurs_tri:
            print(
                f"{joueur.nom} {joueur.prenom}, "
                f"Né(e) le {joueur.date_naissance}, "
                f"ID: {joueur.id_joueur}, Points: {joueur.points}"
            )

    @staticmethod
    def afficher_tournois(db, tournois):
        if not tournois:
            print("Aucun tournoi disponible.")
            return None
        print("\nListe des tournois:")
        for i, tournoi in enumerate(tournois, start=1):
            print(
                f"{i}. {tournoi.nom_tournoi} à {tournoi.lieu}, "
                f"du {tournoi.date_debut.strftime('%d/%m/%Y')} "
                f"au {tournoi.date_fin.strftime('%d/%m/%Y')}, "
                f"ID: {tournoi.id_tournoi}, "
                f"Nombre de tours max : {tournoi.nombre_max_tours}, "
                f"nombre de participants : {len(tournoi.participants)}"
            )

    @staticmethod
    def choix_tournoi(tournois):
        choix = int(input(
            "\nSélectionnez un tournoi pour voir les détails "
            "(ou 0 pour retourner au menu principal) : "
        )) - 1
        if 0 <= choix < len(tournois):
            tournoi = tournois[choix]

            View.afficher_tours_et_matchs(tournoi)

            return tournoi
        else:
            print("Choix invalide ou retour au menu principal.")
            return None

    @staticmethod
    def validate_joueur_id(id_joueur):
        return re.match(r'^[A-ZA-Z]{2}\d{5}$', id_joueur) is not None

    @staticmethod
    def valider_format_date(date_str):
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False

    @staticmethod
    def prompt_joueur():
        nom = input("Nom du joueur: ")
        prenom = input("Prénom du joueur: ")
        while True:
            date_naissance = input("Date de naissance (JJ/MM/AAAA): ")
            if View.valider_format_date(date_naissance):
                break
            else:
                print("Format de date incorrect. Utilisez JJ/MM/AAAA")

        while True:
            id_joueur = input(
                "ID du joueur "
                "(2 lettres suivies de 5 chiffres, ex. TR45871): "
            )
            if View.validate_joueur_id(id_joueur):
                break
            else:
                print(
                    "L'ID du joueur doit contenir 2 lettres "
                    "suivies de 5 chiffres. Veuillez réessayer."
                )
        return Joueur(nom, prenom, date_naissance, id_joueur)

    @staticmethod
    def prompt_tournoi():
        nom_tournoi = input("Nom du tournoi: ")
        lieu = input("Lieu du tournoi: ")
        while True:
            date_debut = input("Date de début (JJ/MM/AAAA): ")
            if View.valider_format_date(date_debut):
                break
            else:
                print("Format de date incorrect. Utilisez JJ/MM/AAAA")
        while True:
            date_fin = input("Date de fin (JJ/MM/AAAA): ")
            if View.valider_format_date(date_fin):
                break
            else:
                print("Format de date incorrect. Utilisez JJ/MM/AAAA")
        id_tournoi = input("ID du tournoi: ")
        nombre_max_tours_str = input(
            "Nombre de tours maximum (4 par défaut) : "
        )
        nombre_max_tours = int(
            (nombre_max_tours_str) if nombre_max_tours_str else 4
        )
        description = input("Description du tournoi: ")
        return Tournoi(
            nom_tournoi, lieu, date_debut, date_fin, id_tournoi, 
            nombre_max_tours, description
        )

    @staticmethod
    def prompt_inscription_tournoi(tournois):
        print("\nSélectionner un tournoi pour inscrire un joueur:")
        for i, tournoi in enumerate(tournois):
            print(
                f"{i + 1}. {tournoi.nom_tournoi} à {tournoi.lieu}, "
                f"du {tournoi.date_debut} au {tournoi.date_fin}")
        choix = int(input("\nChoix: ")) - 1
        return tournois[choix]

    @staticmethod
    def prompt_selection_tournoi(tournois):
        print("\nSélectionner un tournoi pour voir les matchs et tours:")
        for i, tournoi in enumerate(tournois):
            print(
                f"{i + 1}. {tournoi.nom_tournoi} à {tournoi.lieu}, "
                f"du {tournoi.date_debut.strftime('%d/%m/%Y')} au "
                f"{tournoi.date_fin.strftime('%d/%m/%Y')}"
            )
        choix = int(input("\nChoix: ")) - 1
        if 0 <= choix < len(tournois):
            return tournois[choix]
        else:
            print("Choix invalide.")
            return None

    @staticmethod
    def prompt_choix_joueur(joueurs):
        print("1. Choisir un joueur existant")
        print("2. Ajouter un nouveau joueur\n")
        choix = int(input("Choix: "))
        if choix == 1:
            print("\nSélectionner un joueur:")
            for i, joueur in enumerate(joueurs):
                print(f"{i + 1}. {joueur.nom} {joueur.prenom}")
            choix_joueur = int(input("\nChoix: ")) - 1
            return joueurs[choix_joueur]
        elif choix == 2:
            return View.prompt_joueur()

    @staticmethod
    def afficher_tours_et_matchs(tournoi):
        print(f"\n\n--- Tournoi: {tournoi.nom_tournoi} --- \n")
        if tournoi.description:
            print(f"Description : {tournoi.description}\n")
        tournoi.classement_tournoi()
        if not tournoi.tours:
            print("\nAucun tour disponible.\n")
            return

        for index, tour in enumerate(tournoi.tours, start=1):
            print(f"\n\nTour {index}: \n\n")
            if not tour.matchs:
                print("  Aucun match prévu pour ce tour. \n")
                continue

            for match in tour.matchs:
                joueur1 = match.joueur1
                joueur2 = match.joueur2
                print(
                    f"  Match {tour.matchs.index(match) + 1}: "
                    f"{joueur1.prenom} {joueur1.nom} ({joueur1.id_joueur})   v"
                    f"s   ({joueur2.id_joueur}) {joueur2.prenom} {joueur2.nom}"
                )
                resultat = getattr(match, 'resultat', "0 - 0")
                if resultat not in ["0 - 0", None]:
                    print(f"    Résultat: {resultat} \n")
                else:
                    print("    Résultat: En attente \n\n")

    def afficher_tournois_disponibles(self, tournois):
        print("\nSélectionnez un tournoi pour modifier les résultats :")
        for i, tournoi in enumerate(tournois):
            print(
                f"{i + 1}. {tournoi.nom_tournoi} à {tournoi.lieu}, "
                f"du {tournoi.date_debut} au {tournoi.date_fin}"
            )
