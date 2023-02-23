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
    # print("message à envoyer : ",message)
    nonce, tag, ciphertext = encrypt(message,key)
    # Hachage en SHA-256
    hash_object = hashlib.sha256(message)

    # Convertir le hash en hexadécimal
    hex_dig = hash_object.hexdigest()

    # print("LE HASH : ",hex_dig)
    
    # je stocke les données à envoyer dans un objet pour facilité l'échange
    data_obj = {"nonce":nonce, "tag":tag, "msg":ciphertext,"hash":hex_dig}
    
    # Je serialize l'objet avant de l'envoyer 
    data_serialized_obj = pickle.dumps(data_obj,protocol=4)
    
    # print("nonce : ",nonce)
    # print("tag : ",tag)
    # print("ciphertext : ",ciphertext)
    print("TAILLE : ",len(data_serialized_obj))

    vpn_client.sendall(data_serialized_obj)
    
def decrypt(key, nonce, tag, ciphertext):
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    # print("nonce : ",nonce)
    # print("tag : ",tag)
    msg = cipher.decrypt_and_verify(ciphertext, tag)

    print("LE MESSAGE RECU EST : ",msg)
    
    return msg

def recv_message(client_connection,key):
    
    data_obj = client_connection.recv(1024)

    # print("OBJET À DESERIALIZER : ",data_obj)
    # print("TAILLE: ",len(data_obj))
    
    data_obj_deserialized = pickle.loads(data_obj)
    
    # Récupérer les données dans différentes variables
    nonce = data_obj_deserialized["nonce"]
    tag = data_obj_deserialized["tag"]
    msg = data_obj_deserialized["msg"]
    hash = data_obj_deserialized["hash"]
    #nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    # print("nonce : ",nonce)
    # print("tag : ",tag)
    # print("ciphertext : ",ciphertext)
    
    msg = decrypt(key,nonce,tag,msg)
    
     # Hachage en SHA-256
    hash_object = hashlib.sha256(msg)

    # Convertir le hash en hexadécimal
    hex_dig = hash_object.hexdigest()
    
    print("LE HASH : ",hex_dig)
    if hex_dig != hash:
        print("Problème d'intégrité ! Les données ont pu être modifié au cours du transfère")
    return msg

def keyCalculated(server_private_key,client_public_key,p,g):
    return client_public_key ** server_private_key % p
        
        
def ReceptionFile(key_partaged):
    accepte = "non"
    num = 0
    pourcent = 0
    signal = "ok"
    global id_file
    
    send_data(client_connection,signal.encode(),key_partaged)
    
    ip = recv_message(client_connection,key_partaged)
    
    while (client_connection.connect):
        recu = ""
        #recu = client_connection.recv(1024)     
        recu = recv_message(client_connection,key_partaged)
        
        if not recu : return False
        
        if accepte == "non": # Condition si on a pas deja envoyer le nom et la taille du fichier
                tmp = recu.decode()
                nomFich = tmp.split("NAME ")[1]
                nomFich = nomFich.split("OCTETS ")[0]
                taille = tmp.split("OCTETS ")[1]
                print ("\n---> Fichier '" + nomFich + "' [" + taille + " Ko]")
                nom_fichier = os.path.basename(nomFich)
                
                c.execute("SELECT COUNT(*) FROM FICHIERS",)
                id = c.fetchone()[0]
                
                
                c.execute("INSERT INTO FICHIERS (id,source_ip,destinataire_ip,nom_file,file,recu) VALUES (?,?,?,?,?,?)", 
                        (id+1,client_address[0], ip,nom_fichier,"",False))
                conn.commit() 
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

        elif recu.decode() == "bye": # Si on a recu "BYE" le transfer est termine

            print (" -> 100%" ) 
            f.close()
            
            print (time.strftime("\n---> Le %d/%m a %H:%M réception du fichier termine !"))
            break
        else: # Sinon on ecrit au fur et a mesure dans le fichier
            print("j'ai recu le paquet je vais l'archiver")
            f.write(recu)
            #print(recu.decode(),type(recu.decode()))
            
            # récupérer l'ancien contenu de la colonne "file"
            c.execute("SELECT file FROM FICHIERS WHERE id=? AND source_ip=? AND destinataire_ip=? AND nom_file=?", (id+1,client_address[0], ip,nom_fichier))
            ancien_contenu = c.fetchone()[0]
            
            # ajouter du texte à la colonne "file"
            nouveau_contenu = ancien_contenu + recu.decode()

            # mettre à jour la colonne "file" pour l'enregistrement spécifié
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

