import socket
import mysql.connector

# Configuration de la base de données MySQL
db_config = {
    'user': 'root',
    'password': 'passer@123',
    'host': 'localhost',
    'database': 'banque'
}

# Fonction pour exécuter une requête SELECT sur la base de données
def execute_select_query(query):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# Fonction pour exécuter une requête UPDATE ou INSERT sur la base de données
def execute_update_query(query):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

# Fonction pour gérer les requêtes des clients
def handle_request(client_socket):
    request = client_socket.recv(1024).decode()  # Recevoir la requête du client
    parts = request.split()  # Diviser la requête en parties
    response = ""

    if parts[0] == 'TESTPIN':
        account_number = int(parts[1])
        pin_code = parts[2]
        query = "SELECT * FROM compte WHERE idCompte = {} AND codePIN = '{}'".format(account_number, pin_code)
        result = execute_select_query(query)
        if result:
            response = "TESTPIN OK"
        else:
            response = "TESTPIN NOK"

    elif parts[0] == 'RETRAIT':
        account_number = int(parts[1])
        amount = float(parts[2])
        query = "SELECT sole FROM compte WHERE idCompte = {}".format(account_number)
        result = execute_select_query(query)
        if result:
            current_balance = float(result[0][0])
            if current_balance >= amount:
                new_balance = current_balance - amount
                query = "UPDATE compte SET sole = {} WHERE idCompte = {}".format(new_balance, account_number)
                execute_update_query(query)
                response = "RETRAIT OK"
            else:
                response = "RETRAIT NOK"
        else:
            response = "ERROPERATION"

    elif parts[0] == 'DEPOT':
        account_number = int(parts[1])
        amount = float(parts[2])
        query = "SELECT sole FROM compte WHERE idCompte = {}".format(account_number)
        result = execute_select_query(query)
        if result:
            current_balance = float(result[0][0])
            new_balance = current_balance + amount
            query = "UPDATE compte SET sole = {} WHERE idCompte = {}".format(new_balance, account_number)
            execute_update_query(query)
            response = "DEPOT OK"
        else:
            response = "ERROPERATION"
    
    elif parts[0] == 'TRANSFERT':
        source_account_number = int(parts[1])
        destination_account_number = int(parts[2])
        amount = float(parts[3])

        # Vérifier le solde du compte source
        query = "SELECT sole FROM compte WHERE idCompte = {}".format(source_account_number)
        result = execute_select_query(query)
        if not result:
            response = "ERROPERATION"
            client_socket.send(response.encode())
            client_socket.close()
            return

        source_balance = float(result[0][0])
        if source_balance < amount:
            response = "TRANSFERT NOK"
        else:
            # Effectuer le transfert depuis le compte source
            new_source_balance = source_balance - amount
            query = "UPDATE compte SET sole = {} WHERE idCompte = {}".format(new_source_balance, source_account_number)
            execute_update_query(query)

            # Vérifier l'existence du compte destination
            query = "SELECT * FROM compte WHERE idCompte = {}".format(destination_account_number)
            result = execute_select_query(query)
            if not result:
                response = "ERROPERATION"
                client_socket.send(response.encode())
                client_socket.close()
                return

            # Effectuer le transfert vers le compte destination
            query = "SELECT sole FROM compte WHERE idCompte = {}".format(destination_account_number)
            result = execute_select_query(query)
            destination_balance = float(result[0][0])
            new_destination_balance = destination_balance + amount
            query = "UPDATE compte SET sole = {} WHERE idCompte = {}".format(new_destination_balance, destination_account_number)
            execute_update_query(query)

            response = "TRANSFERT OK"
    
    elif parts[0] == 'SOLDE':
        account_number = int(parts[1])

        # Vérifier l'existence du compte
        query = "SELECT * FROM compte WHERE idCompte = {}".format(account_number)
        result = execute_select_query(query)
        if not result:
            response = "ERROPERATION"
        else:
            query = "SELECT sole FROM compte WHERE idCompte = {}".format(account_number)
            result = execute_select_query(query)
            balance = float(result[0][0])
            response = "SOLDE {}".format(balance)

    elif parts[0] == 'HISTORIQUE':
        account_number = int(parts[1])

        # Vérifier l'existence du compte
        query = "SELECT * FROM compte WHERE idCompte = {}".format(account_number)
        result = execute_select_query(query)
        if not result:
            response = "ERROPERATION"
        else:
            query = "SELECT * FROM operations WHERE idCompte = {} ORDER BY dateOperation DESC LIMIT 10".format(account_number)
            result = execute_select_query(query)

            if result:
                operations_csv = ""
                for row in result:
                    date_operation = row[1]
                    libelle_operation = row[3]
                    montant = row[4]
                    operations_csv += "{},{},{}\n".format(date_operation, libelle_operation, montant)
                response = "HISTORIQUE {}".format(operations_csv)
            else:
                response = "HISTORIQUE "
                
    # Gérer d'autres types de requêtes ici (TRANSFERT, SOLDE, HISTORIQUE, etc.)

    else:
        response = "ERROPERATION"

    client_socket.send(response.encode())  # Envoyer la réponse au client
    client_socket.close()

