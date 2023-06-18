import mysql.connector

# Se connecter à la base de données
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="passer@123",
    database="banque"
)

# Créer un curseur
cursor = cnx.cursor()

# Définir le chemin vers le fichier CSV
fichier_csv = "C:/Users/ibrah/OneDrive/Bureau/M2GL/Semestre02/data/client.csv"

# Définir le nom de la table cible
nom_table = "clients"

# Définir les options d'importation
options_import = """
    FIELDS TERMINATED BY ',' 
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS
"""

# Créer la requête SQL pour l'importation
requete_import = f"""
    LOAD DATA LOCAL INFILE '{fichier_csv}'
    INTO TABLE {nom_table}
    {options_import}
"""

# Exécuter la requête
cursor.execute(requete_import)

# Valider les modifications
cnx.commit()

# Fermer le curseur et la connexion
cursor.close()
cnx.close()
