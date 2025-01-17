# coding: utf-8
import os
import sys
import time
import math
import random
import socket
import struct
import pickle
import hashlib
import sqlite3
import warnings
from tkinter import *
from PIL import Image,ImageTk
from datetime import datetime
from Crypto.Cipher import AES
from tkinter import messagebox
from tkinter import filedialog
from Crypto.Hash import SHA256
from tkinter.ttk import Combobox 
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

warnings.filterwarnings("ignore")

#?##########################################################################################################################################
#?----------------------------------------------------------FONCTIONS INTERFACE------------------------------------------------------------#
#?##########################################################################################################################################

#* Cette fonction permet de retourner les informations de la fenêtre : hauteur, largeur, position en x,
#* position en y
#* Paramètre : g = la fenêtre
def geoliste(g):
    r=[i for i in range(0,len(g)) if not g[i].isdigit()]
    return [int(g[0:r[0]]),int(g[r[0]+1:r[1]]),int(g[r[1]+1:r[2]]),int(g[r[2]+1:])]

#* Cette fonction permet de centre la fenêtre
#* Paramètre : fen = la fenêtre
def centrefenetre(fen):
    fen.update_idletasks()
    l,h,x,y=geoliste(fen.geometry())
    fen.geometry("%dx%d%+d%+d" % (l,h,(fen.winfo_screenwidth()-l)//2,(fen.winfo_screenheight()-h)//2))

#* Cette fonction permet d'avoir les informations sur la taille de la fenêtre
def get_window_size():
    window_geometry = fenetre.winfo_geometry()
    width, height = window_geometry.split("x")[0], window_geometry.split("x")[1].split("+")[0]
    return width, height

#* Cette fonction permet d'afficher une fenêtre pop-up avant de fermer la fenêtre
def on_closing():
    if messagebox.askyesno("Fermteture de l'application", "Voulez-vous vraiment fermer l'application ? (Vous serez automiquement déconnecté du serveur)", 
                           icon="warning"):
        fenetre.destroy()

#* Cette fonction permet d'afficher les fichiers du dossier courant pour choisir celui qui va être envoyé
def send_file():
    filepath = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    return filepath

ip_address = ""

#* Cette fonction permet de récupérer la liste de contactes enregistrée dans la BDD
def list_cont():
    cursor.execute("SELECT * FROM contacts ")
    rows = cursor.fetchall()
    list=[]
    for row in rows:
        print(row)
        list.append(row[1])
        print(list)
    return list

#* Cette fonction permet à l'utilisateur d'entrer le destinataire impliqué dans l'envoie d'un fichier
#* Paramètre : file = fichier à envoyer
def ip_window(file):
    # Déclaration de la variable globale ip_address qui contiendra l'adresse IP du destinataire.
    global ip_address
    
    # Création d'une fenêtre enfant (Toplevel) qui va permettre à l'utilisateur d'entrer 
    # l'adresse IP du destinataire.
    window_dest = Toplevel(fenetre)
    window_dest.geometry("300x100")
    window_dest.title("Destinataire")
    window_dest.resizable(False,False)
    
    # Centrage de la fenêtre sur l'écran.
    centrefenetre(window_dest)

    # Ajout d'un label pour l'adresse IP
    ip_label = Label(window_dest, text="Adresse IP:")
    ip_label.pack()
    
    # Création d'une Combobox pour l'entrée de l'adresse IP.
    ip_entry = Combobox(window_dest)
    
    # Récupération d'une liste d'adresses IP à partir de la fonction list_cont().
    list = list_cont()
    
    # Ajout des valeurs de la liste dans la Combobox.
    ip_entry['values'] = list
    ip_entry.pack()

    
    #* Définition de la fonction close() qui va récupérer l'adresse IP entrée par l'utilisateur 
    #* et lancer la fonction sendFile() pour envoyer le fichier.
    def close():
        global ip_address
        ip_address = ip_entry.get()
        print(ip_address)
        
        # Recupère le nombre de message déjà présent dans la BDD pour calculer l'id de prochain
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE ad_mail=?",(ip_address,))
        resultat = cursor.fetchone()
        
        if resultat[0] != 0:
            # Je recupère l'ip
            cursor.execute("SELECT ip FROM contacts WHERE ad_mail=?",(ip_address,))
            rep = cursor.fetchone()
            ip_address = rep[0]
        
        window_dest.destroy()
        window_dest.quit()
        sendFile(file,ip_address)

    # Création d'un bouton pour valider l'adresse IP entrée par l'utilisateur.
    add_button = Button(window_dest, text="Valider", command=close)
    add_button.pack()

    # Démarrage de la boucle principale de la fenêtre
    window_dest.mainloop()

#* Cette fonction permet d'ouvrir la console qui va contenir tous les messages et les statuts
#* des différentes interaction avec le système
#* Paramètre : connecte = statut du client (True connecté / False déconnecté)
def open_console(connecte):
    # Déclaration des variables globales console et console_window.     
    global console
    global console_window
    
    # Vérification si la fenêtre console_window existe déjà.
    if console_window.winfo_exists():
        # Si elle existe, on la réactive.
        console_window.deiconify()
    else:
        # Sinon, on crée une nouvelle fenêtre console_window.
        console_window = Toplevel(fenetre)
        console_window.title("Nouvelle fenêtre")
        console_window.geometry("600x300")
        centrefenetre(console_window)
        console_window.resizable(False,False)
        console_window.attributes("-topmost", True)
        
        # Création d'un widget Text pour afficher les messages dans la console.
        console = Text(console_window)
        
        # Configuration des couleurs des messages selon leur type.
        console.tag_config("red", foreground="red")
        console.tag_config("white", foreground="white")
        console.tag_config("green", foreground="green")
        console.tag_config("orange", foreground="orange")
        console.tag_config("blue", foreground="blue")
        console.config(bg="black")
        console.pack()
        console.insert(INSERT, "Bienvenue dans la console\n","white")
        if connecte:
            # Affichage d'un message de connexion si le client est connecté.
            console.insert("end","Connexion au serveur établie !\n","green")
        else:
            # Affichage d'un message de déconnexion si le client est déconnecté.
            console.insert("end","Vous n'êtes plus connecté au serveur.\n","red")

#* Cette fonction permet d'afficher la liste des contacts enregistrée dans la BDD 
def contacts():
    # Création d'une nouvelle fenêtre pour afficher les contacts
    window_contact = Toplevel(fenetre)
    window_contact.geometry("300x400")
    window_contact.title("Contacts")
    
    # Création d'un nouveau frame pour afficher les détails des contacts
    details_contact = Frame(window_contact)
    details_contact.pack()
    
    # Exécution d'une requête SQL pour récupérer tous les contacts de la table "contacts"
    cursor.execute("SELECT * FROM contacts ")
    rows = cursor.fetchall()
    
    # Création d'un nouveau frame pour afficher la liste des contacts
    frame = Frame(window_contact,height=300)
    frame.pack(side="top",fill="both", expand=True)
    contact_list = Listbox(frame)
    
    # Bouton pour ajouter un nouveau contact 
    add_button = Button(window_contact, text="Ajouter un contact", command=lambda :add_contact(window_contact))
    add_button.pack(side="bottom",pady=10)
    # Si la table "contacts" contient des données, les contacts sont ajoutés dans l'interface
    if len(rows) > 0:
        for row in rows:
            print(row)
            contact_list.insert(0, row[1]+" ("+row[0]+")")
    else:
        # Sinon, un message est affiché pour indiquer qu'il n'y a aucun contact enregistré
        details_label = Label(details_contact, text="Vous n'avez aucun contact.")     
        details_label.pack() 
        
    
    # Affichage de la liste des contacts
    contact_list.pack(side="top",fill="both", expand=True)
    
    window_contact.update()

#* Cette fonction permet d'ajouter des contacts dans la liste de contacts en les enregistrant dans la BDD
#* Paramètre : window_contact = fenêtre des contacts
def add_contact(window_contact):
    # Création d'une nouvelle fenêtre pour ajouter un contact
    add_window = Toplevel(window_contact)
    add_window.geometry("300x200")
    add_window.title("Ajouter un contact")
    
     # Création des champs pour entrer l'IP et l'adresse
    ip_label = Label(add_window, text="IP :")
    ip_label.pack(pady=5)
    ip_entry = Entry(add_window)
    ip_entry.pack(pady=5)
    address_label = Label(add_window, text="Adresse :")
    address_label.pack(pady=5)
    address_entry = Entry(add_window)
    address_entry.pack(pady=5)
    
    #* Définition d'une fonction qui sera appelée lorsque l'utilisateur appuie sur le bouton "Ajouter"
    def close():
        ip = ip_entry.get() # Récupération de l'IP entrée par l'utilisateur
        address = address_entry.get() # Récupération de l'adresse entrée par l'utilisateur
        cursor.execute("INSERT INTO contacts (ip,ad_mail) VALUES (?,?)", (ip, address)) # Ajout de l'IP et de l'adresse dans la BDD
        conn.commit() # Sauvegarde des modifications dans la BDD
        window_contact.update() # Mise à jour de la fenêtre des contacts
        add_window.destroy() # Fermeture de la fenêtre d'ajout de contact
    
    # Création du bouton "Ajouter" qui appelle la fonction close() lorsqu'il est cliqué
    add_button = Button(add_window, text="Ajouter", command=close)
    add_button.pack(side="bottom",pady=10)
    
#* Cette fonction permet de gérer les mails reçus ainsi que l'envoie de message
def send_mail():
    # Création d'une nouvelle fenêtre pour gérer les mails
    window_send = Toplevel(fenetre)
    window_send.geometry("800x600")
    window_send.title("Envoi d'e-mail")

    # Ajout d'un label pour la destination de l'e-mail
    dest_label = Label(window_send, text="Destinataire :")
    dest_label.grid(row=0, column=0, padx=10, pady=10)

    # Ajout d'une liste déroulante pour la destination de l'e-mail
    dest_entry = Combobox(window_send)
    
    # Sotckage de la liste récupérer dans la BDD
    list = list_cont()
    dest_entry['values'] = list
    dest_entry.grid(row=0, column=1, padx=10, pady=10)

    # Ajout d'un label pour le sujet de l'e-mail
    subject_label = Label(window_send, text="Sujet :")
    subject_label.grid(row=1, column=0, padx=10, pady=10)

    # Ajout d'une entrée pour le sujet de l'e-mail
    subject_entry = Entry(window_send)
    subject_entry.grid(row=1, column=1, padx=10, pady=10)

    # Ajout d'un label pour le corps de l'e-mail
    body_label = Label(window_send, text="Corps :")
    body_label.grid(row=2, column=0, padx=10, pady=10)

    # Ajout d'une zone de texte pour le corps de l'e-mail
    body_text = Text(window_send)
    body_text.grid(row=2, column=1, padx=10, pady=10)

    #* Définition d'une fonction pour écrire et envoyé un mail
    def send_msg():
        # Je récupère les valeurs des différents champs
        dest_value = dest_entry.get()
        
        # Recupère le nombre de message déjà présent dans la BDD pour calculer l'id de prochain
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE ad_mail=?",(dest_value,))
        resultat = cursor.fetchone()
        
        if resultat[0] != 0:
            # Je recupère l'ip
            cursor.execute("SELECT ip FROM contacts WHERE ad_mail=?",(dest_value,))
            rep = cursor.fetchone()
            dest_value = rep[0]
            
        sub_value = subject_entry.get()
        text_value = body_text.get("1.0", "end")

        # J'envoie un signal pour indiquer au serveur que je vais envoyer un message
        signal = "reception msg"
        send_data(vpn_client,signal.encode(),key_partaged)
        rep = recv_message(vpn_client,key_partaged)
        
        # Si le serveur est prêt à recevoir le destinataire, j'envoie le destinataire
        if (rep.decode() == "ok"):
            send_data(vpn_client,dest_value.encode(),key_partaged)
            rep = recv_message(vpn_client,key_partaged)
        
        # Si le serveur est prêt à recevoir l'objet, j'envoie l'objet
        if (rep.decode() == "ok"):
            send_data(vpn_client,sub_value.encode(),key_partaged)
            rep = recv_message(vpn_client,key_partaged)
        
        # Si le serveur est prêt à recevoir le corps du message, j'envoie le corps du message
        if (rep.decode() == "ok"):
            send_data(vpn_client,text_value.encode(),key_partaged)
            rep = recv_message(vpn_client,key_partaged)
        
        if connecte:
            # Message console
            console.insert("end","Message envoyé !\n","orange")
        
        # Je ferme la fenetre
        window_send.destroy()

    # Ajout d'un bouton pour envoyer l'e-mail
    send_button = Button(window_send, text="Envoyer", command=send_msg)
    send_button.grid(row=3, column=1, padx=10, pady=10)
    
#* Cette fonction permet d'ouvrir les mails 
def open_mail():
    global window_mail
    global mail_list
    global details_frame
    global details_label
    
    # Vérifie si la fenêtre existe déjà et la déroule si c'est le cas
    if window_mail.winfo_exists():
        window_mail.deiconify()
    else:
        # Sinon, crée une nouvelle fenêtre et configure ses propriétés
        window_mail = Toplevel(fenetre)
        window_mail.geometry("600x400")
        window_mail.title("Application Email")
        window_mail.resizable(False,False)
        centrefenetre(window_mail)
        frame = Frame(window_mail)
        frame.pack(side="left", fill="both", expand=True)
        mail_list = Listbox(frame)
        # Ajout d'une liste de mails
        mail_list.pack(fill="both", expand=True)
        # Ajout d'un cadre pour contenir les détails du mail sélectionné
        details_frame = Frame(window_mail)
        details_frame.pack(side="right", fill="both", expand=True)
        # Ajout d'un label pour afficher les détails du mail sélectionné
        details_label = Label(details_frame, text="Sélectionnez un mail")
        details_label.pack(fill="both", expand=True)
    
    # Vide mail_list si elle déjà été remplie
    if mail_list.winfo_exists():
        mail_list.delete(0,'end')
    
    # Récupère les mails depuis la base de données
    cursor.execute("SELECT * FROM email_client ")
    rows = cursor.fetchall()
    
    # Ajoute les mails dans la liste de mails de l'interface
    for row in rows:
        print(row)
        mail_list.insert(1, row[1]+" ("+row[2]+")")

    #* Définition d'une fonction pour afficher les détails du mail sélectionné
    def display_details(event):
        global details_label
        global details_frame
        global mail_list
        # Efface la notification en haut de l'écran lorsque l'utilisateur ouvre un mail
        canvas.coords(notif,0,0,0,0)
        fenetre.update()
        
        # Récupère l'index du mail sélectionné
        index = mail_list.curselection()[0]
        print(index)
        
        # Remet à 0 les anciens widgets
        for widget in details_frame.winfo_children():
            if isinstance(widget, Label):
                widget.destroy()
                
        # Efface le label des détails pour éviter des doublons et crée les labels pour chaque 
        # détail du mail
        details_label.destroy()
        source_label = Label(details_frame, text="Source :")
        source_label.grid(row=0, column=0, padx=10, pady=10)
        source = Label(details_frame, text=rows[index][1])
        source.grid(row=0, column=1, padx=0, pady=10)
        subject_label = Label(details_frame, text="Sujet :")
        subject_label.grid(row=1, column=0, padx=10, pady=10)
        subject = Label(details_frame, text=rows[index][2])
        subject.grid(row=1, column=1, padx=0, pady=10)
        text_label = Label(details_frame, text="Texte :")
        text_label.grid(row=2, column=0, padx=10, pady=10)
        text = Label(details_frame, text=rows[index][3])
        text.grid(row=2, column=1, padx=0, pady=10)
        
        # Ajoute un bouton "Répondre" dans les détails du mail sélectionné et qui appelle 
        # la fonction send_mail()
        reply_button = Button(details_frame, text="Répondre", command=send_mail)
        reply_button.grid(row=3, column=1, padx=10, pady=10)


    # Liaison de la fonction display_details() à l'événement "selection" de la liste de mails
    mail_list.bind("<<ListboxSelect>>", display_details)
    
    # Ajoute une barre de menu à la fenêtre d'affichage des mails et définit les 
    # commandes à exécuter pour chaque option du menu
    menu_bar = Menu(window_mail)
    window_mail.config(menu=menu_bar)    
    menu_bar.add_command(label="Contacts", command=contacts)
    menu_bar.add_command(label="Envoyer mail", command=send_mail)
    
#* Cette fonction permet d'ajuster tous les éléments graphiques en fonction de la taille de la fenêtre
def on_resize(event):
    # Récupère la nouvelle taille de la fenêtre
    width = event.width
    height = event.height
    
    # Ajuste l'image en arrière plan
    canvas.itemconfigure(img,width=width,height=height)
    
    # MODULE BOUTON ON OFF
    canvas.coords(module1_1,15/1200*width, 15/630*height, 220/1200*width, 320/630*height)
    canvas.coords(module1,20/1200*width, 20/630*height, 215/1200*width, 315/630*height)
    canvas.coords(bouton_module1_1,50/1200*width, 50/630*height, 180/1200*width, 180/630*height)
    canvas.coords(bouton_module1_2,65/1200*width, 65/630*height, 165/1200*width, 165/630*height)
    canvas.coords(bouton_module1_3,85/1200*width, 85/630*height, 145/1200*width, 145/630*height)
    canvas.coords(bouton_module1_4,93/1200*width, 93/630*height, 138/1200*width, 138/630*height)
    canvas.coords(dessin_ON_OFF_module1,113/1200*width, 75/630*height, 120/1200*width, 120/630*height)
    canvas.coords(txt_module1,115/1200*width, 250/630*height)
    canvas.itemconfigure(txt_module1, font=("Robot", int(19/630*height),"bold"))
    
    # MODULE SPEEDTEST
    canvas.coords(txt_speedtest,600/1200*width, 35/630*height)
    canvas.itemconfigure(txt_speedtest, font=("Robot", int(10/630*height),"bold"))
    canvas.coords(module2_1,294/1200*width, 15/630*height, 907/1200*width, 310/630*height)
    canvas.coords(module2,299/1200*width, 20/630*height, 902/1200*width, 305/630*height)
    canvas.coords(carre_download,365/1200*width, 40/630*height, 528/1200*width, 60/630*height)
    canvas.coords(txt_download,445/1200*width, 50/630*height)
    canvas.itemconfigure(txt_download, font=("Robot", int(14/630*height),"bold"))
    canvas.coords(carre_upload,680/1200*width, 40/630*height, 843/1200*width, 60/630*height)
    canvas.coords(txt_upload,764/1200*width, 50/630*height)
    canvas.itemconfigure(txt_upload, font=("Robot", int(14/630*height),"bold"))
    canvas.coords(cercle_down,365/1200*width, 95/630*height, 530/1200*width, 245/630*height)
    canvas.coords(cercle_down2,385/1200*width, 110/630*height, 510/1200*width, 230/630*height)
    canvas.coords(polygone_down,417/1200*width, 247/630*height, 
                                431/1200*width, 211/630*height,
                                465/1200*width, 209/630*height, 
                                475/1200*width, 247/630*height)
    canvas.coords(carre_fleche_down1,432/1200*width, 218/630*height, 462/1200*width, 248/630*height)
    canvas.coords(linefleche_down1_1,437/1200*width, 243/630*height, 457/1200*width, 243/630*height)
    canvas.coords(linefleche_down1_2,447/1200*width, 225/630*height, 447/1200*width, 243/630*height)
    canvas.coords(linefleche_down1_3,439/1200*width, 233/630*height, 447/1200*width, 243/630*height)
    canvas.coords(linefleche_down1_4,454/1200*width, 232/630*height, 447/1200*width, 243/630*height)
    canvas.coords(down_0,403/1200*width, 250/630*height)
    canvas.itemconfigure(down_0, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(down_250,340/1200*width, 165/630*height)
    canvas.itemconfigure(down_250, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(down_500,445/1200*width, 80/630*height)
    canvas.itemconfigure(down_500, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(down_750,555/1200*width, 165/630*height)
    canvas.itemconfigure(down_750, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(down_1000,520/1200*width, 245/630*height)
    canvas.itemconfigure(down_1000, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(aiguille_down,448/1200*width, 200/630*height, 448/1200*width, 200/630*height)
    canvas.coords(speed_txt_down,446/1200*width, 168/630*height)
    canvas.itemconfigure(speed_txt_down, font=("Robot", int(13/630*height),"bold"))
    canvas.coords(bouton_down_rond,401/1200*width, 272/630*height, 426/1200*width, 293/630*height)
    canvas.coords(bouton_down_rond1,465/1200*width, 272/630*height, 490/1200*width, 293/630*height)
    canvas.coords(bouton_down1,412/1200*width, 272/630*height, 478/1200*width, 293/630*height)
    canvas.coords(bouton_down_rond2,401/1200*width, 267/630*height, 426/1200*width, 288/630*height)
    canvas.coords(bouton_down_rond3,465/1200*width, 267/630*height, 490/1200*width, 288/630*height)
    canvas.coords(bouton_down2,412/1200*width, 267/630*height, 478/1200*width, 288/630*height)
    canvas.coords(txt_down,447/1200*width, 278/630*height)
    canvas.itemconfigure(txt_down, font=("Robot", int(11/630*height),"bold")) 
    canvas.coords(trait_4,412/1200*width, 267/630*height, 478/1200*width, 267/630*height)
    canvas.coords(trait_6,412/1200*width, 288/630*height, 478/1200*width, 288/630*height)
    canvas.coords(trait_5,412/1200*width, 293/630*height, 478/1200*width, 293/630*height)
    canvas.coords(cercle_up,685/1200*width, 95/630*height, 850/1200*width, 245/630*height)
    canvas.coords(cercle_up2,705/1200*width, 110/630*height, 830/1200*width, 230/630*height)
    canvas.coords(polygone_up,740/1200*width, 247/630*height, 
                                751/1200*width, 211/630*height,
                                785/1200*width, 209/630*height, 
                                795/1200*width, 247/630*height)
    canvas.coords(carre_fleche_up1,752/1200*width, 218/630*height, 782/1200*width, 248/630*height)
    canvas.coords(linefleche_up1_1,757/1200*width, 243/630*height, 778/1200*width, 243/630*height)
    canvas.coords(linefleche_up1_2,767/1200*width, 223/630*height, 767/1200*width, 243/630*height)
    canvas.coords(linefleche_up1_3,767/1200*width, 223/630*height, 774/1200*width, 233/630*height)
    canvas.coords(linefleche_up1_4,767/1200*width, 223/630*height, 760/1200*width, 233/630*height)
    canvas.coords(up_0,723/1200*width, 250/630*height)
    canvas.itemconfigure(up_0, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(up_250,660/1200*width, 165/630*height)
    canvas.itemconfigure(up_250, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(up_500,765/1200*width, 80/630*height)
    canvas.itemconfigure(up_500, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(up_750,875/1200*width, 165/630*height)
    canvas.itemconfigure(up_750, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(up_1000,840/1200*width, 245/630*height)
    canvas.itemconfigure(up_1000, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(aiguille_up,768/1200*width, 168/630*height, 768/1200*width, 168/630*height)
    canvas.coords(speed_txt_up,766/1200*width, 168/630*height)
    canvas.itemconfigure(speed_txt_up, font=("Robot", int(13/630*height),"bold"))
    canvas.coords(bouton_up_rond2,721/1200*width, 272/630*height, 746/1200*width, 293/630*height)
    canvas.coords(bouton_up_rond3,785/1200*width, 272/630*height, 810/1200*width, 293/630*height)
    canvas.coords(bouton_up2,732/1200*width, 272/630*height, 798/1200*width, 293/630*height)
    canvas.coords(bouton_up1,721/1200*width, 267/630*height, 746/1200*width, 288/630*height)
    canvas.coords(bouton_up2_,785/1200*width, 267/630*height, 810/1200*width, 288/630*height)
    canvas.coords(bouton_up3,732/1200*width, 267/630*height, 798/1200*width, 288/630*height)
    canvas.coords(txt_up,767/1200*width, 278/630*height)
    canvas.itemconfigure(txt_up, font=("Robot", int(11/630*height),"bold")) 
    canvas.coords(trait_7,732/1200*width, 267/630*height, 798/1200*width, 267/630*height)
    canvas.coords(trait_8,732/1200*width, 288/630*height, 798/1200*width, 288/630*height)
    canvas.coords(trait_9,732/1200*width, 293/630*height, 798/1200*width, 293/630*height)
    
    # MODULE LOGO
    canvas.coords(module3_1,975/1200*width, 15/630*height, 1180/1200*width, 320/630*height)
    canvas.coords(module3,980/1200*width, 20/630*height, 1175/1200*width, 320/630*height)
    canvas.coords(logo_carré,1010/1200*width, 58/630*height, 1140/1200*width, 170/630*height)
    canvas.coords(oval1,1010/1200*width, 45/630*height, 1053/1200*width, 70/630*height)
    canvas.coords(oval2,1053/1200*width, 45/630*height, 1097/1200*width, 70/630*height)
    canvas.coords(oval3,1097/1200*width, 45/630*height, 1139/1200*width, 70/630*height)
    canvas.coords(logo_carré2,1010/1200*width, 30/630*height, 1140/1200*width, 59/630*height)
    canvas.coords(pointe,1010/1200*width, 170/630*height, 
                        1013/1200*width, 184/630*height,
                        1015/1200*width, 188/630*height, 
                        1027/1200*width, 203/630*height,
                        1044/1200*width, 215/630*height, 
                        1053/1200*width, 220/630*height,
                        1075/1200*width, 223/630*height,
                        1096/1200*width, 220/630*height, 
                        1105/1200*width, 215/630*height,
                        1122/1200*width, 203/630*height, 
                        1134/1200*width, 188/630*height,
                        1137/1200*width, 184/630*height,
                        1140/1200*width, 170/630*height)
    canvas.coords(trait7,1011/1200*width, 169/630*height, 1139/1200*width, 170/630*height)
    canvas.coords(trait8,1010/1200*width, 170/630*height, 1013/1200*width, 184/630*height)
    canvas.coords(trait9,1013/1200*width, 184/630*height, 1015/1200*width, 188/630*height)
    canvas.coords(trait10,1015/1200*width, 188/630*height, 1027/1200*width, 203/630*height)
    canvas.coords(trait11,1027/1200*width, 203/630*height, 1044/1200*width, 215/630*height)
    canvas.coords(trait12,1044/1200*width, 215/630*height, 1053/1200*width, 220/630*height)
    canvas.coords(trait13,1053/1200*width, 220/630*height, 1075/1200*width, 223/630*height)
    canvas.coords(trait14,1075/1200*width, 223/630*height, 1096/1200*width, 220/630*height)
    canvas.coords(trait15,1096/1200*width, 220/630*height, 1105/1200*width, 215/630*height)
    canvas.coords(trait16,1105/1200*width, 215/630*height, 1122/1200*width, 203/630*height)
    canvas.coords(trait17,1122/1200*width, 203/630*height, 1134/1200*width, 188/630*height)
    canvas.coords(trait18,1134/1200*width, 188/630*height, 1137/1200*width, 184/630*height)
    canvas.coords(trait19,1137/1200*width, 184/630*height, 1140/1200*width, 170/630*height)
    canvas.coords(trait20,1056/1200*width, 169/630*height, 1072/1200*width, 182/630*height)
    canvas.coords(trait21,1070/1200*width, 182/630*height, 1101/1200*width, 155/630*height)
    canvas.coords(txt_VPN,1074/1200*width, 122/630*height)
    canvas.itemconfigure(txt_VPN, font=("Robot", int(20/630*height),"bold"))
    canvas.coords(bouton_send,1020/1200*width, 271/630*height, 1131/1200*width, 305/630*height)
    canvas.coords(bouton_send_rond_,1002/1200*width, 270/630*height, 1050/1200*width, 305/630*height)
    canvas.coords(bouton_send_rond2_,1102/1200*width, 270/630*height, 1150/1200*width, 305/630*height)
    canvas.coords(bouton_send1,1020/1200*width, 265/630*height, 1131/1200*width, 300/630*height)
    canvas.coords(bouton_send_rond,1002/1200*width, 265/630*height, 1050/1200*width, 300/630*height)
    canvas.coords(bouton_send_rond2,1102/1200*width, 265/630*height, 1150/1200*width, 300/630*height)
    canvas.coords(txt_send,1079/1200*width, 284/630*height)
    canvas.itemconfigure(txt_send, font=("Robot", int(13/630*height),"bold"))
    canvas.coords(trait_1,1020/1200*width, 265/630*height, 1131/1200*width, 265/630*height)
    canvas.coords(trait_2,1020/1200*width, 300/630*height, 1131/1200*width, 300/630*height)
    canvas.coords(trait_3,1020/1200*width, 305/630*height, 1131/1200*width, 305/630*height)
    
    # Module USER
    canvas.coords(module4_1,15/1200*width, 325/630*height, 220/1200*width, 625/630*height)
    canvas.coords(module4,20/1200*width, 330/630*height, 215/1200*width, 620/630*height)
    canvas.coords(user,80/1200*width, 420/630*height, 
                        153/1200*width, 420/630*height,
                        153/1200*width, 403/630*height, 
                        140/1200*width, 395/630*height,
                        93/1200*width, 395/630*height, 
                        93/1200*width, 395/630*height,
                        80/1200*width, 403/630*height)
    canvas.coords(trait1,80/1200*width, 420/630*height, 153/1200*width, 420/630*height)
    canvas.coords(trait2,153/1200*width, 420/630*height, 153/1200*width, 403/630*height)
    canvas.coords(trait3,153/1200*width, 403/630*height, 140/1200*width, 395/630*height)
    canvas.coords(trait4,140/1200*width, 395/630*height, 93/1200*width, 395/630*height)
    canvas.coords(trait5,93/1200*width, 395/630*height, 80/1200*width, 403/630*height)
    canvas.coords(trait6,80/1200*width, 403/630*height, 80/1200*width, 420/630*height)
    canvas.coords(tete_user,98/1200*width, 360/630*height, 135/1200*width, 395/630*height)
    canvas.coords(txt_user,115/1200*width, 345/630*height)
    canvas.itemconfigure(txt_user, font=("Robot", int(10/630*height),"bold"))
    canvas.coords(txt_pseudo,100/1200*width, 455/630*height)
    canvas.itemconfigure(txt_pseudo, font=("Robot", int(10/630*height),"bold"))
    canvas.coords(txt_ip,84/1200*width, 490/630*height)
    canvas.itemconfigure(txt_ip, font=("Robot", int(10/630*height),"bold"))
    canvas.coords(txt_connexion,114/1200*width, 525/630*height)
    canvas.itemconfigure(txt_connexion, font=("Robot", int(10/630*height),"bold"))
    canvas.coords(bouton_console_rond,50/1200*width, 581/630*height, 75/1200*width, 605/630*height)
    canvas.coords(bouton_console_rond2,160/1200*width, 581/630*height, 185/1200*width, 605/630*height)
    canvas.coords(bouton_console1,61/1200*width, 582/630*height, 175/1200*width, 605/630*height)
    canvas.coords(bouton_console_rond_,50/1200*width, 576/630*height, 75/1200*width, 600/630*height)
    canvas.coords(bouton_console_rond2_,160/1200*width, 576/630*height, 185/1200*width, 600/630*height)
    canvas.coords(bouton_console,61/1200*width, 577/630*height, 175/1200*width, 600/630*height)
    canvas.coords(txt_console,119/1200*width, 588/630*height)
    canvas.itemconfigure(txt_console, font=("Robot", int(11/630*height),"bold"))
    canvas.coords(trait_10,61/1200*width, 576/630*height, 175/1200*width, 576/630*height)
    canvas.coords(trait_11,61/1200*width, 600/630*height, 175/1200*width, 600/630*height)
    canvas.coords(trait_12,61/1200*width, 605/630*height, 175/1200*width, 605/630*height)
    
    # MODULE TRAFIC RÉSEAU
    canvas.coords(module5_1,975/1200*width, 325/630*height, 1180/1200*width, 625/630*height)
    canvas.coords(module5,980/1200*width, 330/630*height, 1175/1200*width, 620/630*height)
    canvas.coords(line_1,373/1200*width, 410/630*height, 829/1200*width, 410/630*height)
    canvas.coords(line_2,373/1200*width, 460/630*height, 829/1200*width, 460/630*height)
    canvas.coords(line_3,373/1200*width, 510/630*height, 829/1200*width, 510/630*height)
    canvas.coords(line_4,373/1200*width, 560/630*height, 829/1200*width, 560/630*height)
    canvas.coords(line_5,373/1200*width, 410/630*height, 373/1200*width, 560/630*height)
    canvas.coords(line_6,439/1200*width, 410/630*height, 439/1200*width, 560/630*height)
    canvas.coords(line_7,504/1200*width, 410/630*height, 504/1200*width, 560/630*height)
    canvas.coords(line_8,569/1200*width, 410/630*height, 569/1200*width, 560/630*height)
    canvas.coords(line_9,634/1200*width, 410/630*height, 634/1200*width, 560/630*height)
    canvas.coords(line_10,699/1200*width, 410/630*height, 699/1200*width, 560/630*height)
    canvas.coords(line_11,764/1200*width, 410/630*height, 764/1200*width, 560/630*height)
    canvas.coords(line_12,829/1200*width, 410/630*height, 829/1200*width, 560/630*height)
    canvas.coords(txt_trafic,600/1200*width, 350/630*height)
    canvas.itemconfigure(txt_trafic, font=("Robot", int(10/630*height),"bold"))
    canvas.coords(trafic_0GB,353/1200*width, 555/630*height)
    canvas.itemconfigure(trafic_0GB, font=("Robot", int(9/630*height),"bold"))
    canvas.coords(trafic_20GB,350/1200*width, 505/630*height)
    canvas.itemconfigure(trafic_20GB, font=("Robot", int(9/630*height),"bold"))
    canvas.coords(trafic_40GB,350/1200*width, 455/630*height)
    canvas.itemconfigure(trafic_40GB, font=("Robot", int(9/630*height),"bold"))
    canvas.coords(trafic_60GB,350/1200*width, 405/630*height)
    canvas.itemconfigure(trafic_60GB, font=("Robot", int(9/630*height),"bold"))
    canvas.coords(point1,438/1200*width, 377/630*height, 453/1200*width, 392/630*height)
    canvas.coords(point2,688/1200*width, 377/630*height, 703/1200*width, 392/630*height)
    canvas.coords(txt_point1,495/1200*width, 385/630*height)
    canvas.itemconfigure(txt_point1, font=("Robot", int(9/630*height),"bold"))
    canvas.coords(txt_point2,750/1200*width, 385/630*height)
    canvas.itemconfigure(txt_point2, font=("Robot", int(9/630*height),"bold"))
    cursor.execute("SELECT * FROM trafic ORDER BY date DESC")
    rows = cursor.fetchall()
    nb_ligne = len(rows)
    print(nb_ligne)
    space_size = 438 
    if nb_ligne >=1:
        row0 = rows[0]
        pourcentage_up =  (row0[1]*100) / 1_500_000 
        pourcentage_down =  (row0[2]*100) / 1_500_000
        canvas.coords(som1,(space_size-7)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size)/1200*width,560/630*height)
        canvas.coords(som2,(space_size)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size+7)/1200*width,560/630*height)
        canvas.coords(date0,space_size/1200*width,570/630*height)
        space_size = space_size +65
        nb_ligne = nb_ligne -1
        if nb_ligne >= 1:
            row0 = rows[1]
            pourcentage_up =  (row0[1]*100) / 1_500_000 
            pourcentage_down =  (row0[2]*100) / 1_500_000
            canvas.coords(som3,(space_size-7)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size)/1200*width,560/630*height)
            canvas.coords(som4,(space_size)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size+7)/1200*width,560/630*height)
            canvas.coords(date1,space_size/1200*width,570/630*height)
            space_size = space_size +65
            nb_ligne = nb_ligne -1
            if nb_ligne >= 1:
                row0 = rows[2]
                pourcentage_up =  (row0[1]*100) / 1_500_000 
                pourcentage_down =  (row0[2]*100) / 1_500_000
                canvas.coords(som5,(space_size-7)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size)/1200*width,560/630*height)
                canvas.coords(som6,(space_size)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size+7)/1200*width,560/630*height)
                canvas.coords(date2,space_size/1200*width,570/630*height)
                space_size = space_size +65
                nb_ligne = nb_ligne -1
                if nb_ligne >= 1:
                    row0 = rows[3]
                    pourcentage_up =  (row0[1]*100) / 1_500_000 
                    pourcentage_down =  (row0[2]*100) / 1_500_000
                    canvas.coords(som7,(space_size-7)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size)/1200*width,560/630*height)
                    canvas.coords(som8,(space_size)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size+7)/1200*width,560/630*height)
                    canvas.coords(date3,space_size/1200*width,570/630*height)
                    space_size = space_size +65
                    nb_ligne = nb_ligne -1
                    if nb_ligne >= 1:
                        row0 = rows[4]
                        pourcentage_up =  (row0[1]*100) / 1_500_000 
                        pourcentage_down =  (row0[2]*100) / 1_500_000
                        canvas.coords(som9,(space_size-7)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size)/1200*width,560/630*height)
                        canvas.coords(som10,(space_size)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size+7)/1200*width,560/630*height)
                        canvas.coords(date4,space_size/1200*width,570/630*height)
                        space_size = space_size +65
                        nb_ligne = nb_ligne -1
                        if nb_ligne >= 1:
                            row0 = rows[5]
                            pourcentage_up =  (row0[1]*100) / 1_500_000 
                            pourcentage_down =  (row0[2]*100) / 1_500_000
                            canvas.coords(som11,(space_size-7)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size)/1200*width,560/630*height)
                            canvas.coords(som12,(space_size)/1200*width ,(560-98*(pourcentage_up)/100)/630*height,(space_size+7)/1200*width,560/630*height)
                            canvas.coords(date5,space_size/1200*width,570/630*height)
                            space_size = space_size +65
                            nb_ligne = nb_ligne -1
   
    
    # MODULE DATA
    canvas.coords(module6_1,294/1200*width, 325/630*height, 907/1200*width, 620/630*height)
    canvas.coords(module6,299/1200*width, 330/630*height, 902/1200*width, 615/630*height)
    canvas.coords(DATA_txt,1077/1200*width, 345/630*height)
    canvas.itemconfigure(DATA_txt, font=("Robot", int(10/630*height),"bold"))
    canvas.coords(bouton1_mail2,995/1200*width,385/630*height,1035/1200*width,425/630*height)
    canvas.coords(bouton2_mail,995/1200*width, 380/630*height, 1035/1200*width, 420/630*height)
    canvas.coords(txt_mail,1014/1200*width, 400/630*height)
    canvas.itemconfigure(txt_mail,font=("Robot", int(25/630*height)))
    canvas.coords(dessin_mail,1005/1200*width, 388/630*height, 1024/1200*width, 412/630*height)
    canvas.coords(notif,1016/1200*width, 385/630*height, 1026/1200*width, 395/630*height)


#* Cette fonction permet de calculer le mouvement de l'aiguille
#* Paramètres : speed = vitesse récupérer 
#*              x_,y_,x1_,y1_ = position du rectangle qui représente l'aiguille
#*              max = valeure maximum à laquelle le compteur peut aller 
def update_speed(speed,x_,y_,x1_,y1_,aiguille,max):        
    # conversion de la vitesse en angle de l'aiguille
    angle = math.radians(speed * 270 / 100 + 155)
    
    # calcul des coordonnées de l'aiguille en fonction de l'angle
    x = x_+ 55 * math.cos(angle)
    y = y_ + 55 * math.sin(angle)
    x1 = x1_ + 20* math.cos(angle)
    y2 = y1_ + 20 * math.sin(angle)
    
    # récupération de la taille de la fenêtre et redimensionnement des coordonnées en conséquence
    width, height = get_window_size()
    width = int(width)
    height = int(height)
    canvas.coords(aiguille, int(x1)/1200*width, int(y2)/630*height, int(x)/1200*width, int(y)/630*height)

#* Cette fonction permet de modifier la position de l'aiguille et lui donner une impression de mouvement
#* Paramètres : X = vitesse récupérer 
#*              x,y,x1,y1 = position du rectangle qui représente l'aiguille
#*              speed_txt = texte qui indique la vitesse
#*              aiguille  = élément du canvas qui réference le rectangle de l'aiguille
def compteur(X,x,y,x1,y1,speed_txt,aiguille):
    current_speed = 0
    if X > 100:
        X = 100
    # Boucle pour parcourir toutes les valeurs de vitesse
    while True:
        # Met à jour la position de l'aiguille pour refléter la vitesse actuelle
        update_speed(current_speed,x,y,x1,y1,aiguille,X)
        # Met à jour l'affichage de la fenêtre
        fenetre.update()
        # Met à jour le texte pour afficher la vitesse actuelle
        canvas.itemconfigure(speed_txt, text=current_speed)
        # Augmente la vitesse actuelle de 1
        current_speed +=1
        # Pause d'une petite fraction de seconde pour créer une animation fluide
        time.sleep(1/100)
        
         # Si la vitesse actuelle est égale à la vitesse maximale, commence à décrémenter jusqu'à la vitesse X
        if current_speed == 100:
            while current_speed != X:
                # Décrémente la vitesse actuelle de 1
                current_speed -=1
                # Met à jour la position de l'aiguille pour refléter la nouvelle vitesse actuelle
                update_speed(current_speed,x,y,x1,y1,aiguille,X)
                # Met à jour le texte pour afficher la nouvelle vitesse actuelle
                canvas.itemconfigure(speed_txt, text=current_speed)
                # Pause d'une petite fraction de seconde pour créer une animation fluide
                time.sleep(1/100)
                # Met à jour l'affichage de la fenêtre
                fenetre.update()
            # Sort de la boucle while si la vitesse actuelle est égale à la vitesse X
            break  

#?##########################################################################################################################################
#?-----------------------------------------------INTERACTION AVEC LE SERVEUR VIA L'INTERFACE-----------------------------------------------#
#?##########################################################################################################################################

#* Cette fonction permet de gérer les interaction entre l'utilisateur et le système
#* Paramètre : event = les coordonnées du clique de la souris
def clicked (event) :
    global compt
    global jeton
    global statut
    global console
    global connecte 
    global ip_address
    global key_partaged
    global console_window
    global premier_connexion
    
    # On recupère la taille actuelle de la fenêtre pour dessiner les éléments nécessaire à la bonne proportion
    # mais aussi pour tester le clique propotionnelement si la fenêtre a été agrandie ou rétréci
    width, height = get_window_size()
    width = int(width)
    height = int(height)
    
    #! Tous les tests sont effectués par rapport aux coordonnées du clique 
    
    # BOUTON CONNEXION 
    if 65/1200*width < event.x < 165/1200*width and 65/630*height < event.y < 165/630*height and statut == 0:
        # Si c'est la première connexion de l'utilisateur après avoir lancé le programme
        if premier_connexion == 0:
            
            # Simple connexion au serveur
            connecte = connexion(host,port)
            
            # Si la connection a réussi 
            if connecte:
                
                # Modification des éléments du canvas pour le bouton ON/OFF
                canvas.itemconfigure(bouton_module1_3,fill="green")
                canvas.itemconfigure(dessin_ON_OFF_module1,fill="green")
                canvas.itemconfigure(txt_module1, text='Connecté')
                
                # Echange des clés avec la fonction Diffie-Hellman
                key_partaged = Diffie_Hellman_Key()
                
                # Vérifiaction de la signature
                rep = verif_Signature(key_partaged)
                if rep :
                    Signature(key_partaged)
                    if console_window.winfo_exists():
                        if console.winfo_exists():
                            console.insert("end","Les clés ont bien été échangées !\n","green")
                    premier_connexion =  1
                    statut = 1
                else:
                    if console.winfo_exists():
                        console.insert("end","La signature n'est pas validée, votre connexion n'est pas sécurisée !\n","red")
                    deconnexion()
                    return False
        else: 
            # Si ce n'est pas la premiere connexion lance la fonction reconnection
            connecte = reconnection(host,port)
            
            # Si la reconnexion s'est bien passée
            if connecte:
                
                # Modification des éléments du canvas pour le bouton ON/OFF
                canvas.itemconfigure(bouton_module1_3,fill="green")
                canvas.itemconfigure(dessin_ON_OFF_module1,fill="green")
                canvas.itemconfigure(txt_module1, text='Connecté')
                
                # Echange des clés avec la fonction Diffie-Hellman
                key_partaged = Diffie_Hellman_Key()
                console.insert("end","Les clés ont bien été échangées !\n","green")
                
                # Vérifiaction de la signature
                rep = verif_Signature(key_partaged)
                if rep :
                    Signature(key_partaged)
                    if console_window.winfo_exists():
                        if console.winfo_exists():
                            console.insert("end","Les clés ont bien été échangées !\n","green")
                    premier_connexion =  1
                    statut = 1
                else:
                    if console.winfo_exists():
                        console.insert("end","La signature n'est pas validée, votre connexion n'est pas sécurisée !\n","red")
                    deconnexion()
                    return False
                statut =1
    
    # BOUTON DECONNEXION        
    elif 65/1200*width < event.x < 165/1200*width and 65/630*height < event.y < 165/630*height and statut == 1:
        
        # Mise à jour des différents flags
        statut = 0
        connecte = 0
        
        # Modification des éléments du canvas pour le bouton ON/OFF
        canvas.itemconfigure(bouton_module1_3,fill="red")
        canvas.itemconfigure(dessin_ON_OFF_module1,fill="red")
        canvas.itemconfigure(txt_module1, text='Déconnecté')
        
        # Message console
        if console_window.winfo_exists(): 
            console.insert("end","Vous n'êtes plus connecté au serveur.\n","red")
        
        # Lancement de la fonction deconnexion
        deconnexion()
        
    # SPEEDTEST DOWNLOAD
    elif 388/1200*width < event.x< 506/1200*width and 268/630*height < event.y< 298/630*height and jeton == 0:
        
        # Mise à jour des différents flags
        jeton = 1 # permet de bloquer l'exécution uniquement sur ce speedtest
        
        # Modification des éléments du canvas pour le bouton du speedtest download
        canvas.coords(bouton_down_rond2,401/1200*width, 272/630*height, 426/1200*width, 293/630*height)
        canvas.coords(bouton_down_rond3,465/1200*width, 272/630*height, 490/1200*width, 293/630*height)
        canvas.coords(bouton_down2,412/1200*width, 272/630*height, 478/1200*width, 293/630*height)
        canvas.coords(txt_down,447/1200*width, 283/630*height) 
        canvas.coords(trait_4,412/1200*width, 272/630*height, 478/1200*width, 272/630*height)
        canvas.coords(trait_6,412/1200*width, 293/630*height, 478/1200*width, 293/630*height)
        fenetre.update()
        time.sleep(1/10)
        canvas.coords(bouton_down1,412/1200*width, 272/630*height, 478/1200*width, 293/630*height)
        canvas.coords(bouton_down_rond2,401/1200*width, 267/630*height, 426/1200*width, 288/630*height)
        canvas.coords(bouton_down_rond3,465/1200*width, 267/630*height, 490/1200*width, 288/630*height)
        canvas.coords(bouton_down2,412/1200*width, 267/630*height, 478/1200*width, 288/630*height)
        canvas.coords(txt_down,447/1200*width, 278/630*height) 
        canvas.coords(trait_4,412/1200*width, 267/630*height, 478/1200*width, 267/630*height)
        canvas.coords(trait_6,412/1200*width, 288/630*height, 478/1200*width, 288/630*height)
        fenetre.update()
        
        # Si le client est connecté
        if connecte:
            
            # Lancement du speedtest
            speed = speedTestDownload(vpn_client)
            
            # Message console 
            if console.winfo_exists():
                console.insert("end","Débit de transmission en download: "+str(speed)+" Mbps.\n","blue")
                
            # Mise en route du compteur pour l'animation
            compteur(speed,448,168,448,168,speed_txt_down,aiguille_down)  
        else:
            # Si le client n'est pas connecté il ne peut pas faire de speedtest 
            # Fenêtre pop-up erreur
            messagebox.showerror("Erreur", "Vous devez être connecté au serveur pour lancer des tests.")
            
            # Message console 
            if console.winfo_exists():
                console.insert("end","Vous devez être connecté au serveur pour lancer des tests.\n","red")
        # Mise à jour des différents flags
        jeton = 0 # relache la priorité
        
    # SPEEDTEST DOWNLOAD    
    elif 710/1200*width < event.x< 823/1200*width and 270/630*height < event.y< 295/630*height and jeton == 0:
        
        # Mise à jour des différents flags
        jeton = 1
        
        # Modification des éléments du canvas pour le bouton du speedtest upload
        canvas.coords(bouton_up1,721/1200*width, 272/630*height, 746/1200*width, 293/630*height)
        canvas.coords(bouton_up2_,785/1200*width, 272/630*height, 810/1200*width, 293/630*height)
        canvas.coords(bouton_up3,732/1200*width, 272/630*height, 798/1200*width, 293/630*height)
        canvas.coords(txt_up,767/1200*width, 283/630*height)
        canvas.coords(trait_7,732/1200*width, 272/630*height, 798/1200*width, 272/630*height)
        canvas.coords(trait_8,732/1200*width, 293/630*height, 798/1200*width, 293/630*height)
        fenetre.update()
        time.sleep(1/10)
        canvas.coords(bouton_up1,721/1200*width, 267/630*height, 746/1200*width, 288/630*height)
        canvas.coords(bouton_up2_,785/1200*width, 267/630*height, 810/1200*width, 288/630*height)
        canvas.coords(bouton_up3,732/1200*width, 267/630*height, 798/1200*width, 288/630*height)
        canvas.coords(txt_up,767/1200*width, 278/630*height)
        canvas.coords(trait_7,732/1200*width, 267/630*height, 798/1200*width, 267/630*height)
        canvas.coords(trait_8,732/1200*width, 288/630*height, 798/1200*width, 288/630*height)
        fenetre.update()
        
        # Si le client est connecté
        if connecte:
            
            # Lancement du speedtest
            speed = speedTestUpload(vpn_client)
            
            # Message console 
            if console.winfo_exists():
                console.insert("end","Débit de transmission en upload: "+str(speed)+" Mbps.\n","blue")
                
            # Mise en route du compteur pour l'animation
            compteur(speed,768,168,768,168,speed_txt_up,aiguille_up)
        else:
            
            # Si le client n'est pas connecté il ne peut pas faire de speedtest 
            # Fenêtre pop-up erreur
            messagebox.showerror("Erreur", "Vous devez être connecté au serveur pour lancer des tests.")
            
            # Message console 
            if console.winfo_exists():
                console.insert("end","Vous devez être connecté au serveur pour lancer des tests.\n","red")
        
        # Mise à jour des différents flags
        jeton = 0
        
    # BOUTON ENVOIE DE FICHIER    
    elif 1020/1200*width < event.x< 1131/1200*width and 266/630*height < event.y< 300/630*height:
        
        # Modification des éléments du canvas pour le bouton pour envoyer un fichier 
        canvas.coords(bouton_send_rond,1002/1200*width, 270/630*height, 1050/1200*width, 305/630*height)
        canvas.coords(bouton_send_rond2,1102/1200*width, 270/630*height, 1150/1200*width, 305/630*height)
        canvas.coords(bouton_send1,1020/1200*width, 271/630*height, 1131/1200*width, 305/630*height)
        canvas.coords(txt_send,1079/1200*width, 289/630*height)
        canvas.coords(trait_1,1020/1200*width, 270/630*height, 1131/1200*width, 270/630*height)
        canvas.coords(trait_2,1020/1200*width, 305/630*height, 1131/1200*width, 305/630*height)
        fenetre.update()
        time.sleep(1/10)
        canvas.coords(bouton_send1,1020/1200*width, 265/630*height, 1131/1200*width, 300/630*height)
        canvas.coords(bouton_send_rond,1002/1200*width, 265/630*height, 1050/1200*width, 300/630*height)
        canvas.coords(bouton_send_rond2,1102/1200*width, 265/630*height, 1150/1200*width, 300/630*height)
        canvas.coords(txt_send,1079/1200*width, 284/630*height)
        canvas.coords(trait_1,1020/1200*width, 265/630*height, 1131/1200*width, 265/630*height)
        canvas.coords(trait_2,1020/1200*width, 300/630*height, 1131/1200*width, 300/630*height)
        fenetre.update()
        
        # Si le client est connecté 
        if connecte :
            
            # Lancement du processus pour envoyer un fichier 
            file=send_file()
            ip_address = ip_window(file)
            
        else: # Sinon fenêtre pop-up d'erreur
            messagebox.showerror("Erreur", "Vous devez être connecté au serveur pour envoyé des fichiers.")
            
            # Message console   
            if console.winfo_exists():
                console.insert("end","Vous devez être connecté au serveur pour ouvrir cette application.\n","red")
            
    # BOUTON OUVRIR CONSOLE        
    elif 50/1200*width < event.x< 185/1200*width and 581/630*height < event.y< 605/630*height:
        
        # Modification des éléments du canvas pour le bouton pour envoyer un fichier 
        canvas.coords(bouton_console_rond_,50/1200*width, 581/630*height, 75/1200*width, 605/630*height)
        canvas.coords(bouton_console_rond2_,160/1200*width, 581/630*height, 185/1200*width, 605/630*height)
        canvas.coords(bouton_console,61/1200*width, 582/630*height, 175/1200*width, 605/630*height)
        canvas.coords(txt_console,119/1200*width, 593/630*height)
        canvas.coords(trait_10,61/1200*width, 581/630*height, 175/1200*width, 581/630*height)
        canvas.coords(trait_11,61/1200*width, 605/630*height, 175/1200*width, 605/630*height)
        fenetre.update()
        time.sleep(1/10)
        canvas.coords(bouton_console_rond_,50/1200*width, 576/630*height, 75/1200*width, 600/630*height)
        canvas.coords(bouton_console_rond2_,160/1200*width, 576/630*height, 185/1200*width, 600/630*height)
        canvas.coords(bouton_console,61/1200*width, 577/630*height, 175/1200*width, 600/630*height)
        canvas.coords(txt_console,119/1200*width, 588/630*height)
        canvas.coords(trait_10,61/1200*width, 576/630*height, 175/1200*width, 576/630*height)
        canvas.coords(trait_11,61/1200*width, 600/630*height, 175/1200*width, 600/630*height)
        fenetre.update()
        
        # Lancement de la fonction pour ouvrir la console (pas besoin d'être connecté)
        open_console(connecte)
        
    # BOUTON OUVRIR MAIL
    elif 995/1200*width < event.x < 1035/1200*width and 380/630*height < event.y < 420/630*height:
        
        # Modification des éléments du canvas pour le bouton pour ouvrir la boite mail
        canvas.coords(bouton1_mail2,995/1200*width,385/630*height,1035/1200*width,425/630*height)
        canvas.coords(bouton2_mail,995/1200*width,385/630*height,1035/1200*width,425/630*height)
        canvas.coords(txt_mail,1014/1200*width,405/630*height)
        canvas.coords(dessin_mail,1005/1200*width,393/630*height,1024/1200*width,417/630*height)
        fenetre.update()
        time.sleep(1/10)
        canvas.coords(bouton1_mail2,995/1200*width,385/630*height,1035/1200*width,425/630*height)
        canvas.coords(bouton2_mail,995/1200*width,380/630*height,1035/1200*width,420/630*height)
        canvas.coords(txt_mail,1014/1200*width,400/630*height)
        canvas.coords(dessin_mail,1005/1200*width,388/630*height,1024/1200*width,412/630*height)
        
        # Si le client est connecté 
        if connecte :
            
            # Lancement de la fonction pour ouvrir la boite mail 
            open_mail()
            
        else: # Sinon fenêtre pop-up d'erreur 
            messagebox.showerror("Erreur", "Vous devez être connecté au serveur pour ouvrir cette application.")   
            
            # Message console   
            if console.winfo_exists():
                console.insert("end","Vous devez être connecté au serveur pour ouvrir cette application.\n","red")
    
    #* PROCESSUS DE RECUPERATION DE MAILS EN RECEPTIONS
    if connecte:    
        try:
            # Vérifier l'état du socket
            error = vpn_client.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if error != 0:
                raise socket.error(error)
            
            # Envoyer un paquet de données au serveur
            signal = "recv msg ok"
            send_data(vpn_client,signal.encode(),key_partaged)
            
            # Reçoit le nombre de message en attente côté serveur
            nb_msg = recv_message(vpn_client,key_partaged)
            nb_msg = nb_msg.decode()
            print(nb_msg)
            # Si il y a au moins un message 
            if nb_msg != "0":
                
                # Message console
                if console.winfo_exists():
                    console.insert("end","il y a ",nb_msg," message(s) en attente(s)...\n","orange")
            
            # S'il n'y a aucun message 
            if nb_msg == "0":
                
                # Envoi un signal spécifique pour annuler la reception de quelconque message
                signal = "no"
                send_data(vpn_client,signal.encode(),key_partaged)
                
            else: 
                # Modification des éléments du canvas pour le bouton pour envoyer un fichier 
                canvas.coords(notif,1016/1200*width, 385/630*height, 1026/1200*width, 395/630*height)
                canvas.itemconfigure(notif,fill="red",width=1)
                fenetre.update()
                
                # Envoi d'un signal spécifique pour continuer le processus et recevoir le/les messages
                signal = "yes"
                send_data(vpn_client,signal.encode(),key_partaged)
                
                signal = "ok"
                int_msg = int(nb_msg)
                
                # Repète le processus autant de fois qu'il y a de messages
                for i in range(int_msg):
                    
                    # Reception de la source
                    source = recv_message(vpn_client,key_partaged)
                    send_data(vpn_client,signal.encode(),key_partaged)
                    
                    # Reception du sujet du mail
                    subject = recv_message(vpn_client,key_partaged)
                    send_data(vpn_client,signal.encode(),key_partaged)
                    
                    # Reception du corps du message
                    text = recv_message(vpn_client,key_partaged)
                    send_data(vpn_client,signal.encode(),key_partaged)
                    
                    # Recupère le nombre de message déjà présent dans la BDD pour calculer l'id de prochain
                    cursor.execute('SELECT COUNT(*) FROM email_client')
                    resultat = cursor.fetchone()
                    
                    # Si il n'y a aucun message dans la BDD
                    if (resultat[0] == 0):
                        last_id = 0
                    else:
                        
                        # On prend l'id max 
                        cursor.execute("SELECT MAX(id) FROM email_client")
                        last_id = cursor.fetchone()[0]
                        
                    # Ajout du message dans la BDD
                    cursor.execute("""INSERT INTO email_client (id,source, subject, text,open) VALUES (?, ?, ?, ?, ?)""", 
                                (last_id+1,source.decode(), subject.decode(), text.decode(),False))
                    conn.commit()
                    
                # Message console
                if console.winfo_exists():        
                    console.insert("end","Les messages ont bien été reçus, vous pouvez les consulter dans voitre boite mail.\n","orange")
        
        except socket.error as e:
            # Gestion de l'erreur si la connexion est interrompue
            print("La connexion a été interrompue. Erreur :", e)
    
    #* PROCESSUS DE RECUPERATION DE FICHIERS EN RECEPTIONS
    if connecte:
        try:
            # Vérifier l'état du socket
            error = vpn_client.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if error != 0:
                print("je suis deco")
                raise socket.error(error)
            
            # Envoyer un paquet de données au serveur
            signal = "recv file ok"
            send_data(vpn_client,signal.encode(),key_partaged)
            
            # Recption du nombre de fichier stocké en BDD côté serveur
            nb_file = recv_message(vpn_client,key_partaged)
            nb_file = nb_file.decode()
            print(nb_file)
            # S'il y a au moins un fichier 
            if nb_file != "0":
                
                # Message console
                if console.winfo_exists():
                    console.insert("end","il y a ",nb_file," fichier(s) en attente(s)...\n","orange")
            
            # S'il n'y a pas de fichier        
            if nb_file == "0":
                
                # Envoie d'un signal pour sortir du processus 
                signal = "no"
                send_data(vpn_client,signal.encode(),key_partaged)
            else:
                
                # Envoie d'un signal pour continuer le processus et recuperer les fichiers
                signal = "oui"
                send_data(vpn_client,signal.encode(),key_partaged)
                
                # ON repète ce processus autant de fois qu'il y a de fichiers à recevoir
                for i in range(int(nb_file)):
                    
                    # Lancement de la fonction pour recevoir le fichier
                    rep = ReceptionFile(key_partaged)
                    
                # Message console 
                if console.winfo_exists():
                    console.insert("end","Les fichiers ont bien été reçus, vous pouvez les retrouver dans le dossier courant.\n","orange")
        
        except socket.error as e:
            # Gestion de l'erreur si la connexion est interrompue
            print("La connexion a été interrompue. Erreur :", e)
               

#?##########################################################################################################################################
#?------------------------------------------------------------FONCTIONS BACKEND------------------------------------------------------------#
#?##########################################################################################################################################

#* Cette fonction permet de convertir une chaine binaire en entier et retourne cet entier
#* Paramètre : binary = chaine binaire à convertir
def binary2int(binary):
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
    "Convertit un nombre en binaire"
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

    # Convertir le hash en hexadécimal
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
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    print("message recu : ",plaintext)
    return plaintext

#* Cette fonction permet de recevoir des données et de les déchiffrer
#* Paramètres : client_connection = socket de connexion du client duquel sont reçues les données
#*              key = clé à utiliser pour le déchiffrement
def recv_message(client_connection,key):
    
    # Reception du paquet
    data_obj = client_connection.recv(1024)
    
    # Déserialization du paquet
    data_obj_deserialized = pickle.loads(data_obj)
    
    # Récupérer les données dans différentes variables
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
def keyCalculated(client_private_key,server_public_key,p,g):
    return server_public_key ** client_private_key % p

#* Cette fonction permet d'envoi un fichier plus ou moins lourds
#* Paramètres : name_file = nom du fichier à envoyer 
#*              file = fichier à envoyer
#*              ip = adresse ip du client à qui envoyer le fichier
def sendFile(file,ip):  
    global console
    global console_window
    i = 1
    
    # Envoie d'un premier signal pour annoncé que la fonction est lancé
    signal = "send file"
    send_data(vpn_client,signal.encode(),key_partaged)
    
    # Ajout de la taille des données pour le diagramme
    add_data_upload(cursor,len(signal.encode()),now)
    
    # Envoie d'un signal pour me dire que le client est prêt à recevoir les paquets
    rep = recv_message(vpn_client,key_partaged)
    
    # Définissions de la taille du fichier
    octets = os.path.getsize(file) / 870
    
    # Envoie de l'adresse IP
    send_data(vpn_client,ip.encode(),key_partaged)
    
    # Vérifiaction des informations
    print ("\n---> Fichier à envoyer : '" + file + "' [" + str(octets) + " Ko]")
    
    # Message console
    console.insert("end","Fichier à envoyer : " + file + " [" + str(octets) + " Ko]\n","orange")
    
    # Sotckage du nom du fichier (extrait de chemin courant reçu)
    tmp = "NAME " + file + "OCTETS " + str(octets)
    
    # Envoie des informations du fichiers qui va être envoyé
    send_data(vpn_client,tmp.encode(),key_partaged)
    
    # Ajout de la taille des données pour le diagramme
    add_data_upload(cursor,len(tmp.encode()),now) 
    
    
    while (vpn_client.connect):
        tmp = recv_message(vpn_client,key_partaged)
        add_data_download(cursor,len(tmp),now)
        recu = tmp.decode() 
        if not recu : return False

        # Si le serveur accepte on envoi le fichier
        if recu == "GO": 
            
            # Message console
            if console.winfo_exists():
                console.insert("end","Transfert en cours veuillez patienter...\n","orange")
            
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
                        print("Donné à envoyé : ",donnees)   
                        
                        # Envoi du fichier par paquet de 1024 octets
                        send_data(vpn_client,donnees.decode('utf-8', errors='ignore').encode('utf-8'),key_partaged)
                        
                        # Reception du signal pour continuer
                        recv_message(vpn_client,key_partaged)
                        
                        # Ajout de la taille des données pour le diagramme
                        add_data_upload(cursor,len(donnees),now) 
                        num = num + 870
                        remaining_data -= 870
                
                        # Condition pour afficher le % du transfert (pas trouve mieu) :
                        if pourcent == 0 and num > octets / 100 * 10 and num < octets / 100 * 20:
                            if console.winfo_exists():
                                console.insert("end","10%\n","orange")
                            pourcent = 1
                        elif pourcent == 1 and num > octets / 100 * 20 and num < octets / 100 * 30:
                            if console.winfo_exists():
                                console.insert("end","20%\n","orange")
                            pourcent = 2
                        elif pourcent < 3 and num > octets / 100 * 30 and num < octets / 100 * 40:
                            if console.winfo_exists():
                                console.insert("end","30%\n","orange")
                            pourcent = 3
                        elif pourcent < 4 and num > octets / 100 * 40 and num < octets / 100 * 50:
                            if console.winfo_exists():
                                console.insert("end","40%\n","orange")
                            pourcent = 4
                        elif pourcent < 5 and num > octets / 100 * 50 and num < octets / 100 * 60:
                            if console.winfo_exists():
                                console.insert("end","50%\n","orange")
                            pourcent = 5
                        elif pourcent < 6 and num > octets / 100 * 60 and num < octets / 100 * 70:
                            if console.winfo_exists():
                                console.insert("end","60%\n","orange")
                            pourcent = 6
                        elif pourcent < 7 and num > octets / 100 * 70 and num < octets / 100 * 80:
                            if console.winfo_exists():
                                console.insert("end","70%\n","orange")
                            pourcent = 7
                        elif pourcent < 8 and num > octets / 100 * 80 and num < octets / 100 * 90:
                            if console.winfo_exists():
                                console.insert("end","80%\n","orange")
                            pourcent = 8
                        elif pourcent < 9 and num > octets / 100 * 90 and num < octets / 100 * 100:
                            if console.winfo_exists():
                                console.insert("end","90%\n","orange")              
                            pourcent = 9
                    else:# Sinon on arrive à la fin du fichier
                        # Lecture dans le fichier
                        donnees = fich.read(int(remaining_data))  
                        
                        # Envoie des données au serveur
                        send_data(vpn_client,donnees,key_partaged)
                        
                        # Reception du signal pour continuer
                        rep = recv_message(vpn_client,key_partaged)
                        
                        # Ajout de la taille des données pour le diagramme
                        add_data_upload(cursor,len(donnees),now) 
                        
                        # Message console
                        if console.winfo_exists():
                                console.insert("end","100%\n","orange")
                        break  
                        
            else: # Sinon on envoi tous d'un coup
                # Lecture dans le fichier
                donnees = fich.read()
                
                # Envoi des données au serveur
                send_data(vpn_client,donnees,key_partaged)
                
                # Ajout de la taille des données pour le diagramme
                add_data_upload(cursor,len(donnees),now) 
                
                # Reception du signal pour continuer
                recv_message(vpn_client,key_partaged)

            fich.close()
            
            # Message console
            if console.winfo_exists():
                console.insert("end","Transfert du fichier terminé !\n","orange")
                
            # Envoi du signal pour informer que l'envoi du fichier est terminé
            signal2 = "bye"
            send_data(vpn_client,signal2.encode(),key_partaged)
            
            # Ajout de la taille des données pour le diagramme
            add_data_upload(cursor,len(signal2.encode()),now) 
            return True
        else:# Sinon problème de synchronisation
            if console.winfo_exists():
                console.insert("end","Transfert du fichier annulé.\n","orange")
            return "BYE"

#* Cette fonction permet la reception de fichier plus ou moins lourds
#* Paramètre : key_partaged = clé à utiliser pour le déchiffrement
def ReceptionFile(key_partaged):
    num = 0
    pourcent = 0
    accepte = "non"
    signal = "recu"
    global id_file
    
    # Reception d"un premier signal
    ip = recv_message(vpn_client,key_partaged)
    
    # Envoi d'un premier signal avant reception des paquets
    send_data(vpn_client,signal.encode(),key_partaged)
    
    # Tant que la connection avec le client est établie
    while (vpn_client.connect):
        
        # Reception des paquets
        recu = ""
        recu = recv_message(vpn_client,key_partaged)
        
        # Ajout de la taille des données pour le diagramme
        add_data_download(cursor,len(recu),now) 
        
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
                
                # Envoi du signal pour signaler la bonne reception du paquet 
                signal = "GO"
                send_data(vpn_client,signal.encode(),key_partaged)
                print (time.strftime("\n---> [%H:%M] réception du fichier en cours veuillez patienter..."))
                f = open(nom_fichier, "wb")
                accepte = "oui"
                taille = float(taille) * 1024 # Conversion de la taille en octets pour le %

        elif recu.decode() == "bye": # Si on a recu "BYE" le transfer est termine

            # Message console
            if console.winfo_exists():
                console.insert("end","100%\n","orange")
                                
            f.close()
            print (time.strftime("\n---> Le %d/%m a %H:%M réception du fichier termine !"))
            break
        
        else: # Sinon on ecrit au fur et a mesure dans le fichier
            
            # Ecriture du paquet reçu dans le fichier tampon
            f.write(recu)
           
            # Envoi d'un signal pour continuer
            signal="ok"
            send_data(vpn_client,signal.encode(),key_partaged)
            
            if taille > 1024: # Si la taille est plus grande que 1024 on s'occupe du %

                # Condition pour afficher le % du transfert :
                if pourcent == 0 and num > taille / 100 * 10 and num < taille / 100 * 20:
                    # Message console
                    if console.winfo_exists():
                        console.insert("end","10%\n","orange")
                    pourcent = 1
                elif pourcent == 1 and num > taille / 100 * 20 and num < taille / 100 * 30:
                    # Message console
                    if console.winfo_exists():
                        console.insert("end","20%\n","orange")
                    pourcent = 2
                elif pourcent < 3 and num > taille / 100 * 30 and num < taille / 100 * 40:
                   # Message console
                    if console.winfo_exists():
                        console.insert("end","30%\n","orange")
                    pourcent = 3
                elif pourcent < 4 and num > taille / 100 * 40 and num < taille / 100 * 50:
                    # Message console
                    if console.winfo_exists():
                        console.insert("end","40%\n","orange")
                    pourcent = 4
                elif pourcent < 5 and num > taille / 100 * 50 and num < taille / 100 * 60:
                    # Message console
                    if console.winfo_exists():
                        console.insert("end","50%\n","orange")
                    pourcent = 5
                elif pourcent < 6 and num > taille / 100 * 60 and num < taille / 100 * 70:
                    # Message console
                    if console.winfo_exists():
                        console.insert("end","60%\n","orange")
                    pourcent = 6
                elif pourcent < 7 and num > taille / 100 * 70 and num < taille / 100 * 80:
                    # Message console
                    if console.winfo_exists():
                        console.insert("end","70%\n","orange")
                    pourcent = 7
                elif pourcent < 8 and num > taille / 100 * 80 and num < taille / 100 * 90:
                    # Message console
                    if console.winfo_exists():
                        console.insert("end","80%\n","orange")
                    pourcent = 8
                elif pourcent < 9 and num > taille / 100 * 90 and num < taille / 100 * 100:
                    # Message console
                    if console.winfo_exists():
                        console.insert("end","90%\n","orange")         
                    pourcent = 9
                    
                num = num + 1024
    
    return True
    
#* Cette fonction permet de lancer le processus d'échange de donnée calculé pour obtenir une vitesse en Mbit/s
#* Paramètre : vpn_client = socket du client 
def speedTestUpload(vpn_client):
    duration = 0
    taille_bits = 0
    file = open("sauvegarde.txt","rb")
    
    # Envoi d'un premier singal pour commencer
    answer="speedtest upload"
    send_data(vpn_client,answer.encode(),key_partaged)
    
    # Reception d'un signal pour commencer
    recu = recv_message(vpn_client,key_partaged)
    
    if recu.decode() == "GO":
        
        # Lance le timer 
        start = time.time()
        
        # Boucle sur 50 échanges
        for i in range(50):
            data = file.read(870) # Lecture du fichier en 1024 octets
            taille_bits += sys.getsizeof(data) * 8 
            
            # Envoi des données 
            send_data(vpn_client,data,key_partaged)
            
            # Ajout de la taille des données pour le diagramme
            add_data_upload(cursor,len(data),now)  
            
            # Reception d'un signal pour continuer
            recu = recv_message(vpn_client,key_partaged)
            
            # Ajout de la taille des données pour le diagramme
            add_data_download(cursor,len(recu),now) 
        
        # Fin du timer 
        end = time.time()
        
        # Calcul du temps 
        duration += (end - start)
        
        # Envoi d'un signal pour signaler la fin
        signal = "quit"
        send_data(vpn_client,signal.encode(),key_partaged)
        
        # Calcul de la vitesse
        download_speed = ((taille_bits / duration)*8)/1_000_000
        return int(download_speed)

#* Cette fonction permet de lancer le processus d'échange de donnée calculé pour obtenir une vitesse en Mbit/s
#* Paramètre : vpn_client = socket du client 
def speedTestDownload(vpn_client):
    duration = 0
    taille_bits = 0
    
    # Envoi d'un premier singal pour commencer
    answer="speedtest download"
    send_data(vpn_client,answer.encode(),key_partaged)
    
    # Ajout de la taille des données pour le diagramme
    add_data_upload(cursor,len(answer),now) 
    
    # Lance le timer 
    start = time.time()
    
    # Boucle sur 50 échanges
    for i in range(50):
        signal = "OK"
        
        # Reception des données
        data = recv_message(vpn_client,key_partaged)
        
        # Ajout de la taille des données pour le diagramme
        add_data_download(cursor,len(data),now)
        taille_bits += sys.getsizeof(data) * 8
        
        # Envoi d'un signal pour continuer
        send_data(vpn_client,signal.encode(),key_partaged)
        
        # Ajout de la taille des données pour le diagramme
        add_data_upload(cursor,len(signal),now) 
        
    # Fin du timer 
    end = time.time()   
    
    # Calcul du temps 
    duration += (end - start)

    # Calcul de la vitesse
    download_speed = ((taille_bits / duration)*8) / 1_000_000
    
    return int(download_speed)

#* Cette fonction permet de connecter le socket du client au socket du serveur 
#* Paramètres : host = adresse ip du serveur
#*              port = port de connexion ouvert sur le serveur serveur
def connexion(host,port):  
    global console_window
    global console
    
    # Si le serveur existe 
    try:
        vpn_client.connect((host, port)) 
        
        # Message console 
        if console_window.winfo_exists():
            console.insert("end","Connexion au serveur établie !\n","green")
        print("\n--------->Connexion au serveur établie!")
        return True
    except: # Erreur lors de la tentative de connexion
        print ("---------> le serveur '" + host + "' est introuvable.")
        
        # Message console
        if console_window.winfo_exists():
            console.insert("end", "Le serveur '" + host + "' est introuvable.\n","red")
        return False  

#* Cette fonction permet de se déconnecter proprement du serveur auquel il est connecté
def deconnexion():
    
    # Envoi d'un signal pour informer de la déconnexion
    signal = "exit"
    send_data(vpn_client,signal.encode(),key_partaged)
    
    # Ajout de la taille des données pour le diagramme
    add_data_upload(cursor,len(signal.encode()),now)
    
    # Déconnexion et fermeture du socket
    vpn_client.shutdown(socket.SHUT_RDWR)
    vpn_client.close() 
    
#* Cette fonction peremet de se reconnecter proprement à une session déjà ouverte dans la même exécution du programme
#* Paramètres : host = adresse ip du serveur
#*              port = port de connexion ouvert sur le serveur serveur
def reconnection(host, port):
    global vpn_client
    
    # On initialise vpn_client avec une socket TCP/IP
    vpn_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # On définit un délai de 2 secondes pour le timeout de la socket
    vpn_client.settimeout(2)
    
    # On appelle la fonction connexion avec les paramètres host et port pour établir la connexion VPN
    connexion(host, port)
    return True

#* Cette fonction permet d'ajouter la taille des données qui ont été échangé à la BDD pour alimenter le diagramme du trafic réseau
#* Paramètres :  cursor : curseur de la base de données
#*               size_data : taille des données à ajouter
#*               date : date à laquelle les données ont été échangées
def add_data_upload(cursor,size_data,date):
    
    # Recupère la valeurs de la somme des données uploadé jusque là
    cursor.execute("SELECT som_up FROM trafic WHERE date = ?",(date,))
    result = cursor.fetchone()
    
    # Si la somme upload vaut 0
    if result == None:
        # On ajoute juste la taille des données
        cursor.execute("UPDATE trafic SET som_up = ? WHERE date = ?", (size_data, date))
        conn.commit()
        
    else:
        # Sinon, on ajoute la taille des données à la somme déjà enregistré
        som = result[0] + size_data
        print("j'ajoute")
        cursor.execute("UPDATE trafic SET som_up = ? WHERE date = ?", (som, date))
        conn.commit()

#* Cette fonction permet d'ajouter la taille des données qui ont été échangé à la BDD pour alimenter le diagramme du trafic réseau
#* Paramètres :  cursor : curseur de la base de données
#*               size_data : taille des données à ajouter
#*               date : date à laquelle les données ont été échangées
def add_data_download(cursor,size_data,date):
    
    # Recupère la valeurs de la somme des données uploadé jusque là
    cursor.execute("SELECT som_down FROM trafic WHERE date = ?",(date,))
    result = cursor.fetchone()
    
    # Si la somme upload vaut 0
    if result == None:
        # On ajoute juste la taille des données
        cursor.execute("UPDATE trafic SET som_down = ? WHERE date = ?", (size_data, date))
        conn.commit()
    else:
        # Sinon, on ajoute la taille des données à la somme déjà enregistré
        som = result[0] + size_data
        cursor.execute("UPDATE trafic SET som_down = ? WHERE date = ?", (som, date))
        conn.commit()

   
#* Cette fonction permet d'échanger les clés qui permettront un chiffrement/déchiffrement sécurisé selon la méthode de Diffie-Hellman
def Diffie_Hellman_Key():
    
    # Réception des paramètres de Diffie-Hellman en binaire
    parameters_bytes = vpn_client.recv(1024)

    # Parsing des données
    parameters = struct.unpack('!2i',parameters_bytes)
    p = parameters[0]
    g = parameters[1]

    # Choix d'une clé privé aléatoire entre 1 et 1000
    client_private_key = random.randint(2,10)

    # Calcul de la clé publique de Diffie-Hellman pour le client
    client_public_key = (g ** client_private_key) % p 

    # Serialiation de la clé
    client_public_key_binary = str(int2binary(client_public_key)).encode()

    # Envoie de la clé publique du client au serveur
    vpn_client.sendall(client_public_key_binary)

    # Réception de la clé public du client
    server_public_key_byte = vpn_client.recv(1024)

    # Déserialisation de la clé publique du client
    server_public_key_binary = server_public_key_byte.decode()
    server_public_key = binary2int(server_public_key_binary)

    # Calcul de la clé paratagée
    key_partaged = keyCalculated(client_private_key,server_public_key,p,g)
    
    # Génération du hachage de la clé partagée
    h = hashlib.sha256(str(key_partaged).encode())
    key_16 = h.hexdigest()[:16]

    return key_16.encode()


#* Cette fonction permet de signer un message est de l'envoyer au destinataire qui devra la vérifier de son côté
#* Paramètre : key_partaged = clé à utiliser pour le chiffrement
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
    send_data(vpn_client,signature,key_partaged)
    
    # Reception d'un signal pour continuer
    recv_message(vpn_client,key_partaged)
    
    # Convertir la clé publique en bytes
    keypub_bytes = key.publickey().export_key()
    
    # Envoie de la clé publique pour déchiffrer
    send_data(vpn_client, keypub_bytes, key_partaged)

#* Cette fonction permet de vérifier la signature d'un message reçu 
#* Paramètres : key_partaged = clé à utiliser pour le déchiffrement
def verif_Signature(key_partaged):
    # Message à signer
    message = b"Hello, world!"

    # Hash du message
    h = SHA256.new(message)
    
    # Réception du messsage signé
    signature = recv_message(vpn_client,key_partaged)
    
    # ENvoi d'un signal pour continuer 
    signal = "ok signature"
    send_data(vpn_client,signal.encode(),key_partaged)
    
    # Réception de la clé publique pour déchiffrer la signature
    keypub_bytes = recv_message(vpn_client,key_partaged)
    keypub = RSA.import_key(keypub_bytes)
    
    # Vérifier la signature avec la clé publique
    try:
        pkcs1_15.new(keypub).verify(h, signature)
        print("La signature est valide.")
        return True
    except (ValueError, TypeError):
        print("La signature est invalide.")
        return False

#?##########################################################################################################################################
#?--------------------------------------------------------CRÉATION DE LA BASE DE DONNÉES---------------------------------------------------#
#?##########################################################################################################################################
date = 0
now = datetime.now()
now = now.strftime("%d%m%Y")
print(now)
conn = sqlite3.connect("ma_base_de_donnees.db")
cursor = conn.cursor()

# Je créée la base de donnée si elle n'existe pas 
# Si elle est vide => signifie que c'est la première connexion du client
cursor.execute("CREATE TABLE IF NOT EXISTS trafic (date INTEGER PRIMARY KEY, som_up INTEGER,som_down INTEGER)")

cursor.execute("""CREATE TABLE IF NOT EXISTS email_client (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            source TEXT NOT NULL,
                                                            subject TEXT NOT NULL,
                                                            text TEXT NOT NULL, 
                                                            open boolean)""")

cursor.execute("CREATE TABLE IF NOT EXISTS contacts (ip TEXT NOT NULL PRIMARY KEY, ad_mail TEXT NOT NULL)")

# Récupère la nombre d'éléments (jours avec des données) dans le trafic réseau
cursor.execute("SELECT COUNT(*) FROM trafic")
result = cursor.fetchone()

if result[0] == 0:
    # La table utilisateurs est vide. C'est la première connexion de l'utilisateur
    # Insert une nouvelle ligne 
    cursor.execute("INSERT INTO trafic (date, som_up, som_down) VALUES (?,?,?)", (now, 0, 0))
    conn.commit()
else:
    # La table utilisateurs n'est pas vide
    # Recupère le nombre d'éléments enregistré dans la table avec la date actuel
    cursor.execute("SELECT COUNT(*) FROM trafic WHERE date=?",(now,))
    result = cursor.fetchone()
    print(result[0])
    # Je vérifie si le client s'est déjà connecté aujourd'hui ou pas
    if result[0] <= 0:
        # Le client ne s'est pas connecté aujourd'hui
        # Insert une nouvelle ligne
        cursor.execute("INSERT INTO trafic (date, som_up, som_down) VALUES (?,?,?)", (now, 0, 0))
        conn.commit()

#?##########################################################################################################################################
#?---------------------------------------------------------CRÉATION DE L'INTERFACE---------------------------------------------------------#
#?##########################################################################################################################################

#* Création de la fenêtre de l'application
fenetre = Tk()
fenetre['bg'] =  '#372589'
fenetre.geometry("1200x630")
centrefenetre(fenetre)
img = Image.open("img.png")
img = img.resize((2200,1000), Image.BICUBIC)
img = ImageTk.PhotoImage(img)

#* Création d'un canevas qui va contenir tous les éléments de dessins de l'application
canvas = Canvas(fenetre, width=2688, height=1856, background='#372589',borderwidth=0,highlightthickness=0)
image = canvas.create_image(0,0,anchor=NW,image=img)
canvas.pack(fill=BOTH, expand=YES)
width = fenetre.winfo_width()
height = fenetre.winfo_height()

#* Module 1 : Bouton ON/OFF 
module1_1 = canvas.create_rectangle(0, 0, 0, 0, fill="#2d1c76", width=0)
module1= canvas.create_rectangle(0, 0, 0, 0, fill="#412589", width=1)
bouton_module1_1 = canvas.create_oval(0, 0, 0, 0, fill="#a4c2f4", width=1)
bouton_module1_2 = canvas.create_oval(0, 0, 0, 0, fill="#2d1c76", width=1)
bouton_module1_3 = canvas.create_oval(0, 0, 0, 0, fill="red", width=1)
bouton_module1_4= canvas.create_oval(0, 0, 0, 0, fill="#2d1c76", width=1)
dessin_ON_OFF_module1 = canvas.create_rectangle(0, 0, 0, 0, width=1, fill="red")
txt_module1 = canvas.create_text(0, 0, text="Déconnecté",font="Robot 13 bold" ,fill="white")

#* REctangle de fond des différents modules
module2_1 = canvas.create_rectangle(0, 0, 0, 0,fill="#2d1c76",width=0)
module2 = canvas.create_rectangle(0, 0, 0, 0,fill="#412589",width=1)
module3_1 = canvas.create_rectangle(0, 0, 0, 0,fill="#2d1c76",width=0)
module3= canvas.create_rectangle(0, 0, 0, 0,fill="#412589",width=1)
module4_1 = canvas.create_rectangle(0, 0, 0, 0,fill="#2d1c76",width=0)
module4 = canvas.create_rectangle(0, 0, 0, 0,fill="#412589",width=1)
module5_1 = canvas.create_rectangle(0, 0, 0, 0,fill="#2d1c76",width=0)
module5 = canvas.create_rectangle(0, 0, 0, 0,fill="#412589",width=1)
module6_1 = canvas.create_rectangle(0, 0, 0, 0,fill="#2d1c76",width=0)
module6 = canvas.create_rectangle(0, 0, 0, 0,fill="#412589",width=1)

#* Bloc DATA
DATA_txt = canvas.create_text(0,0, text="APPLICATIONS", font="Robot 13 bold", fill="white")

#* Symbole flèche
user = canvas.create_polygon(0, 0, 0, 0,0, 0, 0, 0,0, 0, 0, 0,fill='#a4c2f4')
trait1 = canvas.create_line(0, 0, 0, 0,width=2)
trait2 = canvas.create_line(0, 0, 0, 0,width=2)
trait3 = canvas.create_line(0, 0, 0, 0,width=2)
trait4 = canvas.create_line(0, 0, 0, 0,width=2)
trait5 = canvas.create_line(0, 0, 0, 0,width=2)
trait6 = canvas.create_line(0, 0, 0, 0,width=2)

#* Bloc USER
tete_user = canvas.create_oval(0, 0, 0, 0,fill="#a4c2f4",width=2)
txt_user = canvas.create_text(0, 0, text="USER", font="Robot 13 bold", fill="white")
txt_pseudo = canvas.create_text(0, 0, text="Pseudo : User_24", font="Robot 10 bold", fill="white")
# Récupère l'adresse IP de la machine locale
adresse_ip = socket.gethostbyname(socket.gethostname())
txtIP = "IP : "+str(adresse_ip)
txt_ip = canvas.create_text(0, 0, text=txtIP, font="Robot 10 bold", fill="white")

# Exécution de la requête SELECT
cursor.execute("SELECT * FROM trafic ORDER BY date DESC LIMIT 1;")
derniere_ligne = cursor.fetchone()
txtdate="Dernière connexion : \n"+ str(derniere_ligne[0])
print(txtdate)
txt_connexion = canvas.create_text(0, 0, text=txtdate, font="Robot 10 bold", fill="white")



#* Logo VPN
logo_carré = canvas.create_rectangle(0, 0, 0, 0,fill="#a4c2f4",width=2)
oval1 = canvas.create_oval(0, 0, 0, 0,fill="#412589",width=2)
oval2 = canvas.create_oval(0, 0, 0, 0,fill="#412589",width=2)
oval3 = canvas.create_oval(0, 0, 0, 0,fill="#412589",width=2)
logo_carré2 = canvas.create_rectangle(0, 0, 0, 0,fill="#412589",width=0)
pointe = canvas.create_polygon(0, 0,
                               0, 0,
                               0, 0,
                               0, 0,
                               0, 0,
                               0, 0,
                               0, 0,
                               0, 0,
                               0, 0,
                               0, 0,
                               0, 0,
                               0, 0,
                               0, 0,fill="#a4c2f4")
trait7 = canvas.create_rectangle(0, 0, 0, 0,width=0,fill="#a4c2f4")
trait8 = canvas.create_line(0, 0, 0, 0,width=2)
trait9 = canvas.create_line(0, 0, 0, 0,width=2)
trait10 = canvas.create_line(0, 0, 0, 0,width=2)
trait11 = canvas.create_line(0, 0, 0, 0,width=2)
trait12 = canvas.create_line(0, 0, 0, 0,width=2)
trait13 = canvas.create_line(0, 0, 0, 0,width=2)
trait14 = canvas.create_line(0, 0, 0, 0,width=2)
trait15 = canvas.create_line(0, 0, 0, 0,width=2)
trait16 = canvas.create_line(0, 0, 0, 0,width=2)
trait17 = canvas.create_line(0, 0, 0, 0,width=2)
trait18 = canvas.create_line(0, 0, 0, 0,width=2)
trait19 = canvas.create_line(0, 0, 0, 0,width=2)
txt_VPN = canvas.create_text(0, 0, text="VPN", font="Robot 20 bold", fill="black")
trait20 = canvas.create_line(0, 0, 0, 0,width=6)
trait21 = canvas.create_line(0, 0, 0, 0,width=6)

#* Speedtest
txt_speedtest = canvas.create_text(0, 0, text="SPEEDTEST", font="Robot 13 bold", fill="white")
carre_download = canvas.create_rectangle(0, 0, 0, 0, fill="#a4c2f4")
txt_download = canvas.create_text(0, 0,text="DOWNLOAD",font="Robot 14 bold", fill="black")
carre_upload = canvas.create_rectangle(0, 0, 0, 0, fill="#a4c2f4")
txt_upload = canvas.create_text(0, 0,text="UPLOAD",font="Robot 14 bold", fill="black")
cercle_down = canvas.create_oval(0, 0, 0, 0,fill="#a4c2f4",width=1)
cercle_down2 = canvas.create_oval(0, 0, 0, 0,fill="#412589",width=1)

polygone_down = canvas.create_polygon(0, 0, 0, 0,0, 0, 0, 0,fill="#412589")

carre_fleche_down1 = canvas.create_rectangle(0, 0, 0, 0,fill="#a4c2f4")
linefleche_down1_1 = canvas.create_line(0, 0, 0, 0,width=2)
linefleche_down1_2 = canvas.create_line(0, 0, 0, 0,width=2)
linefleche_down1_3 = canvas.create_line(0, 0, 0, 0,width=2)
linefleche_down1_4 = canvas.create_line(0, 0, 0, 0,width=2)

down_0 = canvas.create_text(0, 0, text="0", font=("Arial bold", 12),fill="white")
down_250 = canvas.create_text(0, 0, text="10", font=("Arial bold", 12),fill="white")
down_500 = canvas.create_text(0, 0, text="20", font=("Arial bold", 12),fill="white")
down_750 = canvas.create_text(0, 0, text="30", font=("Arial bold", 12),fill="white")
down_1000 = canvas.create_text(0, 0, text="40+", font=("Arial bold", 12),fill="white")


aiguille_down = canvas.create_line(0, 0, 0, 0, fill="#a4c2f4",width=5)

speed_txt_down = canvas.create_text(0, 0, text='', font=("Robot bold", 15))

cercle_up = canvas.create_oval(0, 0, 0, 0,fill="#a4c2f4",width=1) #320
cercle_up2 = canvas.create_oval(0, 0, 0, 0,fill="#412589",width=1)

polygone_up = canvas.create_polygon(0, 0, 0, 0,0, 0, 0, 0,fill="#412589")

carre_fleche_up1 = canvas.create_rectangle(0, 0, 0, 0,fill="#a4c2f4")
linefleche_up1_1 = canvas.create_line(0, 0, 0, 0,width=2)
linefleche_up1_2 = canvas.create_line(0, 0, 0, 0,width=2)
linefleche_up1_3 = canvas.create_line(0, 0, 0, 0,width=2)
linefleche_up1_4 = canvas.create_line(0, 0, 0, 0,width=2)

up_0 = canvas.create_text(0, 0,text="0", font=("Arial bold", 12),fill="white")
up_250 = canvas.create_text(0, 0, text="10", font=("Arial bold", 12),fill="white")
up_500 = canvas.create_text(0, 0, text="20", font=("Arial bold", 12),fill="white")
up_750 = canvas.create_text(0, 0, text="30", font=("Arial bold", 12),fill="white")
up_1000 = canvas.create_text(0, 0, text="40+", font=("Arial bold", 12),fill="white")

aiguille_up = canvas.create_line(0, 0, 0, 0, fill="#a4c2f4",width=5)

speed_txt_up = canvas.create_text(0, 0, text='', font=("Robot 13 bold"))

bouton_down_rond = canvas.create_oval(1002,270,1050,305, fill="#6ea1f6",width=1)
bouton_down_rond1 = canvas.create_oval(1002,270,1050,305, fill="#6ea1f6",width=1)
bouton_down1 = canvas.create_rectangle(0, 0, 0, 0, fill="#6ea1f6",width=0)

bouton_down_rond2 = canvas.create_oval(1002,270,1050,305, fill="#a4c2f4",width=1)
bouton_down_rond3 = canvas.create_oval(1002,270,1050,305, fill="#a4c2f4",width=1)
bouton_down2 = canvas.create_rectangle(0, 0, 0, 0, fill="#a4c2f4",width=0)
txt_down = canvas.create_text(449,283,text="Test", font=("Arial 13 bold"))

trait_4 = canvas.create_line(1020,265,1131,265,width=1)
trait_5 = canvas.create_line(1020,300,1131,300,width=1)
trait_6 = canvas.create_line(1020,305,1131,305,width=1)

bouton_up_rond2 = canvas.create_oval(1002,270,1050,305, fill="#6ea1f6",width=1)
bouton_up_rond3 = canvas.create_oval(1002,270,1050,305, fill="#6ea1f6",width=1)
bouton_up2 = canvas.create_rectangle(0, 0, 0, 0, fill="#6ea1f6",width=0)

bouton_up1 = canvas.create_oval(1002,270,1050,305, fill="#a4c2f4",width=1)
bouton_up2_ = canvas.create_oval(1002,270,1050,305, fill="#a4c2f4",width=1)
bouton_up3 = canvas.create_rectangle(0, 0, 0, 0, fill="#a4c2f4",width=0)
txt_up = canvas.create_text(449,283,text="Test", font=("Arial 13 bold"))

trait_7 = canvas.create_line(1020,265,1131,265,width=1)
trait_8 = canvas.create_line(1020,300,1131,300,width=1)
trait_9 = canvas.create_line(1020,305,1131,305,width=1)

line_1 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)
line_2 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)
line_3 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)
line_4 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)

