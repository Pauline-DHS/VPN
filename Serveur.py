# Génération d'une clé de chiffrement partagée avec Diffie-Hellman
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

signal(SIGPIPE,SIG_DFL)

#-----------------------------------FONCTIONS------------------------------------#
#j'ai mis un commentaire
def binary2int(binary):
    if binary.isnumeric():
        binary = int(binary)
        int_val, i, n = 0,0,0
        while(binary != 0):
            a = binary % 10
            #print(a)
            int_val = int_val + a * pow(2,i)
            binary = binary//10
            i += 1
        return int_val

def int2binary(n):
   # "Convertit un nombre en binaire"
    if n == 0: 
        return '0'
    res = ''
    while n != 0: n, res = n >> 1, repr(n & 1) + res
    return res  

def encrypt(message,key):
    #print("key : ",key)
    #print("je suis dans la fonction pour encrypter")
    #print(key)
    cipher = AES.new(key, AES.MODE_EAX)
    #print("test 1")
    ciphertext, tag = cipher.encrypt_and_digest(message)
    #print("J'ai encrypter le message")
    return (cipher.nonce, tag, ciphertext)

def send_data(vpn_client,message,key):
    print("message à envoyer : ",message)
    nonce, tag, ciphertext = encrypt(message,key)
    # print("taille nonce : ",len(nonce))
    # print("taille tag : ",len(tag))
    # print("taille ciphertext : ",len(ciphertext))
    
    # je stocke les données à envoyer dans un objet pour facilité l'échange
    data_obj = {"nonce":nonce, "tag":tag, "msg":ciphertext}
    
    # Je serialize l'objet avant de l'envoyer 
    data_serialized_obj = pickle.dumps(data_obj,protocol=4)
    
    # print("nonce : ",nonce)
    # print("tag : ",tag)
    # print("ciphertext : ",ciphertext)
    vpn_client.sendall(data_serialized_obj)
    
def decrypt(key, nonce, tag, ciphertext):
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    print("nonce : ",nonce)
    print("tag : ",tag)
    msg = cipher.decrypt_and_verify(ciphertext, tag)

    print("LE MESSAGE RECU EST : ",msg)
    return msg

def recv_message(client_connection,key):
    
    data_obj = client_connection.recv(1024)

    print(data_obj)
    print("TAILLE: ",len(data_obj))
    
    

    print("TAILLE: ",len(data_obj))
    
    data_obj_deserialized = pickle.loads(data_obj)
    
    # Récupérer les données dans différentes variables
    nonce = data_obj_deserialized["nonce"]
    tag = data_obj_deserialized["tag"]
    msg = data_obj_deserialized["msg"]
    #nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    # print("nonce : ",nonce)
    # print("tag : ",tag)
    # print("ciphertext : ",ciphertext)
    
    return decrypt(key,nonce,tag,msg)

def decryptFile(_file,_newFile,key):
    file = open(_file,"rb")
    newFile = open(_newFile,"wb")
    lignes = file.readlines()
    #print("lignes: ",lignes)
    for ligne in lignes:
        lineEncrypted = decrypt(ligne.decode(),key)
        #print("ligne encrypté: ",lineEncrypted)
        newFile.write(lineEncrypted)
        
def keyCalculated(server_private_key,client_public_key,p,g):
    return client_public_key ** server_private_key % p
        
        
def ReceptionFile(key_partaged):
    accepte = "non"
    num = 0
    pourcent = 0
    while (client_connection.connect):
        recu = ""
        #recu = client_connection.recv(1024)     
        recu = recv_message(client_connection,key_partaged)
        print(recu)
        if not recu : return False
        
        if accepte == "non": # Condition si on a pas deja envoyer le nom et la taille du fichier
                tmp = recu.decode()
                nomFich = tmp.split("NAME ")[1]
                nomFich = nomFich.split("OCTETS ")[0]
                taille = tmp.split("OCTETS ")[1]
                print ("\n---> Fichier '" + nomFich + "' [" + taille + " Ko]")

                accepte = "o" # demande si on accepte ou pas le transfert                               

                if accepte == "o" or accepte == "oui": # Si oui en lenvoi au client et on cree le fichier
                    signal = "GO"
                    #client_connection.send(signal.encode())
                    send_data(client_connection,signal.encode(),key_partaged)
                    #SomUpload = addDataLenght(recu,SomUpload)
                    print (time.strftime("\n---> [%H:%M] réception du fichier en cours veuillez patienter..."))
                    f = open("RECU.txt", "wb")
                    accepte = "oui"
                    taille = float(taille) * 1024 # Conversion de la taille en octets pour le %
                                        
                else :
                    signal = "Bye"
                    #client_connection.send(signal.encode()) # Si pas accepte on ferme le programme
                    send_data(client_connection,signal.encode(),key_partaged)
                    # SomUpload = addDataLenght(recu,SomUpload)
                    return False

        elif recu.decode('utf-16') == "BYE": # Si on a recu "BYE" le transfer est termine

            print (" -> 100%" ) 
            f.close()
            print (time.strftime("\n---> Le %d/%m a %H:%M réception du fichier termine !"))
            break
        else: # Sinon on ecrit au fur et a mesure dans le fichier
            print("j'ai recu le paquet je vais l'archiver")
            f.write(recu)
            print(recu)
            signal="ok"
            #client_connection.send(signal.encode())
            
            send_data(client_connection,signal.encode(),key_partaged)
            print("J'AI BIEN RECU LE PAQUET")
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
    
    
    #decryptFile("RECU.txt","Serveur_RECU.txt",key_partaged)
    
    return True
    
