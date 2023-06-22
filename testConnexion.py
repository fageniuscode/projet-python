import mysql.connector

# Se connecter à la base de données
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'passer@123',
    'database': 'banque'
}
# Établir la connexion
conn = mysql.connector.connect(**config)

# Créer un curseur
cursor = conn.cursor()

# Exemple de requête SELECT
cursor.execute("SELECT * FROM clients")

# Récupérer les résultats de la requête
results = cursor.fetchall()

# Parcourir les résultats
for row in results:
    # Traiter chaque ligne de résultat
    print(row)

# Fermer le curseur
cursor.close()

# Fermer la connexion à la base de données
conn.close()