line_5 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)
line_6 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)
line_7 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)
line_8 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)
line_9 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)
line_10 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)
line_11 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)
line_12 = canvas.create_line(0, 0, 0, 0,fill="grey",width=2)

bar0 = canvas.create_rectangle(0, 0, 0, 0,fill="grey")
bar1 = canvas.create_rectangle(0, 0, 0, 0,fill="#a4c2f4")
date0 = canvas.create_text(0,0,text='',font="Robot 8 bold")


#* Module diagramme trafic réseau
txt_trafic = canvas.create_text(0, 0, text="TRAFIC USAGE", font="Robot 13 bold", fill="white")

trafic_0GB = canvas.create_text(0, 0, text="0MB", font="Robot 9 bold", fill="white")
trafic_20GB = canvas.create_text(0, 0, text="4MB", font="Robot 9 bold", fill="white")
trafic_40GB = canvas.create_text(0, 0, text="8MB", font="Robot 9 bold", fill="white")
trafic_60GB = canvas.create_text(0, 0, text="12MB", font="Robot 9 bold", fill="white")

point1 = canvas.create_oval(0, 0, 0, 0,fill="#a4c2f4")
point2 = canvas.create_oval(0, 0, 0, 0,fill="#70757d")

txt_point1 = canvas.create_text(0, 0, text="Incoming", font="Robot 9 bold", fill="white")

