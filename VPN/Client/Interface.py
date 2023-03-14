# coding: utf-8

import math
import time
from tkinter import *
from tkinter import messagebox 
from PIL import Image,ImageTk
from tkinter import filedialog

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

def open_file():
    filepath = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if filepath:
        # code pour ouvrir le fichier sélectionné
        with open(filepath, "r") as file:
            print(file.read())

def open_console():
    console_window = Toplevel(fenetre)
    console_window.title("Nouvelle fenêtre")
    console_window.geometry("600x300")
    centrefenetre(console_window)
    console_window.resizable(False,False)
    console_window.attributes("-topmost", True)
    console = Text(console_window)
    console.tag_config("red", foreground="red")
    console.tag_config("white", foreground="white")
    console.config(bg="black")
    console.pack()
    console.insert(INSERT, "Bienvenue dans la console\n","white")

def add_console(console,chaine,color):
    console.insert("end", chaine,"red")

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
    canvas.coords(line_6,449/1200*width, 410/630*height, 449/1200*width, 560/630*height)
    canvas.coords(line_7,525/1200*width, 410/630*height, 525/1200*width, 560/630*height)
    canvas.coords(line_8,601/1200*width, 410/630*height, 601/1200*width, 560/630*height)
    canvas.coords(line_9,677/1200*width, 410/630*height, 677/1200*width, 560/630*height)
    canvas.coords(line_10,753/1200*width, 410/630*height, 753/1200*width, 560/630*height)
    canvas.coords(line_11,829/1200*width, 410/630*height, 829/1200*width, 560/630*height)
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
    


fenetre = Tk()
fenetre['bg'] =  '#372589'
fenetre.geometry("1200x630")

centrefenetre(fenetre)
img = Image.open("img.png")
img = img.resize((2200,1000), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)

# canvas
canvas = Canvas(fenetre, width=2688, height=1856, background='#372589',borderwidth=0,highlightthickness=0)
image = canvas.create_image(0,0,anchor=NW,image=img)
canvas.pack(fill=BOTH, expand=YES)
width = fenetre.winfo_width()
height = fenetre.winfo_height()

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
DATA_txt = canvas.create_text(0,0, text="DATA", font="Robot 13 bold", fill="white")
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
down_250 = canvas.create_text(0, 0, text="250", font=("Arial bold", 12),fill="white")
down_500 = canvas.create_text(0, 0, text="500", font=("Arial bold", 12),fill="white")
down_750 = canvas.create_text(0, 0, text="750", font=("Arial bold", 12),fill="white")
down_1000 = canvas.create_text(0, 0, text="1000", font=("Arial bold", 12),fill="white")


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
up_250 = canvas.create_text(0, 0, text="250", font=("Arial bold", 12),fill="white")
up_500 = canvas.create_text(0, 0, text="500", font=("Arial bold", 12),fill="white")
up_750 = canvas.create_text(0, 0, text="750", font=("Arial bold", 12),fill="white")
up_1000 = canvas.create_text(0, 0, text="1000", font=("Arial bold", 12),fill="white")

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

txt_trafic = canvas.create_text(0, 0, text="TRAFIC USAGE", font="Robot 13 bold", fill="white")

trafic_0GB = canvas.create_text(0, 0, text="0GB", font="Robot 9 bold", fill="white")
trafic_20GB = canvas.create_text(0, 0, text="20GB", font="Robot 9 bold", fill="white")
trafic_40GB = canvas.create_text(0, 0, text="40GB", font="Robot 9 bold", fill="white")
trafic_60GB = canvas.create_text(0, 0, text="60GB", font="Robot 9 bold", fill="white")

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

