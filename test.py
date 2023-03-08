# def sendFileQuery():
#     signal = "send file"
#     vpn_client.send(signal.encode()) # Envoi du nom et de la taille du fichier
#     add_data_upload(cursor,len(signal.encode()),now)
#     tmp = vpn_client.recv(1024)
#     add_data_download(cursor,len(tmp),now)
#     recu = tmp.decode() 
    
#     return recu