txt_point2 = canvas.create_text(0, 0, text="Outcoming", font="Robot 9 bold", fill="white")

#* Module envoi fichier
bouton_send_rond_ = canvas.create_oval(1002,270,1050,305, fill="#6ea1f6",width=1)
bouton_send_rond2_ = canvas.create_oval(1102,270,1150   ,305, fill="#6ea1f6",width=1)
bouton_send_rond = canvas.create_oval(1002,265,1050,300, fill="#a4c2f4",width=1)
bouton_send_rond2 = canvas.create_oval(1102,265,1150,300, fill="#a4c2f4",width=1)
bouton_send = canvas.create_rectangle(0, 0, 0, 0, fill="#6ea1f6",width=0)
bouton_send1 = canvas.create_rectangle(0, 0, 0, 0, fill="#a4c2f4",width=0)
txt_send = canvas.create_text(0,0,text="Send File", font=("Arial 13 bold"))

trait_1 = canvas.create_line(1020,265,1131,265,width=1)
trait_2 = canvas.create_line(1020,300,1131,300,width=1)
trait_3 = canvas.create_line(1020,305,1131,305,width=1)

bouton_console_rond = canvas.create_oval(1002,265,1050,300, fill="#6ea1f6",width=1)
bouton_console_rond2 = canvas.create_oval(1102,265,1150,300, fill="#6ea1f6",width=1)
bouton_console_rond_ = canvas.create_oval(1002,270,1050,305, fill="#a4c2f4",width=1)
bouton_console_rond2_ = canvas.create_oval(1102,270,1150   ,305, fill="#a4c2f4",width=1)
bouton_console1 = canvas.create_rectangle(0, 0, 0, 0, fill="#6ea1f6",width=0)
bouton_console = canvas.create_rectangle(0, 0, 0, 0, fill="#a4c2f4",width=0)
txt_console= canvas.create_text(0,0,text="Open Console", font=("Arial 13 bold"))

