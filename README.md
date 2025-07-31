# Finance-Tips

**Finance-Tips** est une application web, et mobile pensée pour les petites entreprises, vendeurs indépendants et particuliers.
Elle leur permet de gérer leurs reçus, créer leur propre marque, et d’accéder à des calculatrices financières conformes aux principes de la finance halal.

# Finance-Tips

**Finance-Tips** est une application web destinée aux vendeurs de petites boutiques, PME et particuliers pour :
- Éditer et personnaliser leurs reçus (logo, couleurs, texte, etc.)
- Créer leur marque ou tampon personnel
- Accéder à un espace personnel sécurisé (inscription / login)
- Utiliser des calculatrices financières **Halal** (sans intérêts usuriers)
- Consulter des conseils financiers et gérer un blog
- S’abonner à une newsletter

---

## 🎯 Objectifs

- Simplifier la gestion des reçus et documents financiers
- Fournir des outils d’estimation financière éthique (plan d’épargne, simulation de budget, durée de remboursement sans intérêt)
- Permettre la création et gestion de profils pour entreprises (Company) et individus (Entité)
- Offrir une interface personnalisée pour chaque utilisateur
- Éduquer par des conseils financiers accessibles

---

## 🧱 Architecture du projet (backend)

Finance-tips-api/
├── config/
│ ├── constant.py # Constantes globales
│ └── db.py # Connexion à la base de données
├── helpers/
│ ├── users.py # Logique métier utilisateur
│ └── tips.py # Logique de calcul / astuces financières
├── log/ # Logs de l’application
├── model/
│ └── finance_tips.py # Modèles SQLAlchemy
├── resources/
│ ├── users.py # Endpoints utilisateurs (register / login / profile)
│ └── tips.py # Endpoints des calculatrices et conseils
├── statics/ # Assets statiques (images, etc.)
├── templates/ # Templates HTML si rendu côté serveur (emails, etc.)
├── app.py # Point d’entrée Flask
├── requirements.txt # Dépendances Python
└── instructions.txt # Notes pour installation / déploiement



---

## 🔧 Fonctionnalités prévues

### Authentification & profils
- Inscription / connexion (JWT)
- Espaces personnalisés : 
  - **Company** (PME, boutique, entreprise)
  - **Entité** (individu)

### Réception & branding
- Éditeur de reçus : design, logo, champs dynamiques
- Générateur de tampon / marque (texte + logo)

### Calculatrices financières Halal
- Plan d’épargne mensuel (sans intérêt) : atteindre un objectif en épargnant régulièrement
- Durée de remboursement d’un prêt sans intérêt (entrée : montant + versement mensuel → durée)
- Simulation de budget (revenus vs dépenses → épargne potentielle)

### Contenu & acquisition
- Blog / conseils financiers
- Landing page & newsletter (inscription, envoi via Mailchimp ou équivalent)

---

## 🎨 Design & UI/UX (front-end)

- **Couleur principale** : bleu mi-clair / mi-sombre  
  - Exemple : `#2D6A9F` (titres), `#85B6D1` (fonds/boutons secondaires)
- Thème : simple, professionnel, adapté aux petites structures
- Typographie : lisible, sobre
- **Pages clés** :
  - Landing page
  - Inscription / login
  - Tableau de bord utilisateur
  - Éditeur de reçus
  - Générateur de marque
  - Accès aux calculatrices halal
  - Section conseils / blog

**Technologie frontend suggérée** : Angular (ou HTML/CSS/JS pour une version légère)

---

## ⚙️ Installation (backend)

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/ton-utilisateur/Finance-tips-api.git
   cd Finance-tips-api

2. **Créer et activer un environnement virtuel**
   ```bash
    python -m venv venv
    source venv/bin/activate      # macOS / Linux
    venv\Scripts\activate         # Windows

3. **Installer les dépendances**
   ```bash
    pip install -r requirements.txt

4. **Configurer les variables d’environnement**
Crée un fichier .env (exemple) :

FLASK_ENV=development
SECRET_KEY=ton_secret
DATABASE_URL=sqlite:///finance_tips.db
JWT_SECRET_KEY=ton_jwt_secret

5. **Configurer les variables d’environnement**

python app.py


## ⚙️ Exemple de cas d’usage

Un vendeur crée un compte “Company”, personnalise son reçu (logo + tampon), puis génère un reçu pour un cli
Un individu utilise la calculatrice halal pour planifier une épargne sans intérêt.

L’utilisateur reçoit des conseils financiers depuis le blog et s’inscrit à la newsletter

## Stack technique
- Backend : Flask, Flask-RESTful, Flask-JWT-Extended, SQLAlchemy
- Base de données : SQLite (développement) / PostgreSQL (production)
- Frontend : Angular (ou HTML/CSS/JS)
- Auth : JWT
- Email : Mailchimp ou SMTP pour newsletters ## 📦 requirements.txt (extrait recommandé)

Flask==3.0.0
Flask-RESTful==0.3.10
Flask-JWT-Extended==4.6.0
Flask-Cors==4.0.0
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.25
python-dotenv==1.0.1
passlib==1.7.4
bcrypt==4.1.2
PyJWT==2.8.0
gunicorn==21.2.0

## Notes
Les calculs financiers respectent les principes de la finance éthique / halal : pas d’intérêt usurier.
Séparer les rôles entre comptes “Company” et “Entité” permet une personnalisation fine du tableau de bord. 

## Notes
Les calculs financiers respectent les principes de la finance éthique / halal : pas d’intérêt usurier.

Séparer les rôles entre comptes “Company” et “Entité” permet une personnalisation fine du tableau de bord. 🤝 Contribution
Tu peux contribuer via des issues ou pull requests sur GitHub. Merci de forker le dépôt et de soumettre une PR avec une description claire.

## Contact
Pour questions ou support : ouvre une issue sur le dépôt GitHub.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