#-----------------------------------MISE EN PLACE DU SOCKET------------------------------------#

# Création du socket 
vpn_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = ('',24081)

# Liaison du socket à une adresse IP et un port 
vpn_server.bind((host,port))

# Mise en écoute du socket 
vpn_server.listen()
print("\n--------->Ouverture du serveur...")

#-----------------------------------ÉCHANGE DES CLES DE DIFFIE-HUFFMAN------------------------------------#

def addDataLenght(data,somme):
    data = data.decode()
    print(type(data))
    # Permet d'ajouter la taille des données dans la somme qu'on veut
    octets = len(data)
    somme = somme + octets 
    return somme

def generate_random_prime():
    while True:
        n = random.randint(2, 2**256)
        if all(n % i != 0 for i in range(2, int(n ** (1/2)) + 1)):
            return n

def ParametersGenerator():
    p = generate_random_prime()
    g = random.randint(2, 2**256)
    parameters = (p,g)

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
    #print("Génération des paramètres de DH réussi!")

    # Choix d'une clé privé aléatoire entre 2 et 10
    server_private_key = random.randint(2,10)
    #print("Génération des clés privés de DH réussi!")

    # Calcul de la clé publique de Diffie-Hellman pour le serveur
    #print("Calcul de la clé public du serveur...")
    server_public_key = (g ** server_private_key) % p 
    #print("server_public_key: ",server_public_key,type(server_public_key))
    #print("Calcul de la clé public du serveur terminé!")

    # Serialiation de la clé
    server_public_key_binary = str(int2binary(server_public_key)).encode()
    #print("binary server: ",server_public_key_binary)
        
    # Envoi des paramètres au client 
    client_connection.send(parameters_bytes)
    #SomUpload = addDataLenght(parameters_bytes,SomUpload)
    #print("\nEnvoi des paramètres OK!")

    # Réception de la clé public du client
    client_public_key_byte= client_connection.recv(1024)
    #SomDownload = addDataLenght(client_public_key_byte,SomDownload)
    #print("\nclient binary: ",client_public_key_byte)
    #print("\nReception de la clé public du client OK!")

    # Déserialisation de la clé publique du client
    client_public_key_binary = client_public_key_byte.decode()
    client_public_key = binary2int(client_public_key_binary)
    #print("\nclient_public_key: ",client_public_key)
    #print("\nDéserialisation de la clé public du client OK!")
    #print_hashmap(my_hashmap)
    print("\n")


    # Envoie de la clé publique du serveur au client
    #print("\nbinary server: ",server_public_key_binary)
    client_connection.sendall(server_public_key_binary)
    #SomUpload = addDataLenght(server_public_key_binary,SomUpload)
    
    #print("\nEnvoie de la clé sérialisée OK!")

    # Calcul de la clé paratagée
    key_partaged = keyCalculated(server_private_key,client_public_key,p,g)
    #print("\nclé partagée : ",key_partaged)
    # Stockage de la clé public du client et de la clé public du serveur dans la HashMap

    #my_hashmap[client_connection.getpeername()] = {key_partaged}
    #print_hashmap(my_hashmap)
    print("\n-----> Les clés ont bien été échangées et stockées !")
    
    h = hashlib.sha256(str(key_partaged).encode())
    key_16 = h.hexdigest()[:16]

    
    return key_16.encode()
    