# Programme principal
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 50000))
server_socket.listen(5)

print("Le serveur central de la banque écoute sur le port 50000...")

# Partie menu pour l'interface utilisateur
while True:
    print("\n---- Menu ----")
    print("1. Vérifier le code PIN")
    print("2. Effectuer un retrait")
    print("3. Effectuer un dépôt")
    print("4. Effectuer un transfert")
    print("5. Vérifier le solde")
    print("6. Afficher l'historique")
    print("0. Quitter")

    choice = input("Veuillez choisir une opération : ")

    if choice == '1':
        account_number = input("Numéro de compte : ")
        pin_code = input("Code PIN : ")
        request = "TESTPIN {} {}".format(account_number, pin_code)
        print("Requête :", request)
        # Envoyer la requête au serveur et afficher la réponse
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 50000))
        client_socket.send(request.encode())
        response = client_socket.recv(1024).decode()
        print("Réponse :", response)
        client_socket.close()

    elif choice == '2':
        account_number = input("Numéro de compte : ")
        amount = input("Montant : ")
        request = "RETRAIT {} {}".format(account_number, amount)
        print("Requête :", request)
        # Envoyer la requête au serveur et afficher la réponse
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 50000))
        client_socket.send(request.encode())
        response = client_socket.recv(1024).decode()
        print("Réponse :", response)
        client_socket.close()

    elif choice == '3':
        account_number = input("Numéro de compte : ")
        amount = input("Montant : ")
        request = "DEPOT {} {}".format(account_number, amount)
        print("Requête :", request)
        # Envoyer la requête au serveur et afficher la réponse
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 50000))
        client_socket.send(request.encode())
        response = client_socket.recv(1024).decode()
        print("Réponse :", response)
        client_socket.close()

    elif choice == '4':
        source_account_number = input("Numéro de compte source : ")
        destination_account_number = input("Numéro de compte destination : ")
        amount = input("Montant : ")
        request = "TRANSFERT {} {} {}".format(source_account_number, destination_account_number, amount)
        print("Requête :", request)
        # Envoyer la requête au serveur et afficher la réponse
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 50000))
        client_socket.send(request.encode())
        response = client_socket.recv(1024).decode()
        print("Réponse :", response)
        client_socket.close()

    elif choice == '5':
        account_number = input("Numéro de compte : ")
        request = "SOLDE {}".format(account_number)
        print("Requête :", request)
        # Envoyer la requête au serveur et afficher la réponse
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 50000))
        client_socket.send(request.encode())
        response = client_socket.recv(1024).decode()
        print("Réponse :", response)
        client_socket.close()

    elif choice == '6':
        account_number = input("Numéro de compte : ")
        request = "HISTORIQUE {}".format(account_number)
        print("Requête :", request)
        # Envoyer la requête au serveur et afficher la réponse
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 50000))
        client_socket.send(request.encode())
        response = client_socket.recv(1024).decode()
        print("Réponse :", response)
        client_socket.close()

    elif choice == '0':
        print("Au revoir !")
        break

    else:
        print("Opération invalide. Veuillez choisir une opération valide.")

while True:
    client_socket, addr = server_socket.accept()
    print("Connexion acceptée depuis :", addr)
    handle_request(client_socket)