def sendFile(name_file,file,ip,key_partaged):  
    
    # Envoie d'un premier signal pour annoncé que la fonction est lancé
    signal = "send file"
    send_data(client_connection,signal.encode(),key_partaged)
    print("j'ai envoyé signal que je vais envoyer après son signal")
    
    # Envoie d'un signal pour me dire que le client est prêt à recevoir les paquets
    rep = recv_message(client_connection,key_partaged)
    print("j'ai son signal : ",rep)
    
    # Définissions de la taille du fichier
    octets = os.path.getsize(file) / 870
    
    # Vérifiaction des informations
    print ("\n---> Fichier à envoyer : '" + name_file + "' [" + str(octets) + " Ko]")
    tmp = "NAME " + name_file + "OCTETS " + str(octets)
    
    # Envoie des informations du fichiers qui va être envoyé
    send_data(client_connection,tmp.encode(),key_partaged)
    
    while (client_connection.connect):
        print("j'attend")
        tmp = recv_message(client_connection,key_partaged)
        print(tmp)
        print("j'ai reçu")
        recu = tmp.decode() 
        if not recu : return False

        if recu == "GO": # Si le serveur accepte on envoi le fichier
            #console.insert("end","[%H:%M] transfert en cours veuillez patienter...\n","orange")
            print("test 1")
            num = 0
            pourcent = 0
            octets = octets * 870 # Reconverti en octets
            fich = open(file, "rb")
            remaining_data = octets
            if octets > 870:	# Si le fichier est plus lourd que 1024 on l'envoi par paquet
                print("test 2")
                for i in range(int(octets / 870)+1):       
                    print("test 3") 
                    if remaining_data > 870:
                        print("test 4")
                        fich.seek(num, 0) # on se deplace par rapport au numero de caractere (de 1024 a 1024 octets)
                        donnees = fich.read(870) # Lecture du fichier en 1024 octets    
                        print("Donné à envoyé : ",donnees)       
                        #vpn_client.send(donnees) # Envoi du fichier par paquet de 1024 octets
                        #encoded_message = donnees.encode('utf-16-le')
                        send_data(client_connection,donnees,key_partaged)
                        
                        print("jai encoyé un paquet")
                        #rep=vpn_client.recv(1024)
                        rep = recv_message(client_connection,key_partaged)
                        print("JE PEUX CONTINUER")
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
                    else:
                        print("test 5")
                        donnees = fich.read(int(remaining_data))
                        # if len(donnees) < 870:
                        #     padding = b'\x00' * (870 - len(donnees))
                        #     donnees += padding
                        #vpn_client.send(donnees)
                        print("Donné à envoyé en une fois: ",donnees)   
                        send_data(client_connection,donnees,key_partaged)
                        print("jai encoyé un paquet")
                        #rep=vpn_client.recv(1024)
                        rep = recv_message(client_connection,key_partaged)
                        print("JE PEUX CONTINUER")
                        print (" -> 100%")  
                        break  
                        
            else: # Sinon on envoi tous d'un coup
                print("test 6")
                donnees = fich.read()
                # if len(donnees) < 870:
                #             padding = b'\x00' * (870 - len(donnees))
                #             donnees += padding
                #vpn_client.send(donnees)
                print("Donné à envoyé en une fois: ",donnees)
                send_data(client_connection,donnees,key_partaged)
                recv_message(client_connection,key_partaged)

            fich.close()
            # console.insert("end","Le %d/%m a %H:%M transfert termine !\n","orange")
            signal2 = "bye"
            print("fin")
            #vpn_client.send(signal2.encode()) # Envoi comme quoi le transfert est fini
            send_data(client_connection,signal2.encode(),key_partaged)
            #print("\nsignal envoyé : ",signal2)
            
            return True
        else:
            print (time.strftime("\n--->[%H:%M] transfert annulé."))
            # console.insert("end","[%H:%M] transfert annulé.\n","orange")
            return "BYE"
#-----------------------------------MÉTHODE RUN DES SOUS-PROCESSUS CLIENTS------------------------------------#

def modify_list(l, i):
    l.append(i)