# def encrypt(Messageacrypter,key):
#     lg=len(Messageacrypter)
#     MessageCrypte=""
#     for i in range(lg):
#         if Messageacrypter[i].isalpha():
#             if Messageacrypter[i].isupper():
#                 if ord(Messageacrypter[i])+key > 90:
#                     MessageCrypte+=chr(ord(Messageacrypter[i])+key-26)
#                 else:
#                     MessageCrypte+=chr(ord(Messageacrypter[i])+key)
#             else:
#                 if ord(Messageacrypter[i])+key > 122:
#                     MessageCrypte+=chr(ord(Messageacrypter[i])+key-26)
#                 elif ord(Messageacrypter[i])+key < 65:
#                     MessageCrypte+=chr(ord(Messageacrypter[i])+key+26)
#                 else:
#                     MessageCrypte+=chr(ord(Messageacrypter[i])+key)
#         elif Messageacrypter[i].isnumeric():
#             if ord(Messageacrypter[i])+key > 57:
#                 MessageCrypte+=chr(ord(Messageacrypter[i])+key-10)
#             else:
#                 MessageCrypte+=chr(ord(Messageacrypter[i])+key)
#         else:
#             MessageCrypte += Messageacrypter[i]
#     return MessageCrypte

#-----------------------------------MÉTHODE RUN DES SOUS-PROCESSUS CLIENTS------------------------------------#

def modify_list(l, i):
    l.append(i)

def client_handler(client_connection):
    global client_count
    global clients_connected
    global client_address_list
    global id
    SomUpload = 0
    SomDownload = 0
    now = datetime.now()
    print(now.strftime("%d%m%Y"))
    # Création du tableau qui contiendra les données du trafic réseau
    tab = []
    tab
    # Récupère la date de connexion du client
    date = int(time.strftime("%Y%m%d"))
    print(date,type(date))
    tuple = (date,SomUpload,SomDownload)
    tab.append(tuple)
    print(tab)

    # Code pour gérer les communications avec le client ici
    client_count += 1
    clients_connected.append(client_connection)
    print("\nLe thread du client : ",client_connection.getpeername()," est lancé !")
    # Echange des clés de Diffie-Hullman
    key_partaged = DiffieHullamKeyExchange(client_connection)
    while (client_connection.fileno() != -1):
        #recu = client_connection.recv(1024)
        recu = recv_message(client_connection,key_partaged)
        #print(recu)
        if (recu.decode() == "send file"):
            rep= ReceptionFile(key_partaged)
            if rep == False:
                print("\n-----> Le client ",client_connection.getpeername()," s'est déconnecté !")
                client_count -= 1
                clients_connected.remove(client_connection)
                break
        if (recu.decode() == "speedtest upload"):
            print("Début speedtest")
            signal = "GO"
            client_connection.send(signal.encode())
            print("j'ai envoyé go")
            for i in range(10):
                if recu.decode() == "quit":
                    break
                signal = "OK"
                data = client_connection.recv(1024)
                client_connection.send(signal.encode())
            
        if (recu.decode() == "speedtest download"):
            file = open("sauvegarde.txt","rb")
            for i in range(10):
                donnees = file.read(1024) # Lecture du fichier en 1024 octets           
                client_connection.send(donnees) 
                recu = client_connection.recv(50)
        if (recu.decode() == "trafic"):
            print("")
        if (recu.decode() == "reception msg"):
            print("---------> Je vais recevoir un mail \n")
            signal = "ok"
            client_connection.send(signal.encode())
            
            destinataire = client_connection.recv(1024)
            #print("Le destinataire crypté est : ",destinataire.decode())
            destinataire = decrypt(destinataire.decode(),key_partaged)
            print("Le destinataire décrypté est : ",destinataire)
            client_connection.send(signal.encode())
            
            subject = client_connection.recv(1024)
            #print("Le sujet est : ",subject.decode())
            subject = decrypt(subject.decode(),key_partaged)
            print("Le subject décrypté est : ",subject)
            client_connection.send(signal.encode())
            
            text = client_connection.recv(1024)
            #print("Le text est : ",text.decode())
            text = decrypt(text.decode(),key_partaged)
            print("Le text décrypté est : ",text)
            client_connection.send(signal.encode())
            
            print("--------------------> J'AI TROUVÉ LE CLIENT DANS LE FICHIER !!!")
            print("J'ai archiver le mail dans la BDD -----> \n")
            id +=1
            c.execute("INSERT INTO emails (id,connection_ip, source,subject,text,recu) VALUES (?,?, ?,?,?,?)", (id,destinataire, client_address[0],subject,text,False))
            conn.commit()
            for ip in client_address_list:
                print(ip)
                
        # Y A UN PB POUR LES VERIF DU TUPLE DANS LA LISTE 
        ###################################################################### 
        if recu.decode() == "recv msg ok":
            pass
            # print("je regarde dans l'archive si j'ai des msg --> \n")
            
            # c.execute("SELECT COUNT(*) FROM emails WHERE connection_ip = ? and recu = ?", (client_address[0],False))
            # result = c.fetchone()

            # print("Number de message à envoyer au client:", result[0])
            
            # # j'envoie le nombre de msg en attente (peut-être à zéro)
            # nb_msg = str(result[0])
            # #client_connection.send(nb_msg.encode())
            # send_data(client_connection,nb_msg.encode(),key_partaged)
            
            # #rep = client_connection.recv(1024)
            # rep = recv_message(client_connection,key_partaged)
            
            # if rep.decode() == "yes":
            #     c.execute("SELECT * FROM emails WHERE connection_ip IN (SELECT ip FROM connections WHERE ip = ?) and recu = ?", (client_address[0],False))
            #     rows = c.fetchall()
                
            #     for row in rows:
            #         print(row)
                    
            #         source = encrypt(row[2],key_partaged)
            #         subject = encrypt(row[3],key_partaged)
            #         text = encrypt(row[4],key_partaged)
                    
            #         c.execute("UPDATE emails SET recu=? WHERE id=?", (True, row[0]))
            #         conn.commit()
                    
            #         #client_connection.send(source.encode())
            #         send_data(client_connection,source.encode(),key_partaged)
            #         print("j'ai envoyé la source")
            #         print("j'attends signal")
            #         #rep = client_connection.recv(1024)
            #         rep = recv_message(client_connection,key_partaged)
                    
            #         if (rep.decode() == "ok"):
            #             print("j'ai recu le signal")
            #             #client_connection.send(subject.encode())
            #             send_data(client_connection,subject.encode(),key_partaged)
            #             print("j'ai envoyé")
            #             #rep = client_connection.recv(1024)
            #             rep = recv_message(client_connection,key_partaged)
                    
            #         if (rep.decode() == "ok"):
            #             print("j'ai recu le signal")
            #             send_data(client_connection,text.encode(),key_partaged)
            #             #client_connection.send(text.encode())
            #             print("j'ai envoyé")
            #             #rep = client_connection.recv(1024)
            #             rep = recv_message(client_connection,key_partaged)
                
        if (recu.decode() == "exit"):
            print("\n-----> Le client ",client_connection.getpeername()," s'est déconnecté !")
            client_count -= 1
            clients_connected.remove(client_connection)
            break
        
    
