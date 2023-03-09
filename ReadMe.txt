#--> Installation de Python sur Windows, Linux et Mac

Windows

    Téléchargez la dernière version de Python sur https://www.python.org/downloads/windows/
    Cliquez sur le lien de téléchargement correspondant à votre version de Windows (32-bit ou 64-bit).
    Double-cliquez sur le fichier d'installation téléchargé pour lancer l'installation.
    Suivez les instructions à l'écran pour terminer l'installation.
    Ajouter Python à votre PATH en cochant l'option "Add Python to PATH" lors de l'installation.

Linux

Python est préinstallé sur la plupart des distributions Linux. Si Python n'est pas installé, suivez les instructions ci-dessous :

    Ouvrez votre terminal.
    Tapez la commande suivante : sudo apt-get update && sudo apt-get install python3
    Appuyez sur Entrée et entrez votre mot de passe administrateur si nécessaire.
    Attendez que l'installation soit terminée.

Mac

Python est préinstallé sur Mac OS X, cependant vous pouvez télécharger la dernière version sur https://www.python.org/downloads/mac-osx/

    Téléchargez la dernière version de Python pour Mac sur https://www.python.org/downloads/mac-osx/
    Double-cliquez sur le fichier d'installation téléchargé pour lancer l'installation.
    Suivez les instructions à l'écran pour terminer l'installation.

Installation des librairies

Pour installer les librairies nécessaires, ouvrez votre terminal et tapez la commande suivante :


pip install <nom_de_la_librairies_que_vous_souhaitez_installer>

Assurez-vous d'avoir les droits administrateur sur votre système pour installer les librairies.

#--> Mise en place du réseau

Première étape : 

 * Configurer une redirection de port (TCP/IP) sur votre box Internet 
    
        -> Garder en mémoire le port que vous avez désigné comme étant le port de redirection

 * Avant de lancer le programme du client, veillez à changer les informations de connexions 

        -> Host : adresse IPv4 de votre box Internet (ligne 2338)
        -> Port : port de redirection de votre box (ligne 2339)

Deuxième étape : 

    * Avant de lancer le programme du serveur, veillez à ajouter l'adresse IP de la machine que vous voulez connecté au serveur
    dans la liste des adresses autorisées

        -> ligne 750