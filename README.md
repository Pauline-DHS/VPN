# 💻 Conception d'un VPN d'entreprise

Bienvenue sur le README de mon projet de développement de VPN pour les PME. Ce projet a été développé dans le cadre de mon projet de fin d'étude et vise à fournir une solution de VPN sécurisée pour les petites et moyennes entreprises.

# 📝 Description du projet
Le VPN pour les PME est un projet qui vise à fournir une solution de VPN hautement sécurisée pour les entreprises de petite et moyenne taille. J'ai développé ce VPN en respectant les protocoles de sécurité en vigueur et les normes de sécurité actuelles.

# ⚙️ Installation
Le VPN pour les PME est facile à installer et peut être configuré en quelques minutes. Les instructions d'installation et de configuration sont disponibles dans la documentation, qui est disponible ci-dessus.

# Installation de Python 🐍 

Windows 🟥🟦🟩🟧

    Téléchargez la dernière version de Python sur https://www.python.org/downloads/windows/
    Cliquez sur le lien de téléchargement correspondant à votre version de Windows (32-bit ou 64-bit).
    Double-cliquez sur le fichier d'installation téléchargé pour lancer l'installation.
    Suivez les instructions à l'écran pour terminer l'installation.
    Ajouter Python à votre PATH en cochant l'option "Add Python to PATH" lors de l'installation.

Linux 🐧

Python est préinstallé sur la plupart des distributions Linux. Si Python n'est pas installé, suivez les instructions ci-dessous :

    Ouvrez votre terminal.
    Tapez la commande suivante : sudo apt-get update && sudo apt-get install python3
    Appuyez sur Entrée et entrez votre mot de passe administrateur si nécessaire.
    Attendez que l'installation soit terminée.

Mac 🍏

Python est préinstallé sur Mac OS X, cependant vous pouvez télécharger la dernière version sur https://www.python.org/downloads/mac-osx/

    Téléchargez la dernière version de Python pour Mac sur https://www.python.org/downloads/mac-osx/
    Double-cliquez sur le fichier d'installation téléchargé pour lancer l'installation.
    Suivez les instructions à l'écran pour terminer l'installation.

# Installation des librairies 📚

Pour installer les librairies nécessaires, ouvrez votre terminal et tapez la commande suivante :


pip install <nom_de_la_librairies_que_vous_souhaitez_installer>

Assurez-vous d'avoir les droits administrateur sur votre système pour installer les librairies.

# Mise en place du réseau ⚙️

Première étape : 

 * Configurer une redirection de port (TCP/IP) sur votre box Internet 
    
        -> Garder en mémoire le port que vous avez désigné comme étant le port de redirection

 * Avant de lancer le programme du client, veillez à changer les informations de connexions 

        -> Host : adresse IPv4 de votre box Internet (ligne 2338)
        -> Port : port de redirection de votre box (ligne 2339)

Deuxième étape : 

 * Avant de lancer le programme du serveur, veillez à ajouter l'adresse IP de la machine que vous voulez connecté au serveur dans la liste des adresses autorisées
    
        -> ligne 750

# ▶️ Utilisation
Une fois que le VPN est installé, les utilisateurs peuvent facilement se connecter et utiliser le VPN pour sécuriser leur connexion à Internet. J'ai également fourni des instructions détaillées sur l'utilisation du VPN pour les utilisateurs dans un diaporama disponible ici :

👉https://docs.google.com/presentation/d/1jze_ERt7KdsmgiX-hE7vqTsZg3f9KIWqNWcOXmD_76s/edit#slide=id.p.

# ❓ Contribuer
J'encourage toutes critques constructives sur ce projet pour améliorer le VPN. Vous pouvez contribuer en signalant des problèmes ou en soumettant des demandes de fonctionnalités.