trait_10 = canvas.create_line(1020,265,1131,265,width=1)
trait_11 = canvas.create_line(1020,300,1131,300,width=1)
trait_12 = canvas.create_line(1020,305,1131,305,width=1)

#* Bouton mail
bouton1_mail2 = canvas.create_rectangle(995,380,1035,425,fill="grey",width=1)
bouton2_mail = canvas.create_rectangle(995,380,1035,420,fill="#a4c2f4",width=1)
txt_mail = canvas.create_text(1014,400,text="M",font="Robot 25")
dessin_mail = canvas.create_rectangle(1005,388,1024,412,width=2)
notif = canvas.create_oval(1016,385,1026,395,fill=None,width=0)




#* Histogramme
bar0 = canvas.create_rectangle(0,0,0,0,fill="#a4c2f4")
bar1 = canvas.create_rectangle(0,0,0,0,fill="grey")

bar0_1 = canvas.create_rectangle(0,0,0,0,fill="#a4c2f4")
bar1_1 = canvas.create_rectangle(0,0,0,0,fill="grey")

bar0_2 = canvas.create_rectangle(0,0,0,0,fill="#a4c2f4")
bar1_2 = canvas.create_rectangle(0,0,0,0,fill="grey")

bar0_3 = canvas.create_rectangle(0,0,0,0,fill="#a4c2f4")
bar1_3 = canvas.create_rectangle(0,0,0,0,fill="grey")

