# coding: utf-8
from ctypes import pythonapi
from datetime import datetime
import hashlib
import os
import pickle
import random
import socket
import struct
import sys
import threading
import time
import math
import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox 
from PIL import Image,ImageTk
from tkinter import filedialog

###########################################################################################################################################
#---------------------------------------------------------FONCTIONS INTERFACE---------------------------------------------------------#
###########################################################################################################################################
def geoliste(g):
    r=[i for i in range(0,len(g)) if not g[i].isdigit()]
    return [int(g[0:r[0]]),int(g[r[0]+1:r[1]]),int(g[r[1]+1:r[2]]),int(g[r[2]+1:])]

def centrefenetre(fen):
    fen.update_idletasks()
    l,h,x,y=geoliste(fen.geometry())
    fen.geometry("%dx%d%+d%+d" % (l,h,(fen.winfo_screenwidth()-l)//2,(fen.winfo_screenheight()-h)//2))

def get_window_size():
    window_geometry = fenetre.winfo_geometry()
    width, height = window_geometry.split("x")[0], window_geometry.split("x")[1].split("+")[0]
    return width, height

def on_closing():
    if messagebox.askyesno("Fermteture de l'application", "Voulez-vous vraiment fermer l'application ? (Vous serez automiquement déconnecté du serveur)", 
                           icon="warning"):
        fenetre.destroy()

# Fonction qui permet d'afficher les fichiers du dossier courant pour choisir celui qui va être envoyé
def send_file():
    filepath = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    return filepath

ip_address = ""

def list_cont():
    cursor.execute("SELECT * FROM contacts ")
    rows = cursor.fetchall()
    list=[]
    for row in rows:
        print(row)
        list.append(row[1])
        print(list)
    return list

def ip_window(file):
    global ip_address
    window_dest = Toplevel(fenetre)
    window_dest.geometry("300x100")
    window_dest.title("Destinataire")
    window_dest.resizable(False,False)
    centrefenetre(window_dest)

    # Ajout d'un label pour l'adresse IP
    ip_label = Label(window_dest, text="Adresse IP:")
    ip_label.pack()
    
    ip_entry = Combobox(window_dest)
    
    list = list_cont()
        
    ip_entry['values'] = list
    ip_entry.pack()

    def close():
        global ip_address
        ip_address = ip_entry.get()
        print(ip_address)
        window_dest.destroy()
        window_dest.quit()
        sendFile(file,ip_address)

    add_button = Button(window_dest, text="Valider", command=close)
    add_button.pack()

    # Démarrage de la boucle principale de la fenêtre
    window_dest.mainloop()


def open_console(connecte):
    global console
    global console_window
    consol_stat = 0
    if console_window.winfo_exists():
        console_window.deiconify()
    else:
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
        console.tag_config("orange", foreground="orange")
        console.tag_config("blue", foreground="blue")
        console.config(bg="black")
        console.pack()
        console.insert(INSERT, "Bienvenue dans la console\n","white")
        if connecte:
            print("je susi connectée")
            console.insert("end","Connexion au serveur établie !\n","green")
        else:
            print("je suis pas")
            console.insert("end","Vous n'êtes plus connecté au serveur.\n","red")

def contacts():
    window_contact = Toplevel(fenetre)
    window_contact.geometry("300x400")
    window_contact.title("Contacts")
    details_contact = Frame(window_contact)
    details_contact.pack()
    cursor.execute("SELECT * FROM contacts ")
    rows = cursor.fetchall()
    frame = Frame(window_contact,height=300)
    frame.pack(side="top",fill="both", expand=True)
    contact_list = Listbox(frame)
    
    # Ajout d'une liste de mails
    if len(rows) > 0:
        # Ajout des contacts dans l'interface
        for row in rows:
            print(row)
            contact_list.insert(0, row[1]+" ("+row[0]+")")
        
    else:
        details_label = Label(details_contact, text="Vous n'avez aucun contact.")     
        details_label.pack()  
    add_button = Button(window_contact, text="Ajouter un contact", command=lambda :add_contact(window_contact))
    add_button.pack(side="bottom",pady=10)
    
    contact_list.pack(side="top",fill="both", expand=True)

def add_contact(window_contact):
    # Code pour ajouter un contact
    add_window = Toplevel(window_contact)
    add_window.geometry("300x200")
    add_window.title("Ajouter un contact")
    ip_label = Label(add_window, text="IP :")
    ip_label.pack(pady=5)
    ip_entry = Entry(add_window)
    ip_entry.pack(pady=5)
    address_label = Label(add_window, text="Adresse :")
    address_label.pack(pady=5)
    address_entry = Entry(add_window)
    address_entry.pack(pady=5)
    
    def close():
        ip = ip_entry.get()
        address = address_entry.get()
        print(ip,address,type(ip))
        cursor.execute("INSERT INTO contacts (ip,ad_mail) VALUES (?,?)", (ip, address))
        window_contact.update()
        add_window.destroy()
    
    add_button = Button(add_window, text="Ajouter", command=close)
    add_button.pack(side="bottom",pady=10)
    
            

def send_mail():
    window_send = Toplevel(fenetre)
    window_send.geometry("800x600")
    window_send.title("Envoi d'e-mail")

    # Ajout d'un label pour la destination de l'e-mail
    dest_label = Label(window_send, text="Destinataire :")
    dest_label.grid(row=0, column=0, padx=10, pady=10)

    # Ajout d'une liste déroulante pour la destination de l'e-mail
    dest_entry = Combobox(window_send)
    
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

    def send_msg():
        # Je récupère les valeurs des différents champs
        dest_value = dest_entry.get()
        sub_value = subject_entry.get()
        text_value = body_text.get("1.0", "end")

        signal = "reception msg"
        #vpn_client.send(signal.encode())
        send_data(vpn_client,signal.encode(),key_partaged)
        #rep = vpn_client.recv(1024)
        rep = recv_message(vpn_client,key_partaged)
        
        if (rep.decode() == "ok"):
            #dest_value = encrypt(dest_value,key_partaged)
            #vpn_client.send(dest_value.encode())
            send_data(vpn_client,dest_value.encode(),key_partaged)
            #rep = vpn_client.recv(1024)
            rep = recv_message(vpn_client,key_partaged)
        
        if (rep.decode() == "ok"):
            #sub_value = encrypt(sub_value,key_partaged)
            #vpn_client.send(sub_value.encode())
            send_data(vpn_client,sub_value.encode(),key_partaged)
            #rep = vpn_client.recv(1024)
            rep = recv_message(vpn_client,key_partaged)
        
        if (rep.decode() == "ok"):
            #text_value = encrypt(text_value,key_partaged)
            #vpn_client.send(text_value.encode())
            send_data(vpn_client,text_value.encode(),key_partaged)
            #rep = vpn_client.recv(1024)
            rep = recv_message(vpn_client,key_partaged)
        
        # Je ferme la fenetre
        window_send.destroy()

    # Ajout d'un bouton pour envoyer l'e-mail
    send_button = Button(window_send, text="Envoyer", command=send_msg)
    send_button.grid(row=3, column=1, padx=10, pady=10)
    
    
def open_mail(statut,window_mail):
    
    if window_mail.winfo_exists():
        window_mail.deiconify()
    else:
        window_mail = Toplevel(fenetre)
        window_mail.geometry("600x400")
        window_mail.title("Application Email")
        window_mail.resizable(False,False)
        centrefenetre(window_mail)
    
    if statut == 0:
        
        frame = Frame(window_mail)
        frame.pack(side="left", fill="both", expand=True)

        mail_list = Listbox(frame)
        # Ajout d'une liste de mails
        mail_list.pack(fill="both", expand=True)
        
        cursor.execute("SELECT * FROM email_client ")
        rows = cursor.fetchall()
        
        # Ajout des mails dans l'interface
        for row in rows:
            print(row)
            mail_list.insert(0, row[1]+" ("+row[2]+")")


        # Ajout d'un cadre pour contenir les détails du mail sélectionné
        details_frame = Frame(window_mail)
        details_frame.pack(side="right", fill="both", expand=True)

        # Ajout d'un label pour afficher les détails du mail sélectionné
        details_label = Label(details_frame, text="Sélectionnez un mail")
        details_label.pack(fill="both", expand=True)

         # Définition d'une fonction pour afficher les détails du mail sélectionné
        def display_details(event):
            canvas.coords(notif,0,0,0,0)
            fenetre.update()
            
            index = mail_list.curselection()[0]
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

            reply_button = Button(details_frame, text="Répondre", command=send_mail)
            reply_button.grid(row=3, column=1, padx=10, pady=10)


        # Liaison de la fonction à l'événement "selection" de la liste de mails
        mail_list.bind("<<ListboxSelect>>", display_details)
        
        menu_bar = Menu(window_mail)
        window_mail.config(menu=menu_bar)    

        file_menu = Menu(menu_bar)
        menu_bar.add_command(label="Contacts", command=contacts)
        menu_bar.add_command(label="Envoyer mail", command=send_mail)
    else:
        window_mail.update()

def on_resize(event):
    width = event.width
    height = event.height
    
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
    canvas.coords(txt_pseudo,65/1200*width, 455/630*height)
    canvas.itemconfigure(txt_pseudo, font=("Robot", int(10/630*height),"bold"))
    canvas.coords(txt_ip,45/1200*width, 490/630*height)
    canvas.itemconfigure(txt_ip, font=("Robot", int(10/630*height),"bold"))
    canvas.coords(txt_connexion,110/1200*width, 525/630*height)
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
    
    # MODULE DATA
    canvas.coords(module6_1,294/1200*width, 325/630*height, 907/1200*width, 620/630*height)
    canvas.coords(module6,299/1200*width, 330/630*height, 902/1200*width, 615/630*height)
    canvas.coords(DATA_txt,1077/1200*width, 345/630*height)
    canvas.itemconfigure(DATA_txt, font=("Robot", int(10/630*height),"bold"))
    
    
    canvas.coords(bouton1_mail,995/1200*width, 380/630*height, 1035/1200*width, 425/630*height)
    canvas.coords(bouton2_mail,995/1200*width, 380/630*height, 1035/1200*width, 420/630*height)
    canvas.coords(txt_mail,1014/1200*width, 400/630*height)
    canvas.itemconfigure(txt_mail,font=("Robot", int(25/630*height)))
    canvas.coords(dessin_mail,1005/1200*width, 388/630*height, 1024/1200*width, 412/630*height)
    
    canvas.coords(notif,1016/1200*width, 385/630*height, 1026/1200*width, 395/630*height)

def update_speed(speed,x_,y_,x1_,y1_,aiguille,max):        
    width, height = get_window_size()
    angle = math.radians(speed * 270 / 100 + 155)
    x = x_+ 55 * math.cos(angle)
    y = y_ + 55 * math.sin(angle)
    x1 = x1_ + 20* math.cos(angle)
    y2 = y1_ + 20 * math.sin(angle)
    width = int(width)
    height = int(height)
    canvas.coords(aiguille, int(x1)/1200*width, int(y2)/630*height, int(x)/1200*width, int(y)/630*height)


def compteur(X,x,y,x1,y1,speed_txt,aiguille):
    current_speed = 0
    if X > 100:
        X = 100
    # Boucle pour parcourir toutes les valeurs de vitesse
    while True:
        update_speed(current_speed,x,y,x1,y1,aiguille,X)
        fenetre.update()
        canvas.itemconfigure(speed_txt, text=current_speed)
        current_speed +=1
        time.sleep(1/100)
        if current_speed == 100:
            while current_speed != X:
                current_speed -=1
                update_speed(current_speed,x,y,x1,y1,aiguille,X)
                canvas.itemconfigure(speed_txt, text=current_speed)
                time.sleep(1/100)
                fenetre.update()
            break  

###########################################################################################################################################
#-----------------------------------------------INTERACTION AVEC LE SERVEUR VIA L'INTERFACE-----------------------------------------------#
###########################################################################################################################################
def clicked (event) :
    global statut
    global jeton
    global premier_connexion
    global compt
    global console_window
    global console
    width, height = get_window_size()
    width = int(width)
    height = int(height)
    global connecte 
    global ip_address
    global key_partaged
    print (f'You clicked at {event.x} X {event.y}.')
    if 65/1200*width < event.x < 165/1200*width and 65/630*height < event.y < 165/630*height and statut == 0:
        if premier_connexion == 0:
            connecte = connexion(host,port)
            
            if connecte:
                canvas.itemconfigure(bouton_module1_3,fill="green")
                canvas.itemconfigure(dessin_ON_OFF_module1,fill="green")
                canvas.itemconfigure(txt_module1, text='Connecté')
                key_partaged = Diffie_Hullman_Key()
                print(key_partaged)
                print("je teste")
                if console_window.winfo_exists():
                    print("j'écris dans la console ")
                    console.insert("end","Les clés ont bien été échangées !\n","green")
                premier_connexion =  1
                statut = 1
        else:
            connecte = reconnection(host,port)
            if connecte:
                canvas.itemconfigure(bouton_module1_3,fill="green")
                canvas.itemconfigure(dessin_ON_OFF_module1,fill="green")
                canvas.itemconfigure(txt_module1, text='Connecté')
                key_partaged = Diffie_Hullman_Key()
                statut =1
            
    elif 65/1200*width < event.x < 165/1200*width and 65/630*height < event.y < 165/630*height and statut == 1:
        statut = 0
        canvas.itemconfigure(bouton_module1_3,fill="red")
        canvas.itemconfigure(dessin_ON_OFF_module1,fill="red")
        canvas.itemconfigure(txt_module1, text='Déconnecté')
        connecte = 0
        if console_window.winfo_exists(): 
            console.insert("end","Vous n'êtes plus connecté au serveur.\n","red")
        deconnexion()
    elif 388/1200*width < event.x< 506/1200*width and 268/630*height < event.y< 298/630*height and jeton == 0:
        jeton = 1
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
        if connecte:
            speed = speedTestDownload(vpn_client)
            console.insert("end","Débit de transmission en download: "+str(speed)+" Mbps.\n","blue")
            compteur(speed,448,168,448,168,speed_txt_down,aiguille_down)  
        else:
            messagebox.showerror("Erreur", "Vous devez être connecté au serveur pour lancer des tests.")
            console.insert("end","Vous devez être connecté au serveur pour lancer des tests.\n","red")
        jeton = 0
    elif 710/1200*width < event.x< 823/1200*width and 270/630*height < event.y< 295/630*height and jeton == 0:
        jeton = 1
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
        if connecte:
            speed = speedTestUpload(vpn_client)
            console.insert("end","Débit de transmission en upload: "+str(speed)+" Mbps.\n","blue")
            compteur(speed,768,168,768,168,speed_txt_up,aiguille_up)
        else:
            messagebox.showerror("Erreur", "Vous devez être connecté au serveur pour lancer des tests.")
            console.insert("end","Vous devez être connecté au serveur pour lancer des tests.\n","red")
        jeton = 0
    elif 1020/1200*width < event.x< 1131/1200*width and 266/630*height < event.y< 300/630*height:
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
        if connecte :
            file=send_file()
            
            ip_address = ip_window(file)
            print("ip : ",ip_address)
            #sendFile(file,ip_address)

            compt = compt + 1
            print(compt)
            if (compt > 9):
                compt = 0 
            
        else:
            messagebox.showerror("Erreur", "Vous devez être connecté au serveur pour envoyé des fichiers.")
    elif 50/1200*width < event.x< 185/1200*width and 581/630*height < event.y< 605/630*height:
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
        open_console(connecte)
    elif 995/1200*width < event.x < 1035/1200*width and 380/630*height < event.y < 420/630*height:
        canvas.coords(bouton1_mail,995/1200*width,385/630*height,1035/1200*width,425/630*height)
        canvas.coords(bouton2_mail,995/1200*width,385/630*height,1035/1200*width,425/630*height)
        canvas.coords(txt_mail,1014/1200*width,405/630*height)
        canvas.coords(dessin_mail,1005/1200*width,393/630*height,1024/1200*width,417/630*height)
        fenetre.update()
        time.sleep(1/10)
        canvas.coords(bouton1_mail,995/1200*width,385/630*height,1035/1200*width,425/630*height)
        canvas.coords(bouton2_mail,995/1200*width,380/630*height,1035/1200*width,420/630*height)
        canvas.coords(txt_mail,1014/1200*width,400/630*height)
        canvas.coords(dessin_mail,1005/1200*width,388/630*height,1024/1200*width,412/630*height)
        if connecte :
            open_mail(0,window_mail)
        else:
            messagebox.showerror("Erreur", "Vous devez être connecté au serveur pour ouvrir cette application.")     
            console.insert("end","Vous devez être connecté au serveur pour ouvrir cette application.\n","red")
    
    if connecte:    
        try:
            # vérifier l'état du socket
            error = vpn_client.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if error != 0:
                raise socket.error(error)
            
            # envoyer un paquet de données au serveur
            signal = "recv msg ok"
            #vpn_client.send(signal.encode())
            send_data(vpn_client,signal.encode(),key_partaged)
            
            #nb_msg = vpn_client.recv(1024)
            nb_msg = recv_message(vpn_client,key_partaged)
            print("il y a ",nb_msg.decode()," msg")
            nb_msg = nb_msg.decode()
            
            if (int(nb_msg) == 0):
                signal = "no"
                #vpn_client.send(signal.encode())
                send_data(vpn_client,signal.encode(),key_partaged)
            else:
                canvas.coords(notif,1016/1200*width, 385/630*height, 1026/1200*width, 395/630*height)
                canvas.itemconfigure(notif,fill="red",width=1)
                fenetre.update()
                
                signal = "yes"
                #vpn_client.send(signal.encode())
                send_data(vpn_client,signal.encode(),key_partaged)
                print("il y a des messages j'envoie signal pour les recevoirs ")
                print("J'attends le message")
                
                signal = "ok"
                for i in range(int(nb_msg)):
                    print("je suis dans le for et j'attends")
                    #source = vpn_client.recv(1024)
                    source = recv_message(vpn_client,key_partaged)
                    print("j'ai recu")
                    #source = decrypt(source.decode(),key_partaged)
                    print("Le destinataire décrypté est : ",source)
                    #vpn_client.send(signal.encode())
                    send_data(vpn_client,signal.encode(),key_partaged)
                    
                    #subject = vpn_client.recv(1024)
                    subject = recv_message(vpn_client,key_partaged)
                    #subject = decrypt(subject.decode(),key_partaged)
                    print("Le subject décrypté est : ",subject)
                    #vpn_client.send(signal.encode())
                    send_data(vpn_client,signal.encode(),key_partaged)
                    
                    #text = vpn_client.recv(1024)
                    text = recv_message(vpn_client,key_partaged)
                    #text = decrypt(text.decode(),key_partaged)
                    print("Le text décrypté est : ",text)
                    #vpn_client.send(signal.encode())
                    send_data(vpn_client,signal.encode(),key_partaged)
                    
                    cursor.execute('SELECT COUNT(*) FROM email_client')
                    resultat = cursor.fetchone()
                    
                    if (resultat[0] == 0):
                        print("y a aucun message archiver")
                        last_id = 0
                    else:
                        print("y a déjà des msg avant")
                        cursor.execute("SELECT MAX(id) FROM email_client")
                        last_id = cursor.fetchone()[0]
                        
                    # Add a new email to the email_client table
                    cursor.execute("""INSERT INTO email_client (id,source, subject, text) VALUES (?, ?, ?, ?,?)""", 
                                (last_id+1,source.decode(), subject.decode(), text.decode(),False))
                    #open_mail(1,window_mail)
                    cursor.execute('SELECT * FROM email_client')
                    rows = cursor.fetchall()

                    # Affichage des lignes
                    print('Contenu de la table "email_client":')
                    for row in rows:
                        print("\'",row,"\'")
        except socket.error as e:
            # gérer l'erreur si la connexion est interrompue
            print("La connexion a été interrompue. Erreur :", e)
    
    if connecte:
        try:
            # vérifier l'état du socket
            error = vpn_client.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if error != 0:
                print("je suis deco")
                raise socket.error(error)
            
            # envoyer un paquet de données au serveur
            signal = "recv file ok"
            
            send_data(vpn_client,signal.encode(),key_partaged)
            
            #nb_msg = vpn_client.recv(1024)
            nb_file = recv_message(vpn_client,key_partaged)
            print("il y a ",nb_file.decode()," file")
            nb_file = nb_file.decode()
            if nb_file == "0":
                signal = "no"
                send_data(vpn_client,signal.encode(),key_partaged)
            else:
                signal = "oui"
                send_data(vpn_client,signal.encode(),key_partaged)
                
                for i in range(int(nb_file)):
                    rep = ReceptionFile(key_partaged)
                
        except socket.error as e:
            # gérer l'erreur si la connexion est interrompue
            print("La connexion a été interrompue. Erreur :", e)
    
            
            




###########################################################################################################################################
#------------------------------------------------------------FONCTIONS BACKEND------------------------------------------------------------#
###########################################################################################################################################
def binary2int(binary):
    binary = int(binary)
    int_val, i, n = 0,0,0
    while(binary != 0):
        a = binary % 10
        int_val = int_val + a * pow(2,i)
        binary = binary//10
        i += 1
    return int_val

def int2binary(n):
    "Convertit un nombre en binaire"
    if n == 0: 
        return '0'
    res = ''
    while n != 0: n, res = n >> 1, repr(n & 1) + res
    return res  

from Crypto.Cipher import AES

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
    # print("taille nonce : ",len(nonce))
    # print("taille tag : ",len(tag))
    # print("taille ciphertext : ",len(ciphertext))
    # Hachage en SHA-256
    hash_object = hashlib.sha256(message)

    # Convertir le hash en hexadécimal
    hex_dig = hash_object.hexdigest()
    
    # je stocke les données à envoyer dans un objet pour facilité l'échange
    data_obj = {"nonce":nonce, "tag":tag, "msg":ciphertext,"hash":hex_dig}
    
    # Je serialize l'objet avant de l'envoyer 
    data_serialized_obj = pickle.dumps(data_obj,protocol=4)
    
    # print("nonce : ",nonce)
    # print("tag : ",tag)
    # print("ciphertext : ",ciphertext)
    # print("TAILLE : ",len(data_serialized_obj))
    
    # print("LE HASH : ",hex_dig)
    
    vpn_client.sendall(data_serialized_obj)
    
def decrypt(key, nonce, tag, ciphertext):
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    print("message recu : ",plaintext)
    return plaintext

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
    # print("LE HASH : ",hex_dig)
    if hex_dig != hash:
        print("Problème d'intégrité ! Les données ont pu être modifié au cours du transfère")
    return msg


def keyCalculated(client_private_key,server_public_key,p,g):
    return server_public_key ** client_private_key % p

def sendFileQuery():
    signal = "send file"
    vpn_client.send(signal.encode()) # Envoi du nom et de la taille du fichier
    add_data_upload(cursor,len(signal.encode()),now)
    tmp = vpn_client.recv(1024)
    add_data_download(cursor,len(tmp),now)
    recu = tmp.decode() 
    
    return recu
       
def sendFile(file,ip):  
    global console
    global console_window
    i = 1
    signal = "send file"
    send_data(vpn_client,signal.encode(),key_partaged)
    add_data_upload(cursor,len(signal.encode()),now)
    
    rep = recv_message(vpn_client,key_partaged)
    
    # Définissions de la taille du fichier
    octets = os.path.getsize(file) / 870
    print("nombre d'octets :", octets)
    
    # Envoie de l'adresse IP
    send_data(vpn_client,ip.encode(),key_partaged)
    
    # Vérifiaction des informations
    print ("\n---> Fichier à envoyer : '" + file + "' [" + str(octets) + " Ko]")
    #console.insert("end","Fichier à envoyer : " + file + " [" + str(octets) + " Ko]\n","orange")
    tmp = "NAME " + file + "OCTETS " + str(octets)
    #vpn_client.send(tmp.encode()) # Envoi du nom et de la taille du fichier
    send_data(vpn_client,tmp.encode(),key_partaged)
    add_data_upload(cursor,len(tmp.encode()),now) 
    while (vpn_client.connect):
        # print("j'attend")
        #tmp = vpn_client.recv(1024)
        tmp = recv_message(vpn_client,key_partaged)
        print(tmp)
        print("j'ai reçu")
        add_data_download(cursor,len(tmp),now)
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
                        send_data(vpn_client,donnees,key_partaged)
                        
                        print("jai encoyé un paquet")
                        #rep=vpn_client.recv(1024)
                        rep = recv_message(vpn_client,key_partaged)
                        print("JE PEUX CONTINUER")
                        add_data_upload(cursor,len(donnees),now) 
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
                            # donnees += padding
                        #vpn_client.send(donnees)
                        print("Donné à envoyé en une fois: ",donnees)   
                        send_data(vpn_client,donnees,key_partaged)
                        print("jai encoyé un paquet")
                        #rep=vpn_client.recv(1024)
                        rep = recv_message(vpn_client,key_partaged)
                        print("JE PEUX CONTINUER")
                        add_data_upload(cursor,len(donnees),now) 
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
                send_data(vpn_client,donnees,key_partaged)
                add_data_upload(cursor,len(donnees),now) 
                recv_message(vpn_client,key_partaged)

            fich.close()
            console.insert("end","Le %d/%m a %H:%M transfert termine !\n","orange")
            signal2 = "bye"
            #vpn_client.send(signal2.encode()) # Envoi comme quoi le transfert est fini
            send_data(vpn_client,signal2.encode(),key_partaged)
            add_data_upload(cursor,len(signal2.encode()),now) 
            #print("\nsignal envoyé : ",signal2)
            return True
        else:
            print (time.strftime("\n--->[%H:%M] transfert annulé."))
            console.insert("end","[%H:%M] transfert annulé.\n","orange")
            return "BYE"

def ReceptionFile(key_partaged):
    accepte = "non"
    num = 0
    pourcent = 0
    signal = "recu"
    global id_file
    
    ip = recv_message(vpn_client,key_partaged)
            
    print("je recois signal")  
    
    send_data(vpn_client,signal.encode(),key_partaged)
    
    print("j'envoie signal pour recevoir")
    while (vpn_client.connect):
        recu = ""
        #recu = client_connection.recv(1024)     
        recu = recv_message(vpn_client,key_partaged)
        print(recu)
        if not recu : return False
        
        if accepte == "non": # Condition si on a pas deja envoyer le nom et la taille du fichier
                tmp = recu.decode()
                nomFich = tmp.split("NAME ")[1]
                nomFich = nomFich.split("OCTETS ")[0]
                taille = tmp.split("OCTETS ")[1]
                print ("\n---> Fichier '" + nomFich + "' [" + taille + " Ko]")
                nom_fichier = os.path.basename(nomFich)
                
                signal = "GO"
                #client_connection.send(signal.encode())
                send_data(vpn_client,signal.encode(),key_partaged)
                #SomUpload = addDataLenght(recu,SomUpload)
                print (time.strftime("\n---> [%H:%M] réception du fichier en cours veuillez patienter..."))
                f = open(nom_fichier, "wb")
                accepte = "oui"
                taille = float(taille) * 1024 # Conversion de la taille en octets pour le %

        elif recu.decode() == "bye": # Si on a recu "BYE" le transfer est termine

            print (" -> 100%" ) 
            f.close()
            print (time.strftime("\n---> Le %d/%m a %H:%M réception du fichier termine !"))
            break
        else: # Sinon on ecrit au fur et a mesure dans le fichier
            print("j'ai recu le paquet je vais l'archiver")
            f.write(recu)
            #print(recu.decode(),type(recu.decode()))
           
            signal="ok"
            
            send_data(vpn_client,signal.encode(),key_partaged)
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
    

def speedTestUpload(vpn_client):
    answer="speedtest upload"
    send_data(vpn_client,answer.encode(),key_partaged)
    #vpn_client.send(answer.encode())
    print("\nDébut du speed test ")
    duration = 0
    taille_bits = 0
    file = open("sauvegarde.txt","rb")
    recu = recv_message(vpn_client,key_partaged)
    if recu.decode() == "GO":
        start = time.time()
        for i in range(50):
            data = file.read(870) # Lecture du fichier en 1024 octets
            taille_bits += sys.getsizeof(data) * 8    
            #vpn_client.send(data)
            send_data(vpn_client,data,key_partaged)
            add_data_upload(cursor,len(data),now)  
            recu = recv_message(vpn_client,key_partaged)
            print("\nJ'ai recu:",recu.decode())
            add_data_download(cursor,len(recu),now) 
        end = time.time()
        duration += (end - start)
        signal = "quit"
        send_data(vpn_client,signal.encode(),key_partaged)
        #vpn_client.send(signal.encode())
        download_speed = ((taille_bits / duration)*8)/1_000_000
        return int(download_speed)

    
def speedTestDownload(vpn_client):
    answer="speedtest download"
    send_data(vpn_client,answer.encode(),key_partaged)
    #vpn_client.send(answer.encode())
    add_data_upload(cursor,len(answer.encode()),now) 
    duration = 0
    taille_bits = 0
    start = time.time()
    for i in range(50):
        signal = "OK"
        data = recv_message(vpn_client,key_partaged)
        add_data_download(cursor,len(data),now)
        taille_bits += sys.getsizeof(data) * 8
        #vpn_client.send(signal.encode())
        send_data(vpn_client,signal.encode(),key_partaged)
        add_data_upload(cursor,len(signal.encode()),now) 
    end = time.time()   
    duration += (end - start)
    print("duration : ",duration)
    download_speed = ((taille_bits / duration)*8) / 1_000_000
    print(download_speed)
    return int(download_speed)


def connexion(host,port):  
    global console_window
    global console
    try:
        vpn_client.connect((host, port)) # test si le serveur existe
        if console_window.winfo_exists():
            console.insert("end","Connexion au serveur établie !\n","green")
        print("\n--------->Connexion au serveur établie!")
        return True
    except:
        print ("---------> le serveur '" + host + "' est introuvable.")
        if console_window.winfo_exists():
            console.insert("end", "Le serveur '" + host + "' est introuvable.\n","red")
        return False  

def deconnexion():
    signal = "exit"
    send_data(vpn_client,signal.encode(),key_partaged)
    add_data_upload(cursor,len(signal.encode()),now)
    #print("signal envoyé")
    vpn_client.shutdown(socket.SHUT_RDWR)
    vpn_client.close() 
    
def reconnection(host, port):
    global vpn_client
    vpn_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    vpn_client.settimeout(2)
    connexion(host, port)
    return True

def add_data_upload(cursor,size_data,date):
    
    cursor.execute("SELECT som_up FROM trafic WHERE date = ?",(date,))
    result = cursor.fetchone()
    
    # Si la somme upload vaut 0
    if result == 0:
        # On ajoute juste la taille des données
        cursor.execute("UPDATE trafic SET som_up = ? WHERE date = ?", (size_data, date))
    else:
        # Sinon, on ajoute la taille des données à la somme déjà enregistré
        som = result[0] + size_data
        cursor.execute("UPDATE trafic SET som_up = ? WHERE date = ?", (som, date))
        
def add_data_download(cursor,size_data,date):
    
    cursor.execute("SELECT som_down FROM trafic WHERE date = ?",(date,))
    result = cursor.fetchone()
    
    # Si la somme upload vaut 0
    if result == 0:
        # On ajoute juste la taille des données
        cursor.execute("UPDATE trafic SET som_down = ? WHERE date = ?", (size_data, date))
    else:
        # Sinon, on ajoute la taille des données à la somme déjà enregistré
        som = result[0] + size_data
        cursor.execute("UPDATE trafic SET som_down = ? WHERE date = ?", (som, date))

def initialise_trafic_reseau():
    global tab_trafic
    now = datetime.now()
    now = now.strftime("%d%m%Y")
    
    if len(tab_trafic) < 0:
        new_line = (date,0,0)
        # Ajout nouvelle ligne car nouvelle date
        tab_trafic.append(new_line)
        return False
        
    for ligne in tab_trafic:
        print(ligne[0],type(ligne[0]))
        if ligne[0] == now:
            print("\nJe connais cette date")
            return True
    print("\nC'est différent, je créée une nouvelle ligne")
    date = now
    new_line = (date,0,0)
    # Ajout nouvelle ligne car nouvelle date
    tab_trafic.append(new_line)
    return False
    
def Diffie_Hullman_Key():
   # Reception des paramètres de DH envoyé par le serveur
    # Réception des paramètres de Diffie-Hellman en binaire
    parameters_bytes = vpn_client.recv(1024)
    add_data_download(cursor,len(parameters_bytes),now)

    # Parsing des données
    parameters = struct.unpack('!2i',parameters_bytes)
    p = parameters[0]
    g = parameters[1]
    #print("Reception des paramètres de DF OK!")

    # Choix d'une clé privé aléatoire entre 1 et 1000
    client_private_key = random.randint(2,10)
    #print("Génération de la clé privé de DH du client OK!")

    # Calcul de la clé publique de Diffie-Hellman pour le client
    client_public_key = (g ** client_private_key) % p 
    #print("client_public_key: ",client_public_key)
    #print("\nCalcul de la clé public du client OK!")

    # Serialiation de la clé
    client_public_key_binary = str(int2binary(client_public_key)).encode()
    #print("binary client: ",client_public_key_binary)

    # Envoie de la clé publique du client au serveur
    #print("client public binary : ",client_public_key_binary)
    vpn_client.sendall(client_public_key_binary)
    add_data_upload(cursor,len(client_public_key_binary),now)
    #print("\nEnvoie de la clé sérialisée OK!\n")

    # Réception de la clé public du client
    server_public_key_byte = vpn_client.recv(1024)
    add_data_download(cursor,len(server_public_key_byte),now)
    #print("server binary: ",server_public_key_byte,type(server_public_key_byte))
    #print("\nRéception de la clé public du serveur OK!")

    # Déserialisation de la clé publique du client
    server_public_key_binary = server_public_key_byte.decode()
    server_public_key = binary2int(server_public_key_binary)
    #print("server_public_key: ",server_public_key,type(server_public_key))
    #print("\nDéserialisation de la clé public du serveur OK!")

    # Calcul de la clé paratagée
    key_partaged = keyCalculated(client_private_key,server_public_key,p,g)
    #print("\nclé partagée : ",key_partaged)
    #print("\n-----> Les clés ont bien été échangées !")
    # Génération du hachage de la clé partagée
    h = hashlib.sha256(str(key_partaged).encode())
    key_16 = h.hexdigest()[:16]

    return key_16.encode()
###########################################################################################################################################
#---------------------------------------------------------CRÉATION DE L'INTERFACE---------------------------------------------------------#
###########################################################################################################################################
# Création de la fenêtre de l'application
fenetre = Tk()
fenetre['bg'] =  '#372589'
fenetre.geometry("1200x630")
centrefenetre(fenetre)
img = Image.open("img.png")
img = img.resize((2200,1000), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)

# Création d'un canevas qui va contenir tous les éléments de dessins de l'application
canvas = Canvas(fenetre, width=2688, height=1856, background='#372589',borderwidth=0,highlightthickness=0)
image = canvas.create_image(0,0,anchor=NW,image=img)
canvas.pack(fill=BOTH, expand=YES)
width = fenetre.winfo_width()
height = fenetre.winfo_height()

# Module 1 : Bouton ON/OFF 
module1_1 = canvas.create_rectangle(0, 0, 0, 0, fill="#2d1c76", width=0)
module1= canvas.create_rectangle(0, 0, 0, 0, fill="#412589", width=1)
bouton_module1_1 = canvas.create_oval(0, 0, 0, 0, fill="#a4c2f4", width=1)
bouton_module1_2 = canvas.create_oval(0, 0, 0, 0, fill="#2d1c76", width=1)
bouton_module1_3 = canvas.create_oval(0, 0, 0, 0, fill="red", width=1)
bouton_module1_4= canvas.create_oval(0, 0, 0, 0, fill="#2d1c76", width=1)
dessin_ON_OFF_module1 = canvas.create_rectangle(0, 0, 0, 0, width=1, fill="red")
txt_module1 = canvas.create_text(0, 0, text="Déconnecté",font="Robot 13 bold" ,fill="white")


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

# Bloc DATA
DATA_txt = canvas.create_text(0,0, text="APPLICATIONS", font="Robot 13 bold", fill="white")
# Symbole flèche

user = canvas.create_polygon(0, 0, 0, 0,0, 0, 0, 0,0, 0, 0, 0,fill='#a4c2f4')
trait1 = canvas.create_line(0, 0, 0, 0,width=2)
trait2 = canvas.create_line(0, 0, 0, 0,width=2)
trait3 = canvas.create_line(0, 0, 0, 0,width=2)
trait4 = canvas.create_line(0, 0, 0, 0,width=2)
trait5 = canvas.create_line(0, 0, 0, 0,width=2)
trait6 = canvas.create_line(0, 0, 0, 0,width=2)

tete_user = canvas.create_oval(0, 0, 0, 0,fill="#a4c2f4",width=2)
txt_user = canvas.create_text(0, 0, text="USER", font="Robot 13 bold", fill="white")
txt_pseudo = canvas.create_text(0, 0, text="Pseudo :", font="Robot 10 bold", fill="white")
txt_ip = canvas.create_text(0, 0, text="IP :", font="Robot 10 bold", fill="white")
txt_connexion = canvas.create_text(0, 0, text="Dernière connexion :", font="Robot 10 bold", fill="white")

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
#linefleche1_1 = canvas.create_line(437,223,457,223,width=2)

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

txt_trafic = canvas.create_text(0, 0, text="TRAFIC USAGE", font="Robot 13 bold", fill="white")

trafic_0GB = canvas.create_text(0, 0, text="0MB", font="Robot 9 bold", fill="white")
trafic_20GB = canvas.create_text(0, 0, text="5MB", font="Robot 9 bold", fill="white")
trafic_40GB = canvas.create_text(0, 0, text="10MB", font="Robot 9 bold", fill="white")
trafic_60GB = canvas.create_text(0, 0, text="15MB", font="Robot 9 bold", fill="white")

point1 = canvas.create_oval(0, 0, 0, 0,fill="#a4c2f4")
point2 = canvas.create_oval(0, 0, 0, 0,fill="#70757d")

txt_point1 = canvas.create_text(0, 0, text="Incoming", font="Robot 9 bold", fill="white")

txt_point2 = canvas.create_text(0, 0, text="Outcoming", font="Robot 9 bold", fill="white")

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


#file_send = []
#file0 = canvas.create_rectangle(0,0,0,0,fill="#a4c2f4",state="hidden")
#nom_file0 = canvas.create_text(0,0,text="" ,font=("Arial 10 bold"),state="hidden",fill="white")
#linefleche_down1_1_1 = canvas.create_line(0, 0, 0, 0,width=2,state="hidden")
#linefleche_down1_2_2 = canvas.create_line(0, 0, 0, 0,width=2,state="hidden")
#linefleche_down1_3_3 = canvas.create_line(0, 0, 0, 0,width=2,state="hidden")
#linefleche_down1_4_4 = canvas.create_line(0, 0, 0, 0,width=2,state="hidden" )


#file_send.append((file0,nom_file0,linefleche_down1_1_1,linefleche_down1_2_2,linefleche_down1_3_3,linefleche_down1_4_4))

#file_send.append((file2,nom_file2,linefleche_down2_1_1,linefleche_down2_2_2,linefleche_down2_3_3,linefleche_down2_4_4))
#file_send.append((file3,nom_file3,linefleche_down3_1_1,linefleche_down3_2_2,linefleche_down3_3_3,linefleche_down3_4_4))
#file_send.append((file4,nom_file4,linefleche_down4_1_1,linefleche_down4_2_2,linefleche_down4_3_3,linefleche_down4_4_4))


###########################################################################################################################################
#--------------------------------------------------CRÉATION DES INTERACTIONS DE L'INTERFACE-----------------------------------------------#
###########################################################################################################################################
statut = 0
jeton = 0
connecte = False
premier_connexion = 0
compt = 0
canvas.bind('<Button>',clicked)
# Mise à jour des formes géométriques lorsque la fenêtre est agrandie
canvas.bind("<Configure>", on_resize)
fenetre.protocol("WM_DELETE_WINDOW", on_closing)
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

window_mail = Toplevel(fenetre)
window_mail.geometry("600x400")
window_mail.title("Application Email")
window_mail.resizable(False,False)
centrefenetre(window_mail)
window_mail.withdraw()


###########################################################################################################################################
#--------------------------------------------------------CRÉATION DE LA BASE DE DONNÉES---------------------------------------------------#
###########################################################################################################################################
date = 0
now = datetime.now()
now = now.strftime("%d%m%Y")
print(now)
conn = sqlite3.connect("ma_base_de_donnees.db")
cursor = conn.cursor()
# Je créée la base de donnée si elle n'existe pas 
cursor.execute("CREATE TABLE IF NOT EXISTS trafic (date INTEGER PRIMARY KEY, som_up INTEGER,som_down INTEGER)")
cursor.execute("""CREATE TABLE IF NOT EXISTS email_client (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            source TEXT NOT NULL,
                                                            subject TEXT NOT NULL,
                                                            text TEXT NOT NULL, 
                                                            open boolean)""")
cursor.execute("CREATE TABLE IF NOT EXISTS contacts (ip TEXT NOT NULL PRIMARY KEY, ad_mail TEXT NOT NULL)")
# Si elle est vide => signifie que c'est la première connexion du client
cursor.execute("SELECT COUNT(*) FROM trafic")
result = cursor.fetchone()
if result[0] == 0:
    print("La table utilisateurs est vide. C'est la première connexion de l'utilisateur")
    cursor.execute("INSERT INTO trafic (date, som_up, som_down) VALUES (?,?,?)", (now, 0, 0))
else:
    cursor.execute("SELECT COUNT(*) FROM trafic WHERE date=?",(now,))
    result = cursor.fetchone()

    # Je vérifie si le client s'est déjà connecté aujourd'hui ou pas
    if result[0] > 0:
        print("\nLe client s'est déjà connecté aujourd'hui")
    else:
        print("\nLe client s'est déjà connecté mais pas aujourd'hui")
        cursor.execute("INSERT INTO trafic (date, som_up, som_down) VALUES (?,?,?)", (now, 0, 0))

cursor.execute("SELECT * FROM trafic")
rows = cursor.fetchall()
for row in rows:
    print(row)

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


cursor.execute("SELECT * FROM trafic ORDER BY date DESC")
rows = cursor.fetchall()
nb_ligne = len(rows)
i=0
nb_date = 1

for row in rows:
    if nb_date < 7:
        space_size = (830-375) / 7 * nb_ligne + 375
        pourcentage =  (row[1]/1000000) / 15
        pourcent =  (row[2]/1000000) /15
        print(pourcent)
        bar0 = canvas.create_rectangle((space_size-7-i) ,(560-(149*pourcentage)),(space_size+7-i),560,fill="#a4c2f4")
        bar1 = canvas.create_rectangle((space_size-7-i),(560-(149*pourcentage)-(149*pourcent)),(space_size+7-i),(560-(149*pourcentage)),fill="grey")
        date0 = canvas.create_text(0,0,text=row[0],font="Robot 8 bold")
        
        i += 65
        nb_date += 1
    

bouton1_mail = canvas.create_rectangle(995,380,1035,425,fill="grey",width=1)
bouton2_mail = canvas.create_rectangle(995,380,1035,420,fill="#a4c2f4",width=1)
txt_mail = canvas.create_text(1014,400,text="M",font="Robot 25")
dessin_mail = canvas.create_rectangle(1005,388,1024,412,width=2)
notif = canvas.create_oval(1016,385,1026,395,fill=None,width=0)
###########################################################################################################################################
#----------------------------------------------------------MISE EN PLACE DU SOCKET--------------------------------------------------------#
###########################################################################################################################################
# Paramètres de connexion
host = 'localhost'
port = 24081

# host = '31.33.237.105'
# port = 16387

# Création du socket client
vpn_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

###########################################################################################################################################
#-----------------------------------------------INTERACTION AVEC LE SERVEUR VIA L'INTERFACE-----------------------------------------------#
###########################################################################################################################################

answer = input()

if answer == "exit":
    vpn_client.close()
    conn.commit()
    conn.close()

fenetre.mainloop()