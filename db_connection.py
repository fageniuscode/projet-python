import mysql.connector

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='utilisateur',
                password='motdepasse',
                database='basededonnees'
            )
            print("Connexion à la base de données réussie !")
        except mysql.connector.Error as error:
            print(f"Erreur lors de la connexion à la base de données : {error}")

    # Autres méthodes et opérations sur la base de données