bar0_4 = canvas.create_rectangle(0,0,0,0,fill="#a4c2f4")
bar1_4 = canvas.create_rectangle(0,0,0,0,fill="grey")

bar0_5 = canvas.create_rectangle(0,0,0,0,fill="#a4c2f4")
bar1_5 = canvas.create_rectangle(0,0,0,0,fill="grey")

bar0_6 = canvas.create_rectangle(0,0,0,0,fill="#a4c2f4")
bar1_6 = canvas.create_rectangle(0,0,0,0,fill="grey")

bars = [bar0, bar1]

#* Stockage des données 
cursor.execute("SELECT * FROM trafic ORDER BY date DESC")
rows = cursor.fetchall()
nb_ligne = len(rows)
space_size = 438 

#! Chaque bloc de if vérifie si il y a encore une valeur qui peut être affiché
#! Si c'est le cas, elle suit toujours le même processus pour l'afficher dans le diagramme en décalant la barre et en 
#! changeant la valeur des données
if nb_ligne >=1:
    
    # Récupère la ligne qui correspondra à la date la plus éloigné à celle de aujourd'hui
    row0 = rows[0] 
    
    # Calcul du pourcentage de la barre  pour les données uploadées
    pourcentage_up =  (row0[1]*100) / 1_500_000
    
    # Calcul du pourcentage de la barre  pour les données downloadées
    pourcentage_down =  (row0[2]*100) / 1_500_000
    
    # Création des éléments pour dessiner les deux colonnes avec les b
    som1 = canvas.create_rectangle((space_size-7) ,(560-150*(pourcentage_up)/100),(space_size),560,fill="#a4c2f4")
    som2 = canvas.create_rectangle((space_size) ,(560-(150*(pourcentage_up)/100)),(space_size+152),(560-150*(pourcentage_up)/100-(150*pourcentage_down)/100),fill="grey")
    date0 = canvas.create_text(space_size,570,text=row0[0],font="Robot 8 bold", fill="white")
    
    # Décalage pour les prochaines colonnes
    space_size = space_size +65
    nb_ligne = nb_ligne -1
    if nb_ligne >= 1:
        row0 = rows[1]
        pourcentage_up =  (row0[1]*100) / 1_500_000
        pourcentage_down =  (row0[2]*100) / 1_500_000
        som3 = canvas.create_rectangle((space_size-7) ,(560-150*(pourcentage_up)/100),(space_size+7),560,fill="#a4c2f4")
        som4 = canvas.create_rectangle((space_size-7) ,(560-(150*(pourcentage_up)/100)),(space_size+7),(560-150*(pourcentage_up)/100-(150*pourcentage_down)/100),fill="grey")
        date1 = canvas.create_text(space_size,570,text=row0[0],font="Robot 8 bold", fill="white")
        space_size = space_size +65
        nb_ligne = nb_ligne -1
        if nb_ligne >= 1:
            row0 = rows[2]
            pourcentage_up =  (row0[1]*100) / 1_500_000
            pourcentage_down =  (row0[2]*100) / 1_500_000
            som5 = canvas.create_rectangle((space_size-7) ,(560-150*(pourcentage_up)/100),(space_size+7),560,fill="#a4c2f4")
            som6 = canvas.create_rectangle((space_size-7) ,(560-(150*(pourcentage_up)/100)),(space_size+7),(560-150*(pourcentage_up)/100-(150*pourcentage_down)/100),fill="grey")
            date2 = canvas.create_text(space_size,570,text=row0[0],font="Robot 8 bold", fill="white")
            space_size = space_size +65
            nb_ligne = nb_ligne -1
            if nb_ligne >= 1:
                row0 = rows[3]
                pourcentage_up =  (row0[1]*100) / 1_500_000
                pourcentage_down =  (row0[2]*100) / 1_500_000
                som7 = canvas.create_rectangle((space_size-7) ,(560-150*(pourcentage_up)/100),(space_size+7),560,fill="#a4c2f4")
                som8 = canvas.create_rectangle((space_size-7) ,(560-(150*(pourcentage_up)/100)),(space_size+7),(560-150*(pourcentage_up)/100-(150*pourcentage_down)/100),fill="grey")
                date3 = canvas.create_text(space_size,570,text=row0[0],font="Robot 8 bold", fill="white")
                space_size = space_size +65
                nb_ligne = nb_ligne -1
                if nb_ligne >= 1:
                    row0 = rows[4]
                    pourcentage_up =  (row0[1]*100) / 1_500_000 
                    pourcentage_down =  (row0[2]*100) / 1_500_000
                    som9 = canvas.create_rectangle((space_size-7) ,(560-150*(pourcentage_up)/100),(space_size+7),560,fill="#a4c2f4")
                    som10 = canvas.create_rectangle((space_size-7) ,(560-(150*(pourcentage_up)/100)),(space_size+7),(560-150*(pourcentage_up)/100-(150*pourcentage_down)/100),fill="grey")
                    date4 = canvas.create_text(space_size,570,text=row0[0],font="Robot 8 bold", fill="white")
                    space_size = space_size +65
                    nb_ligne = nb_ligne -1
                    if nb_ligne >= 1:
                        row0 = rows[5]
                        pourcentage_up =  (row0[1]*100) / 1_500_000
                        pourcentage_down =  (row0[2]*100) / 1_500_000
                        som11 = canvas.create_rectangle((space_size-7) ,(560-150*(pourcentage_up)/100),(space_size+7),560,fill="#a4c2f4")
                        som12 = canvas.create_rectangle((space_size-7) ,(560-(150*(pourcentage_up)/100)),(space_size+7),(560-150*(pourcentage_up)/100-(150*pourcentage_down)/100),fill="grey")
                        date5 = canvas.create_text(space_size,570,text=row0[0],font="Robot 8 bold", fill="white")
                        space_size = space_size +65
                        nb_ligne = nb_ligne -1
                        