#-----------------------------------MISE EN RESEAU------------------------------------#
print("\n--------->Serveur ouvert!")
# Variables pour compter les clients connectés
client_count = 0
clients_connected = []
processus_list = []
client_address_list = []
id = 0 
# Connect to or create the database
conn = sqlite3.connect('client_connections.db')
c = conn.cursor()

# Create table if not exists
c.execute("CREATE TABLE IF NOT EXISTS connections (ip text, port integer)")
c.execute('''CREATE TABLE IF NOT EXISTS emails (id integer,
                                                connection_ip text, 
                                                source text, 
                                                subject text, 
                                                text text, 
                                                recu boolean,
                                                FOREIGN KEY(connection_ip) REFERENCES connections(ip))''')


while(True):
    client_connection, client_address = vpn_server.accept()
    if client_address[0] == "77.128.169.245" or client_address[0] == "192.168.1.5":
        client_found = False
        for i, ca in enumerate(client_address_list):
            if ca[0] == client_address[0]:
                client_address_list[i] = client_address
                client_found = True
                client_process = Process(target=client_handler, args=(client_connection,))
                client_process.start()
                break
        if not client_found:
            client_address_list.append(client_address)
            client_process = Process(target=client_handler, args=(client_connection,))
            processus_list.append(client_process)
            client_process.start()
            print(f'\n--------->Connexion de {client_address}')
            c.execute("INSERT INTO connections (ip, port) VALUES (?, ?)", (client_address[0], client_address[1]))
            conn.commit()
            print("\n---> Liste des clients connecté\n")
            for ip in client_address_list:
                print(ip,type(ip))
                print(len(client_address_list))
        else:
            print(f'\n--------->Connexion existante de {client_address} mise à jour')
            c.execute("UPDATE connections SET port=? WHERE ip=?", (client_address[1], client_address[0]))
            conn.commit()
    else:
        print(f'\n--------->Refus de la connexion de {client_address}')
        client_connection.close()
    
conn.close()
vpn_server.close()
#-----------------------------------ÉCHANGE DES CLES DE DIFFIE-HUFFMAN------------------------------------#