def client_handler(client_connection):
    global client_count
    global clients_connected
    global client_address_list
    global id_mail
    global id_file
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
            id_file = id_file + 1
            
            rep= ReceptionFile(key_partaged)
            if rep == False:
                print("\n-----> Le client ",client_connection.getpeername()," s'est déconnecté !")
                client_count -= 1
                clients_connected.remove(client_connection)
                break
        if (recu.decode() == "speedtest upload"):
            print("Début speedtest")
            signal = "GO"
            send_data(client_connection,signal.encode(),key_partaged)
            #client_connection.send(signal.encode())
            print("j'ai envoyé go")
            for i in range(50):
                if recu.decode() == "quit":
                    break
                signal = "OK"
                #data = client_connection.recv(1024)
                data = recv_message(client_connection,key_partaged)
                #client_connection.send(signal.encode())
                send_data(client_connection,signal.encode(),key_partaged)
            
        if (recu.decode() == "speedtest download"):
            file = open("sauvegarde.txt","rb")
            for i in range(50):
                donnees = file.read(870) # Lecture du fichier en 1024 octets          
                print(donnees) 
                #client_connection.send(donnees) 
                send_data(client_connection,donnees,key_partaged)
                recu = recv_message(client_connection,key_partaged)
        if (recu.decode() == "trafic"):
            print("")
        if (recu.decode() == "reception msg"):
            print("---------> Je vais recevoir un mail \n")
            signal = "ok"
            send_data(client_connection,signal.encode(),key_partaged)
            #client_connection.send(signal.encode())
            
            destinataire = recv_message(client_connection,key_partaged)
            
            #print("Le destinataire crypté est : ",destinataire.decode())
            #destinataire = decrypt(destinataire.decode(),key_partaged)
            print("Le destinataire décrypté est : ",destinataire)
            #client_connection.send(signal.encode())
            send_data(client_connection,signal.encode(),key_partaged)
            
            subject = recv_message(client_connection,key_partaged)
            #print("Le sujet est : ",subject.decode())
            #subject = decrypt(subject.decode(),key_partaged)
            print("Le subject décrypté est : ",subject)
            #client_connection.send(signal.encode())
            send_data(client_connection,signal.encode(),key_partaged)
            
            text = recv_message(client_connection,key_partaged)
            #print("Le text est : ",text.decode())
            #text = decrypt(text.decode(),key_partaged)
            #print("Le text décrypté est : ",text)
            #client_connection.send(signal.encode())
            send_data(client_connection,signal.encode(),key_partaged)
            
            # print("--------------------> J'AI TROUVÉ LE CLIENT DANS LE FICHIER !!!")
            # print("J'ai archiver le mail dans la BDD -----> \n")
            id_mail +=1
            c.execute("INSERT INTO emails (id_mail,connection_ip, source,subject,text,recu) VALUES (?,?, ?,?,?,?)", (id,destinataire.decode(), client_address[0],subject.decode(),text.decode(),False))
            conn.commit()
            
            c.execute('SELECT * FROM emails')
            rows = c.fetchall() 
            for row in rows:
                print("\'",row,"\'")
                
        if recu.decode() == "recv msg ok":
            
            c.execute('SELECT * FROM emails')
            rows = c.fetchall() 
            for row in rows:
                print("\'",row,"\'")
            c.execute("SELECT COUNT(*) FROM emails WHERE connection_ip = ? and recu = ?", (client_address[0],False))
            result = c.fetchone()
            
            # j'envoie le nombre de msg en attente (peut-être à zéro)
            nb_msg = str(result[0])
            send_data(client_connection,nb_msg.encode(),key_partaged)
            
            rep = recv_message(client_connection,key_partaged)
            print("signal recu\n")
            if rep.decode() == "yes":
                c.execute("SELECT * FROM emails WHERE connection_ip IN (SELECT ip FROM connections WHERE ip = ?) and recu = ?", (client_address[0],False))
                rows = c.fetchall()
                # print("J'ai récuperer tous les messages\n")
                for row in rows:
                    print(row)
                    
                    source = row[2]
                    subject = row[3]
                    text = row[4]
                    
                    c.execute("UPDATE emails SET recu=? WHERE id=?", (True, row[0]))
                    conn.commit()
                    
                    send_data(client_connection,source.encode(),key_partaged)
                    rep = recv_message(client_connection,key_partaged)
                    
                    if (rep.decode() == "ok"):
                        send_data(client_connection,subject.encode(),key_partaged)
                        rep = recv_message(client_connection,key_partaged)
                    
                    if (rep.decode() == "ok"):
                        send_data(client_connection,text.encode(),key_partaged)
                        rep = recv_message(client_connection,key_partaged)
        if recu.decode() == "recv file ok":
            pass 
            ip = client_address[0]
            c.execute("SELECT COUNT(*) FROM fichiers WHERE destinataire_ip= ? and recu=?", (ip.encode(),False))
            nb_file = c.fetchall()[0][0]
            send_data(client_connection,str(nb_file).encode(),key_partaged)
            print("J'ai envoyé : ",nb_file)
            
            rep = recv_message(client_connection,key_partaged)
            print(rep)
            if rep.decode() == "oui":
                print("j'ai rcu le signal pour envoyer les fichiers")
                c.execute('SELECT * FROM fichiers WHERE recu=?',(False,))
                rows = c.fetchall() 
                
                for row in rows:
                    #print("\'",row,"\'")
                    #print("je suis dans le for")
                    file = open("fichier_tmp.txt", "w")
                    file.write(row[4])
                    file.close()
                    print("j'ai écrit dans le fichier")
                    print("je lance la fonction")
                    sendFile(row[3],"fichier_tmp.txt",client_address[0],key_partaged)
                    c.execute("UPDATE FICHIERS SET recu=? WHERE id=?", (True, row[0]))
                    conn.commit()
            
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
id_mail = 0 
id_file = 0
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
c.execute('''CREATE TABLE IF NOT EXISTS fichiers (id integer,
                                                    source_ip text,
                                                    destinataire_ip text,
                                                    nom_file text,
                                                    file text,
                                                    recu boolean)''')


while(True):
    client_connection, client_address = vpn_server.accept()
    if client_address[0] == "77.128.153.176" or client_address[0] == "192.168.1.5" or client_address[0] == "127.0.0.1":
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