#?##########################################################################################################################################
#?--------------------------------------------------CRÉATION DES INTERACTIONS DE L'INTERFACE-----------------------------------------------#
#?##########################################################################################################################################
compt = 0
jeton = 0
statut = 0
connecte = False
premier_connexion = 0

# Interaction avec le système 
canvas.bind('<Button>',clicked)

# Mise à jour des formes géométriques lorsque la fenêtre est agrandie
canvas.bind("<Configure>", on_resize)

# Fenêtre pop-up pour confirmer la fermeture de la fenêtre
fenetre.protocol("WM_DELETE_WINDOW", on_closing)

# Initialisation de la fenêtre pour la console
console_window = Toplevel(fenetre)
console_window.title("Nouvelle fenêtre")
console_window.geometry("600x300")
centrefenetre(console_window)
console_window.resizable(False,False)
console_window.attributes("-topmost", True)
console = Text(console_window)
console.tag_config("red", foreground="red")
console.tag_config("white", foreground="white")
console.tag_config("green", foreground="green")
console.tag_config("blue", foreground="blue")
console.tag_config("orange", foreground="orange")
console.config(bg="black")
console.pack()
console_window.withdraw()
console.insert(INSERT, "Bienvenue dans la console\n","white")
consol_stat = 1

# Initialisation de la fenêtre pour la boite mail
window_mail = Toplevel(fenetre)
window_mail.geometry("600x400")
window_mail.title("Application Email")
window_mail.resizable(False,False)
centrefenetre(window_mail)
frame = Frame(window_mail)
frame.pack(side="left", fill="both", expand=True)
mail_list = Listbox(frame)
# Ajout d'une liste de mails
mail_list.pack(fill="both", expand=True)
# Ajout d'un cadre pour contenir les détails du mail sélectionné
details_frame = Frame(window_mail)
details_frame.pack(side="right", fill="both", expand=True)
# Ajout d'un label pour afficher les détails du mail sélectionné
details_label = Label(details_frame, text="Sélectionnez un mail")
details_label.pack(fill="both", expand=True)
window_mail.withdraw()
    

#?##########################################################################################################################################
#?----------------------------------------------------------MISE EN PLACE DU SOCKET--------------------------------------------------------#
#?##########################################################################################################################################

# Paramètres de connexion
host = '127.0.0.1'
port = 24081

# Création du socket client
vpn_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Boucle de la fenêtre principale
fenetre.mainloop()

# Fermeture de la BDD
conn.close()