def update_speed(event,speed,x_,y_,x1_,y1_,aiguille):
    width, height = get_window_size()
    angle = math.radians(speed * 270 / 1000 + 155)
    x = x_+ 55 * math.cos(angle)
    y = y_ + 55 * math.sin(angle)
    x1 = x1_ + 20* math.cos(angle)
    y2 = y1_ + 20 * math.sin(angle)
    width = int(width)
    height = int(height)
    canvas.coords(aiguille, int(x1)/1200*width, int(y2)/630*height, int(x)/1200*width, int(y)/630*height)


def compteur(event,X,x,y,x1,y1,speed_txt,aiguille):
    current_speed = 0
    # Boucle pour parcourir toutes les valeurs de vitesse
    while True:
        update_speed(event,current_speed,x,y,x1,y1,aiguille)
        fenetre.update()
        canvas.itemconfigure(speed_txt, text=current_speed)
        current_speed +=1
        if current_speed == 1000:
            while current_speed != X:
                current_speed -=1
                update_speed(event,current_speed,x,y,x1,y1,aiguille)
                canvas.itemconfigure(speed_txt, text=current_speed)
                fenetre.update()
            break  

def clicked (event) :
    global statut
    global jeton
    width, height = get_window_size()
    width = int(width)
    height = int(height)
    print (f'You clicked at {event.x} X {event.y}.')
    if 65/1200*width < event.x < 165/1200*width and 65/630*height < event.y < 165/630*height and statut == 0:
        canvas.itemconfigure(bouton_module1_3,fill="green")
        canvas.itemconfigure(dessin_ON_OFF_module1,fill="green")
        canvas.itemconfigure(txt_module1, text='Connecté')
        statut = 1
        print(statut)
    elif 65/1200*width < event.x < 165/1200*width and 65/630*height < event.y < 165/630*height and statut == 1:
        statut = 0
        print(statut)
        canvas.itemconfigure(bouton_module1_3,fill="red")
        canvas.itemconfigure(dessin_ON_OFF_module1,fill="red")
        canvas.itemconfigure(txt_module1, text='Déconnecté')
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
        compteur(event,760,448,168,448,168,speed_txt_down,aiguille_down)
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
        compteur(event,550,768,168,768,168,speed_txt_up,aiguille_up)
        time__ = 486
        time__ = str(time__)
        chaine = "Débit upload : "+time__
        add_console(console,chaine,"red")
          
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
        open_file()
    elif 50/1200*width < event.x< 185/1200*width and 581/630*height < event.y< 605/630*height:
        canvas.coords(bouton_console_rond_,50/1200*width, 581/630*height, 75/1200*width, 605/630*height)
        canvas.coords(bouton_console_rond2_,160/1200*width, 581/630*height, 185/1200*width, 605/630*height)
        canvas.coords(bouton_console,61/1200*width, 582/630*height, 175/1200*width, 605/630*height)
        canvas.coords(txt_console,119/1200*width, 593/630*height)
        canvas.coords(trait_10,61/1200*width, 581/630*height, 175/1200*width, 581/630*height)
        canvas.coords(trait_11,61/1200*width, 605/630*height, 175/1200*width, 605/630*height)
        fenetre.update()
        time.sleep(1/10)
        console_window.deiconify()
        canvas.coords(bouton_console_rond_,50/1200*width, 576/630*height, 75/1200*width, 600/630*height)
        canvas.coords(bouton_console_rond2_,160/1200*width, 576/630*height, 185/1200*width, 600/630*height)
        canvas.coords(bouton_console,61/1200*width, 577/630*height, 175/1200*width, 600/630*height)
        canvas.coords(txt_console,119/1200*width, 588/630*height)
        canvas.coords(trait_10,61/1200*width, 576/630*height, 175/1200*width, 576/630*height)
        canvas.coords(trait_11,61/1200*width, 600/630*height, 175/1200*width, 600/630*height)
        fenetre.update()


statut = 0
jeton = 0
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
console.config(bg="black")
console.pack()
console_window.withdraw()
console.insert(INSERT, "Bienvenue dans la console\n","white")
fenetre.mainloop()