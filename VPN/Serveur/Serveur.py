###################################################################################################
#------------------------------------------LIBRAIRIES---------------------------------------------#
###################################################################################################
import hashlib
from logging import Manager
from multiprocessing import Process
import os
import pickle
import random
import socket
import sqlite3
import struct
import time
from signal import signal, SIGPIPE, SIG_DFL
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

signal(SIGPIPE,SIG_DFL)

#?##################################################################################################
#?-------------------------------------------FONCTIONS---------------------------------------------#
#?##################################################################################################
#* Cette fonction permet de convertir une chaine binaire en entier et retourne cet entier
#* Paramètre : binary = chaine binaire à convertir
def binary2int(binary):
    if binary.isnumeric():
        binary = int(binary)
        int_val, i, n = 0,0,0
        while(binary != 0):
            a = binary % 10
            int_val = int_val + a * pow(2,i)
            binary = binary//10
            i += 1
        return int_val

#* Cette fonction permet de convertir un entier en une chaine binaire et retourne cette chaine
#* Paramètre : n = entier à convertir 
def int2binary(n):
    if n == 0: 
        return '0'
    res = ''
    while n != 0: n, res = n >> 1, repr(n & 1) + res
    return res  

#* Cette fonction permet de chiffrer des données avec l'algorithme AES
#* Paramètres : message = texte à chiffrer
#*              key = clé à utiliser pour le chiffrement
#! La clé de chiffrement doit être d'une taille de 16 caractères
def encrypt(message,key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return (cipher.nonce, tag, ciphertext)

#* Cette fonction permet d'envoyer des données à un client en les chiffrants
#* Paramètres : vpn_client = socket de connexion du client à qui sont envoyées les données
#*              message = texte à envoyer (pas encore chiffré)
#*              key = clé à utiliser pour le chiffrement
def send_data(vpn_client,message,key):
    
    # Chiffrement du message
    nonce, tag, ciphertext = encrypt(message,key)
    
    # Hachage en SHA-256
    hash_object = hashlib.sha256(message)

    # Convertion du hash en hexadécimal
    hex_dig = hash_object.hexdigest()
    
    # Stockage des données à envoyer dans un objet pour faciliter l'échange
    data_obj = {"nonce":nonce, "tag":tag, "msg":ciphertext,"hash":hex_dig}
    
    # Serialization de l'objet qui contient les info à envoyer
    data_serialized_obj = pickle.dumps(data_obj,protocol=4)

    # Envoie
    vpn_client.sendall(data_serialized_obj)
    
#* Cette fonction permet de déchiffrer une donnée chiffré par la fonction "encrypt()"
#* Paramètres : key = clé partagé pour le chiffrement
#*              nonce, tag = nonce et tag utilisés lors du chiffrement des données
#*              ciphertext = texte à déchiffrer
def decrypt(key, nonce, tag, ciphertext):
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    msg = cipher.decrypt_and_verify(ciphertext, tag)
    return msg

#* Cette fonction permet de recevoir des données et de les déchiffrer
#* Paramètres : client_connection = socket de connexion du client duquel sont reçues les données
#*              key = clé à utiliser pour le déchiffrement
def recv_message(client_connection,key):
    
    # Reception du paquet
    data_obj = client_connection.recv(1024)
    
    # Déserialization du paquet
    data_obj_deserialized = pickle.loads(data_obj)
    
    # Récupération des données dans différentes variables
    nonce = data_obj_deserialized["nonce"]
    tag = data_obj_deserialized["tag"]
    msg = data_obj_deserialized["msg"]
    hash = data_obj_deserialized["hash"]
    
    # Déchiffrement du message
    msg = decrypt(key,nonce,tag,msg)
    
    # Hachage en SHA-256
    hash_object = hashlib.sha256(msg)

    # Convertion du hash en hexadécimal
    hex_dig = hash_object.hexdigest()
    
    #! Test d'intégrité du hash
    if hex_dig != hash:
        print("Problème d'intégrité ! Les données ont pu être modifié au cours du transfère")
    return msg

#* Cette fonction permet de calculer la clé partagé 
#* Paramètres : server_private_key = clé privé du serveur
#*              client_public_key = clé publique du client
#*              p, g = paramètres de Diffie Hellman
def keyCalculated(server_private_key,client_public_key,p,g):
    return client_public_key ** server_private_key % p

#* Cette fonction permet la reception de fichier plus ou moins lourds
#* Paramètre : key_partaged = clé à utiliser pour le déchiffrement
def ReceptionFile(key_partaged):
    accepte = "non"
    num = 0
    taille_bdd = 0
    pourcent = 0
    flag = 0
    signal = "ok"
    global id_file
    
    # Envoi d'un premier signal avant reception des paquets
    send_data(client_connection,signal.encode(),key_partaged)
    
    # Reception du premier paquet
    ip = recv_message(client_connection,key_partaged)
    
    # Tant que la connection avec le client est établie
    while (client_connection.connect):
        recu = ""
        
        # Recpetion du paquet    
        recu = recv_message(client_connection,key_partaged)
        print(recu)
        # Test la bonne reception du paquet
        if not recu : return False
        
        # Test grâce au flag si le premier paquet correspond aux informations du fichier
        #! Chaque envoi de fichier doit commencer par un premier paquet qui contient
        #! le chemin relatif et la taille du fichier qui va être envoyé
        if accepte == "non": 
                tmp = recu.decode()
                # Stockage du chemin relatif du fichier
                nomFich = tmp.split("NAME ")[1]
                # Stockage du chemin relatif du fichier
                nomFich = nomFich.split("OCTETS ")[0]
                taille = tmp.split("OCTETS ")[1]
                #print ("\n---> Fichier '" + nomFich + "' [" + taille + " Ko]")
                
                # Récupération du nom du fichier via le chemin relatif reçu 
                nom_fichier = os.path.basename(nomFich)
                
                # Récupération du nombre de fichier déjà présent dans la BDD
                # donc reçu précédement
                c.execute("SELECT COUNT(*) FROM FICHIERS",)
                id = c.fetchone()[0]
                
                # Stockage dans un premier temps des informations du fichier dans la BDD
                c.execute("INSERT INTO FICHIERS (id,source_ip,destinataire_ip,nom_file,file,recu) VALUES (?,?,?,?,?,?)", 
                        (id+1,client_address[0], ip,nom_fichier,"",False))
                conn.commit() 
                
                # Changement du flag
                accepte = "o"                             

                signal = "GO"
                
                # Envoi du signal pour signaler la bonne reception du paquet 
                send_data(client_connection,signal.encode(),key_partaged)
                #SomUpload = addDataLenght(recu,SomUpload)
                print (time.strftime("\n---> [%H:%M] réception du fichier en cours veuillez patienter..."))
                
                # Ouverture du fichier dans lequel on va écrire les paquets reçus
                f = open("RECU.txt", "wb")
                
                # Changement du flag
                accepte = "oui"
                
                # Conversion de la taille en octets pour le %
                taille = float(taille) * 1024 
               
        # Si on a recu "bye" le transfer est termine
        elif recu.decode() == "bye": 
            print (" -> 100%" ) 
            f.close()
            print (time.strftime("\n---> Le %d/%m a %H:%M réception du fichier termine !"))
            break
        
        # Sinon on ecrit le paquet dans le fichier
        else: 
            f.write(recu)
            taille_bdd = taille_bdd + len(recu)
            
            
            # Récupération de l'ancien contenu de la colonne "file"
            #! Pour stocker le fichier dans la BDD il faut modifier le contenu de l'attribut "file" 
            #! à chaque réception d'un nouveau paquet auquelle on va concatener le paquet reçu et 
            #! modifier le contenu dans la BDD
            
            c.execute("SELECT file FROM FICHIERS WHERE id=? AND source_ip=? AND destinataire_ip=? AND nom_file=?", (id+1,client_address[0], ip,nom_fichier))
            ancien_contenu = c.fetchone()[0]
            
            # Concaténation du texte à la colonne "file"
            nouveau_contenu = ancien_contenu + recu.decode()

            # Mis à jour de la colonne "file"
            c.execute("UPDATE FICHIERS SET file=? WHERE id=?  AND source_ip=? AND destinataire_ip=? AND nom_file=?", (nouveau_contenu, id+1,client_address[0], ip,nom_fichier))
            conn.commit()
            
            signal="ok"
            send_data(client_connection,signal.encode(),key_partaged)
            
            if taille > 1024: # Si la taille est plus grande que 1024 on s'occupe du %

                # Condition pour afficher le % du transfert :
                if pourcent == 0 and num > taille / 100 * 10 and num < taille / 100 * 20:
                    print (" -> 10%")
                    pourcent = 1
                elif pourcent == 1 and num > taille / 100 * 20 and num < taille / 100 * 30:
                    print (" -> 20%")
                    pourcent = 2
                elif pourcent < 3 and num > taille / 100 * 30 and num < taille / 100 * 40:
                    print (" -> 30%")
                    pourcent = 3
                elif pourcent < 4 and num > taille / 100 * 40 and num < taille / 100 * 50:
                    print (" -> 40%")
                    pourcent = 4
                elif pourcent < 5 and num > taille / 100 * 50 and num < taille / 100 * 60:
                    print (" -> 50%")
                    pourcent = 5
                elif pourcent < 6 and num > taille / 100 * 60 and num < taille / 100 * 70:
                    print (" -> 60%")
                    pourcent = 6
                elif pourcent < 7 and num > taille / 100 * 70 and num < taille / 100 * 80:
                    print (" -> 70%")
                    pourcent = 7
                elif pourcent < 8 and num > taille / 100 * 80 and num < taille / 100 * 90:
                    print (" -> 80%")
                    pourcent = 8
                elif pourcent < 9 and num > taille / 100 * 90 and num < taille / 100 * 100:
                    print (" -> 90%" )                   
                    pourcent = 9
                    
                num = num + 1024
    print("FIN : ",taille_bdd)
    return True
    
#* Cette fonction permet d'ajouter la taille des données échanger à la somme totale sur la journée
#TODO (nécessaire pour l'histogramme)
#* Paramètres : data = donnée reçue / envoyé
#*              somme = somme des échanges de données du jour
def addDataLenght(data,somme):
    data = data.decode()
    octets = len(data)
    somme = somme + octets 
    return somme

#* Cette fonction permet de générer un nombre premier semi-aléatoirement
#TODO (nécessaire pour la génération des paramètres de Diffie-Hellman)
def generate_random_prime():
    while True:
        n = random.randint(2, 2**256)
        if all(n % i != 0 for i in range(2, int(n ** (1/2)) + 1)):
            return n

#* Cette fonction permet de générer les paramètre de Diffie-Hellman
def ParametersGenerator():
    p = generate_random_prime()
    g = random.randint(2, 2**256)
    return (p,g)

#* Cette fonction permet d'échanger les clés selon le protocole de Diffie-Hellman
#* Paramètres : client_connection = socket de connexion du client
def DiffieHullamKeyExchange(client_connection):
    
    # Génération des paramètres de Diffie-Hellman
    # Déclaration du nombre premier
    p = 13

    # Déclaration de la racine primitive modulo p
    g = 5

    # Déclaration de la variable paramètre
    parameters = (p,g)

    # Conversion du tuble de paramètre en binaire 
    parameters_bytes = struct.pack('!2i',*parameters)

    # Choix d'une clé privé aléatoire entre 2 et 10
    server_private_key = random.randint(2,10)

    # Calcul de la clé publique de Diffie-Hellman pour le serveur
    server_public_key = (g ** server_private_key) % p 

    # Serialization de la clé
    server_public_key_binary = str(int2binary(server_public_key)).encode()
        
    # Envoi des paramètres au client 
    client_connection.send(parameters_bytes)
    print("j'ai envoyé")

    # Réception de la clé public du client
    client_public_key_byte= client_connection.recv(1024)
    #SomDownload = addDataLenght(client_public_key_byte,SomDownload)

    # Déserialisation de la clé publique du client
    client_public_key_binary = client_public_key_byte.decode()
    client_public_key = binary2int(client_public_key_binary)

    # Envoie de la clé publique du serveur au client
    client_connection.sendall(server_public_key_binary)
    #SomUpload = addDataLenght(server_public_key_binary,SomUpload)

    # Calcul de la clé paratagée
    key_partaged = keyCalculated(server_private_key,client_public_key,p,g)
    print("\n-----> Les clés ont bien été échangées et stockées !")
    
    # Hashage de la clé pour correspondre au format requis pour le chiffrement / déchiffrement
    # avec l'AES
    h = hashlib.sha256(str(key_partaged).encode())
    key_16 = h.hexdigest()[:16]
    
    return key_16.encode()

#* Cette fonction permet d'envoi un fichier plus ou moins lourds
#* Paramètres : name_file = nom du fichier à envoyer 
#*              file = fichier à envoyer
#*              ip = adresse ip du client à qui envoyer le fichier
def sendFile(name_file,file,ip,key_partaged):  
    
    # Envoie d'un premier signal pour annoncé que la fonction est lancé
    signal = "send file"
    send_data(client_connection,signal.encode(),key_partaged)
    
    # Envoie d'un signal pour me dire que le client est prêt à recevoir les paquets
    rep = recv_message(client_connection,key_partaged)
    
    # Définissions de la taille du fichier
    octets = os.path.getsize(file) / 870
    
    # Vérifiaction des informations
    print ("\n---> Fichier à envoyer : '" + name_file + "' [" + str(octets) + " Ko]")
    tmp = "NAME " + name_file + "OCTETS " + str(octets)
    
    # Envoie des informations du fichiers qui va être envoyé
    send_data(client_connection,tmp.encode(),key_partaged)
    
    while (client_connection.connect):
        tmp = recv_message(client_connection,key_partaged)
        recu = tmp.decode() 
        if not recu : return False

        # Si le serveur accepte on envoi le fichier
        if recu == "GO": 
            
            num = 0
            pourcent = 0
            octets = octets * 870 
            fich = open(file, "rb")
            remaining_data = octets
            
            # Si le fichier est plus lourd que 1024 on l'envoi par paquet
            if octets > 870:	
                for i in range(int(octets / 870)+1):    
                    if remaining_data > 870:
                        
                        # on se deplace par rapport au numero de caractere (de 1024 a 1024 octets)
                        fich.seek(num, 0) 
                        
                        # Lecture du fichier en 1024 octets 
                        donnees = fich.read(870)         
                        
                        # Envoie des données
                        send_data(client_connection,donnees.decode('utf-8', errors='ignore').encode('utf-8'),key_partaged)
                        
                        # Reception du signal pour continuer
                        recv_message(client_connection,key_partaged)
                        
                        num = num + 870
                        remaining_data -= 870
                
                        # Condition pour afficher le % du transfert (pas trouve mieu) :
                        if pourcent == 0 and num > octets / 100 * 10 and num < octets / 100 * 20:
                            print (" -> 10%")
                            pourcent = 1
                        elif pourcent == 1 and num > octets / 100 * 20 and num < octets / 100 * 30:
                            print (" -> 20%")
                            pourcent = 2
                        elif pourcent < 3 and num > octets / 100 * 30 and num < octets / 100 * 40:
                            print (" -> 30%")
                            pourcent = 3
                        elif pourcent < 4 and num > octets / 100 * 40 and num < octets / 100 * 50:
                            print (" -> 40%")
                            pourcent = 4
                        elif pourcent < 5 and num > octets / 100 * 50 and num < octets / 100 * 60:
                            print (" -> 50%")
                            pourcent = 5
                        elif pourcent < 6 and num > octets / 100 * 60 and num < octets / 100 * 70:
                            print (" -> 60%")
                            pourcent = 6
                        elif pourcent < 7 and num > octets / 100 * 70 and num < octets / 100 * 80:
                            print (" -> 70%")
                            pourcent = 7
                        elif pourcent < 8 and num > octets / 100 * 80 and num < octets / 100 * 90:
                            print (" -> 80%")
                            pourcent = 8
                        elif pourcent < 9 and num > octets / 100 * 90 and num < octets / 100 * 100:
                            print (" -> 90%")                    
                            pourcent = 9
                    else: # Sinon on arrive à la fin du fichier
                        # Lecture dans le fichier
                        donnees = fich.read(int(remaining_data))
                        
                        # Envoie des données au client
                        send_data(client_connection,donnees,key_partaged)
                        
                        # Reception du signal pour continuer
                        rep = recv_message(client_connection,key_partaged)
                        print (" -> 100%")  
                        break  
                        
            else: # Sinon on envoi tous d'un coup
                # Lecture dans le fichier
                donnees = fich.read()
                
                # Envoi des données au client
                send_data(client_connection,donnees,key_partaged)
                
                # Reception du signal pour continuer
                recv_message(client_connection,key_partaged)

            fich.close()
            signal2 = "bye"
            
            # Envoi du signal pour informer que l'envoi du fichier est terminé
            send_data(client_connection,signal2.encode(),key_partaged)
            
            return True
        else: # Sinon problème de synchronisation
            print (time.strftime("\n--->[%H:%M] transfert annulé."))
            return "BYE"

def Signature(key_partaged):
    # Générer une paire de clés RSA
    key = RSA.generate(2048)

    # Message à signer
    message = b"Hello, world!"

    # Hash du message
    h = SHA256.new(message)

    # Signer le hash avec la clé privée
    signature = pkcs1_15.new(key).sign(h)
    
    # Envoie de la signature et de la clé
    send_data(client_connection,signature,key_partaged)
    
    # Reception d'un signal pour continuer
    recv_message(client_connection,key_partaged)
    
    # Convertir la clé publique en bytes
    keypub_bytes = key.publickey().export_key()

    # Envoie de la clé publique pour déchiffrer
    send_data(client_connection, keypub_bytes, key_partaged)

def verif_Signature(key_partaged):
    # Message à signer
    message = b"Hello, world!"

    # Hash du message
    h = SHA256.new(message)
    
    signature = recv_message(client_connection,key_partaged)
    signal = "ok signature"
    send_data(client_connection,signal.encode(),key_partaged)
    keypub_bytes = recv_message(client_connection,key_partaged)
    keypub = RSA.import_key(keypub_bytes)
    print(keypub)
    # Vérifier la signature avec la clé publique
    try:
        pkcs1_15.new(keypub).verify(h, signature)
        print("La signature est valide.")
        return True
    except (ValueError, TypeError):
        print("La signature est invalide.")
        return False

#?##################################################################################################
#?------------------------------------MISE EN PLACE DU SOCKET--------------------------------------#
#?##################################################################################################

# Création du socket 
vpn_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = ('',24081)

# Liaison du socket à une adresse IP et un port 
vpn_server.bind((host,port))

# Mise en écoute du socket 
vpn_server.listen()
print("\n--------->Ouverture du serveur...")
        
#?##############################################################################################################
#?--------------------------------------FONCTION RUN DES SOUS-PROCESSUS----------------------------------------#
#?##############################################################################################################

#* Cette fonction est exécuter automatiquement à chaque connection d'un client et permet entre-autre
#* de gérer toutes les interactions entre le client et le serveur
#* Paramètres : client_connection = socket de connection du client
def client_handler(client_connection):
    global client_count
    global clients_connected
    global client_address_list
    global id_mail
    global id_file
    SomUpload = 0
    SomDownload = 0
    # Création du tableau qui contiendra les données du trafic réseau
    #tab = []
    #tab
    # Récupère la date de connexion du client
    #date = int(time.strftime("%Y%m%d"))
    #print(date,type(date))
    #tuple = (date,SomUpload,SomDownload)
    #tab.append(tuple)
    #print(tab)

    client_count += 1
    clients_connected.append(client_connection)
    print("\nLe thread du client : ",client_connection.getpeername()," est lancé !")
    
    # Echange des clés de Diffie-Hullman
    key_partaged = DiffieHullamKeyExchange(client_connection)
    
    # Signature pour vérifier l'authenticité de la source
    Signature(key_partaged)
    rep = verif_Signature(key_partaged)
    if rep == False:
        print("Erreur, la signature du client n'est pas valide")
        return False
    
    while (client_connection.fileno() != -1):
        
        # Reception d'un signal 
        recu = recv_message(client_connection,key_partaged)
        
        if (recu.decode() == "send file"): # Le client veut envoyer un fichier
            id_file = id_file + 1
            rep= ReceptionFile(key_partaged)
            if rep == False: # Execution de la fonction ReceptionFile() échoué
                print("\n-----> Le client ",client_connection.getpeername()," s'est déconnecté !")
                client_count -= 1
                clients_connected.remove(client_connection)
                break
            
        if (recu.decode() == "speedtest upload"): # Le client veut tester l'échange de donnée en upload
            signal = "GO"
            send_data(client_connection,signal.encode(),key_partaged)
            # Reception de paquet 50 fois 
            #! Le calcul de la vitesse en Mbit/s se fait côté client
            for i in range(50):
                if recu.decode() == "quit":
                    break
                signal = "OK"
                data = recv_message(client_connection,key_partaged)
                send_data(client_connection,signal.encode(),key_partaged)
            
        if (recu.decode() == "speedtest download"):# Le client veut tester l'échange de donnée en download
            file = open("sauvegarde.txt","rb")
            # Envoi de paquet 50 fois 
            #! Le calcul de la vitesse en Mbit/s se fait côté client
            for i in range(50):
                donnees = file.read(870) # Lecture du fichier en 1024 octets  
                send_data(client_connection,donnees,key_partaged)
                recu = recv_message(client_connection,key_partaged)
                
        if (recu.decode() == "reception msg"): # Le client veut envoyer un message
            signal = "ok"
            
            # Envoi d'un signal pour continuer
            send_data(client_connection,signal.encode(),key_partaged)
            
            # Reception du destinataire (celui qui va revoir le message)
            destinataire = recv_message(client_connection,key_partaged)
            
            # Envoi d'un signal pour continuer
            send_data(client_connection,signal.encode(),key_partaged)
            
            # Reception du sujet du mail
            subject = recv_message(client_connection,key_partaged)
            
            # Envoi d'un signal pour continuer
            send_data(client_connection,signal.encode(),key_partaged)
            
            # Reception du corps du mail
            text = recv_message(client_connection,key_partaged)
            
            # Envoi d'un signal pour continuer
            send_data(client_connection,signal.encode(),key_partaged)
            
            # Stockage du mails et de ses informations de la BDD
            id_mail +=1
            c.execute("INSERT INTO emails (id,connection_ip, source,subject,text,recu) VALUES (?,?, ?,?,?,?)", (id_mail,destinataire.decode(), client_address[0],subject.decode(),text.decode(),False))
            conn.commit()

        if recu.decode() == "recv msg ok": # Le client veut recevoir ses messages (s'il en a)
            
            # Récuperation du nombre de messages qui doivent être envoyé au client
            c.execute("SELECT COUNT(*) FROM emails WHERE connection_ip = ? and recu = ?", (client_address[0],False))
            result = c.fetchone()
            
            # Envoie du nombre de message
            nb_msg = str(result[0])
            send_data(client_connection,nb_msg.encode(),key_partaged)
            
            # Reception d'un signal pour continuer
            rep = recv_message(client_connection,key_partaged)
            
            if rep.decode() == "yes":
                # Récuperation des mails qui doivent être envoyés
                c.execute("SELECT * FROM emails WHERE connection_ip IN (SELECT ip FROM connections WHERE ip = ?) and recu = ?", (client_address[0],False))
                rows = c.fetchall()
                for row in rows: # Pour chaque ligne (chaque fichier)
                    # Stockage des différents éléments
                    source = row[2]
                    subject = row[3]
                    text = row[4]
                    
                    # Modification du statut du message qui passe à "message reçu"
                    c.execute("UPDATE emails SET recu=? WHERE id=?", (True, row[0]))
                    conn.commit()
                    
                    # Envoi de la source
                    send_data(client_connection,source.encode(),key_partaged)
                    
                    # Reception d'un signal pour continuer
                    rep = recv_message(client_connection,key_partaged)
                    
                    if (rep.decode() == "ok"):
                        # Envoi du sujet 
                        send_data(client_connection,subject.encode(),key_partaged)
                        # Reception d'un signal pour continuer
                        rep = recv_message(client_connection,key_partaged)
                    
                    if (rep.decode() == "ok"):
                        # Envoi du texte
                        send_data(client_connection,text.encode(),key_partaged)
                        # Reception d'un signal pour continuer
                        rep = recv_message(client_connection,key_partaged)
                        
        if recu.decode() == "recv file ok": # Le client souhaite recevoir les fichiers en attentes 
            # Récupération de l'adresse IP du client
            ip = client_address[0]
            
            # Récupération du nombre de fichiers en attentes
            c.execute("SELECT COUNT(*) FROM fichiers WHERE destinataire_ip= ? and recu=?", (ip.encode(),False))
            nb_file = c.fetchall()[0][0]
            
            # Envoi le nombre de fichiers en attentes
            send_data(client_connection,str(nb_file).encode(),key_partaged)
            
            # Reception d'un signal pour continuer
            rep = recv_message(client_connection,key_partaged)
            
            if rep.decode() == "oui":
                # Recupération des informations et des fichiers stockés dans la BDD
                c.execute('SELECT * FROM fichiers WHERE recu=?',(False,))
                rows = c.fetchall() 
                
                for row in rows: # Pour chaque fichier à envoyer
                    file = open("fichier_tmp.txt", "w")
                    # Ecriture du contenu de la BDD dans un fichier temporaire
                    file.write(row[4])
                    file.close()
                    
                    # Envoi du fichier 
                    sendFile(row[3],"fichier_tmp.txt",client_address[0],key_partaged)
                    
                    # Mise à jour du statut du fichier dans la BDD (reçu = True)
                    c.execute("UPDATE FICHIERS SET recu=? WHERE id=?", (True, row[0]))
                    conn.commit()
            
        if (recu.decode() == "exit"): # Le client s'est déconnecté
            print("\n-----> Le client ",client_connection.getpeername()," s'est déconnecté !")
            client_count -= 1
            clients_connected.remove(client_connection)
            return 0
        
    
#?##############################################################################################################
#?---------------------------------------BDD ET VARIABLES GLOBALES---------------------------------------------#
#?##############################################################################################################

print("\n--------->Serveur ouvert!")
# Variables pour compter les clients connectés
client_count = 0
clients_connected = []
processus_list = []
client_address_list = []
id_mail = 0 
id_file = 0

# Connection à la BDD ou création de la BDD
conn = sqlite3.connect('client_connections.db')
c = conn.cursor()

# Création des différentes tables de la BDD
c.execute("CREATE TABLE IF NOT EXISTS connections (ip text, port integer)")
c.execute('''CREATE TABLE IF NOT EXISTS emails (id integer,
                                                connection_ip text, 
                                                source text, 
                                                subject text, 
                                                text text, 
                                                recu boolean,
                                                FOREIGN KEY(connection_ip) REFERENCES connections(ip))''')
c.execute('''CREATE TABLE IF NOT EXISTS fichiers (id integer,
                                                    source_ip text,
                                                    destinataire_ip text,
                                                    nom_file text,
                                                    file text,
                                                    recu boolean)''')

#?##############################################################################################################
#?-----------------------------------------------MAIN----------------------------------------------------------#
#?##############################################################################################################

while(True):
    client_connection, client_address = vpn_server.accept()
    
    # Vérification des adresses IP
    if client_address[0] == "77.130.108.126" or client_address[0] == "127.0.0.1":
        client_found = False
        
        #! On va chercher à savoir si le client est connu dans la BDD 
        #! (signifie qu'il s'est déjà connecté au serveur)
        for i, ca in enumerate(client_address_list):
            if ca[0] == client_address[0]: #* Le client est connu
                client_address_list[i] = client_address
                client_found = True
                #* Lancement du sous-processus pour le client avec les informations connues
                client_process = Process(target=client_handler, args=(client_connection,))
                client_process.start()
                break
        if not client_found: #* Le client ne s'est jamais connecté (première connection)
            client_address_list.append(client_address)
            #* Lancement du sous-processus pour le client
            client_process = Process(target=client_handler, args=(client_connection,))
            processus_list.append(client_process)
            client_process.start()
            print(f'\n--------->Connexion de {client_address}')
            c.execute("INSERT INTO connections (ip, port) VALUES (?, ?)", (client_address[0], client_address[1]))
            conn.commit()
        else: #* Le client s"est déjà connecté et est inscrit dans la BDD
            print(f'\n--------->Connexion existante de {client_address} mise à jour')
            #* Mise à jour du port de connection du client
            c.execute("UPDATE connections SET port=? WHERE ip=?", (client_address[1], client_address[0]))
            conn.commit()
    else: #* L'adresse IP n'est pas autorisée
        print(f'\n--------->Refus de la connexion de {client_address}')
        client_connection.close()
    
conn.close()
vpn_server.close()