# def sendFileQuery():
#     signal = "send file"
#     vpn_client.send(signal.encode()) # Envoi du nom et de la taille du fichier
#     add_data_upload(cursor,len(signal.encode()),now)
#     tmp = vpn_client.recv(1024)
#     add_data_download(cursor,len(tmp),now)
#     recu = tmp.decode() 
    
#     return recu

#* Cette fonction permet de gérer initialisation des données pour le diagramme
# def initialise_trafic_reseau():
#     global tab_trafic
    
#     # Recupère la date actuelle
#     now = datetime.now()
#     now = now.strftime("%d%m%Y")
    
#     # Si la table 
#     if len(tab_trafic) < 0:
#         new_line = (date,0,0)
#         # Ajout nouvelle ligne car nouvelle date
#         tab_trafic.append(new_line)
#         return False
        
#     for ligne in tab_trafic:
#         print(ligne[0],type(ligne[0]))
#         if ligne[0] == now:
#             return True
#     date = now
#     new_line = (date,0,0)
#     # Ajout nouvelle ligne car nouvelle date
#     tab_trafic.append(new_line)
#     return False
