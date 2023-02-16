import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('client_connections.db')
c = conn.cursor()

# Exécution de la requête SQL pour compter le nombre de lignes dans la table "client_connections"
c.execute('SELECT COUNT(*) FROM emails WHERE connection_ip=?', ("192.168.1.5".encode(),))
resultat = c.fetchone()

# Affichage du nombre de lignes
print('Il y a', resultat[0], 'lignes dans la table "client_connections" avec l\'adresse IP "192.168.1.5".')

# Exécution de la requête SQL pour afficher toutes les lignes de la table "client_connections"
c.execute('SELECT * FROM emails')
rows = c.fetchall()

# Affichage des lignes
print('Contenu de la table "client_connections":')
for row in rows:
    print("\'",row,"\'")

# Fermeture de la connexion à la base de données
conn.close()
