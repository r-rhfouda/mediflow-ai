# Guide de réalisation — pas à pas (Groq + Supabase, 100% gratuit)

Ce guide part de zéro : terminal vide → produit qui tourne. Tout le code mentionné existe déjà dans le projet fourni (`mediflow-ai.zip`) ; ce guide vous dit **où cliquer, quoi taper, quoi vérifier**, dans l'ordre. Faites-le à deux, en suivant `docs/PROJECT_PLAN.md` pour la répartition des jours.

> Convention : `$` = terminal, à taper tel quel (sans le `$`). Tout ce qui est entre `< >` est à remplacer par votre valeur.

---

## Étape 0 — Outils à installer une fois (15 min)

```bash
# Vérifier ce qui est déjà installé
node -v      # il faut Node 18+ — sinon installer depuis nodejs.org
python3 --version   # il faut Python 3.11+
git --version
```

Si Node ou Python manquent, installez-les depuis leurs sites officiels (gratuits). VSCode : [code.visualstudio.com](https://code.visualstudio.com).

Extensions VSCode utiles : **Python** (Microsoft), **ESLint**, **Tailwind CSS IntelliSense**, **Thunder Client** (pour tester l'API sans Postman).

---

## Étape 1 — Récupérer le projet (5 min)

```bash
cd ~/Desktop                      # ou où vous voulez travailler
unzip mediflow-ai.zip
cd mediflow-ai
code .                            # ouvre le dossier dans VSCode
```

Initialisez Git pour travailler à deux :

```bash
git init
git add .
git commit -m "Scaffold initial du projet"
```

Créez un dépôt vide sur GitHub (gratuit), puis :

```bash
git remote add origin https://github.com/<votre-compte>/mediflow-ai.git
git branch -M main
git push -u origin main
```

Votre coéquipier fait ensuite `git clone https://github.com/<votre-compte>/mediflow-ai.git`.

---

## Étape 2 — Créer le projet Supabase (10 min)

1. Aller sur [supabase.com](https://supabase.com) → **Start your project** → se connecter avec GitHub (gratuit, aucune carte demandée).
2. **New project** :
   - Name : `mediflow-ai`
   - Database Password : générez-en un fort, **notez-le quelque part** (vous ne le reverrez plus en clair).
   - Region : choisissez la plus proche (ex. `eu-west` si vous êtes au Maroc/Europe).
   - Plan : **Free** (déjà sélectionné par défaut).
3. Attendez ~2 minutes que le projet se provisionne.

### 2.1 Récupérer les clés API

Dans le projet Supabase → **Settings** (roue dentée) → **API**. Notez ces 3 valeurs, vous en aurez besoin partout :

| Valeur | Où l'utiliser |
|---|---|
| `Project URL` | `frontend/.env.local` (`NEXT_PUBLIC_SUPABASE_URL`) et `backend/.env` (`SUPABASE_URL`) |
| `anon public` key | `frontend/.env.local` (`NEXT_PUBLIC_SUPABASE_ANON_KEY`) |
| `service_role` key | `backend/.env` (`SUPABASE_SERVICE_ROLE_KEY`) — **jamais côté frontend, jamais sur GitHub** |

### 2.2 Appliquer le schéma de base de données

Dans Supabase → **SQL Editor** → **New query**. Ouvrez `database/schema.sql` dans VSCode, copiez tout le contenu, collez-le dans l'éditeur SQL Supabase, cliquez **Run**.

Vérifiez : **Table Editor** (menu de gauche) doit maintenant afficher `profiles`, `patients`, `doctors`, `appointments`, `queue_entries`, `consultations`, `prescriptions`, `documents`, `audit_log`, `google_credentials`.

### 2.3 Créer les buckets de stockage (audio + documents)

**Storage** (menu de gauche) → **New bucket** :
- Nom : `consultation-audio`, **Public bucket : NON** (décoché — il faut que ce soit privé).
- Nom : `patient-documents`, **Public bucket : NON**.

### 2.4 Activer l'authentification par email/mot de passe

**Authentication** → **Providers** → vérifiez que **Email** est activé (il l'est par défaut). Pour la démo, désactivez la confirmation par email pour aller plus vite : **Authentication** → **Settings** → décochez **Confirm email**.

---

## Étape 3 — Créer la clé Groq (2 min, gratuit, sans carte)

1. Aller sur [console.groq.com/keys](https://console.groq.com/keys).
2. Se connecter (email ou Google).
3. **Create API Key** → donnez-lui un nom (`mediflow-dev`) → copiez la clé (elle commence par `gsk_...`, vous ne la reverrez plus en clair).

C'est tout. Pas de carte bancaire, pas d'installation. Le modèle utilisé par le projet est `llama-3.3-70b-versatile` (gratuit, rapide, bon en français).

---

## Étape 4 — Configurer et lancer le backend (FastAPI)

### 4.1 Environnement virtuel et dépendances

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

Si `pip install` échoue sur `faster-whisper` (rare, dépend de l'OS), relancez juste cette ligne seule : `pip install faster-whisper==1.0.3`.

### 4.2 Fichier `.env`

```bash
cp .env.example .env
```

Ouvrez `backend/.env` dans VSCode et remplissez avec vos vraies valeurs :

```bash
ENV=development
FRONTEND_ORIGIN=http://localhost:3000

SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJI...   # la clé service_role, étape 2.1

GOOGLE_CLIENT_ID=                            # laissez vide pour l'instant (étape 7)
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/calendar/oauth/callback

LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx        # la clé Groq, étape 3
GROQ_MODEL=llama-3.3-70b-versatile

TRANSCRIPTION_PROVIDER=local
WHISPER_MODEL_SIZE=small
```

### 4.3 Lancer le serveur

```bash
uvicorn main:app --reload --port 8000
```

Vérifiez dans le navigateur : [http://localhost:8000/health](http://localhost:8000/health) doit répondre :
```json
{"status": "ok", "env": "development", "llm_provider": "groq"}
```

Et [http://localhost:8000/docs](http://localhost:8000/docs) ouvre la documentation interactive Swagger — gardez cet onglet ouvert, il sert à tester chaque endpoint manuellement pendant le développement, sans avoir besoin du frontend.

### 4.4 Tester que Groq répond bien

Dans un terminal séparé (gardez `uvicorn` lancé dans le premier) :

```bash
cd backend
source .venv/bin/activate
python3 -c "
from agents.base_agent import get_llm_provider
llm = get_llm_provider()
print(llm.complete('Réponds en un mot.', 'Dis bonjour.'))
"
```

Si ça affiche une réponse, Groq est bien connecté. Si erreur `GROQ_API_KEY manquant`, vérifiez votre `.env`.

### 4.5 Lancer les tests automatiques

```bash
pytest tests/ -v
```

Les 6 tests de `test_triage_agent.py` doivent passer en vert — ils ne dépendent ni de Groq ni de Supabase (uniquement les règles déterministes), donc toujours reproductibles.

---

## Étape 5 — Charger les données de démo

Gardez `uvicorn` lancé, ouvrez un nouveau terminal :

```bash
cd backend
source .venv/bin/activate
python3 scripts/seed_demo_data.py
```

Si tout va bien, vous verrez s'afficher la création de 4 comptes staff + 5 patients + une file d'attente déjà priorisée, et à la fin :
```
✅ Données de démo créées avec succès.
   Mot de passe (tous les comptes de démo) : MediFlowDemo2026!
   Connectez-vous sur le frontend avec, par exemple : reception@mediflow.demo
```

Vérifiez dans Supabase → **Table Editor** → `queue_entries` : vous devriez voir 5 lignes, avec des priorités 1 à 4 qui ne suivent pas l'ordre d'arrivée — c'est exactement le comportement attendu.

> En cas d'erreur "User already registered" si vous relancez le script deux fois : allez dans Supabase → **Authentication** → **Users**, supprimez les comptes `@mediflow.demo`, puis relancez.

---

## Étape 6 — Configurer et lancer le frontend (Next.js)

Dans un **nouveau terminal** (gardez `uvicorn` lancé dans l'autre) :

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

Remplissez `frontend/.env.local` :

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJI...   # la clé "anon public", PAS service_role
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Lancer :

```bash
npm run dev
```

Ouvrez [http://localhost:3000](http://localhost:3000) → vous devriez arriver sur `/login`.

Connectez-vous avec `reception@mediflow.demo` / `MediFlowDemo2026!` (créé par le script de seed à l'étape 5). Vous devriez atterrir sur `/queue` et voir la vraie file d'attente venant de Supabase (le badge jaune "Données de démonstration" doit avoir disparu — s'il est encore là, c'est que le backend ou les `.env` ne sont pas bien branchés, vérifiez la console du navigateur, F12).

**Vous avez maintenant un produit qui tourne de bout en bout.** Tout ce qui suit dans le planning (`docs/PROJECT_PLAN.md`) consiste à enrichir/finir chaque page.

---

## Étape 7 — Google Calendar (optionnel, à faire au Jour 3 selon le planning)

1. [console.cloud.google.com](https://console.cloud.google.com) → créer un projet (gratuit), nommez-le `mediflow-ai`.
2. Menu ☰ → **APIs & Services** → **Library** → cherchez "Google Calendar API" → **Enable**.
3. **APIs & Services** → **OAuth consent screen** :
   - User Type : **External**.
   - Renseignez juste le nom de l'app et un email de contact.
   - **Test users** : ajoutez les emails Google réels que vous utiliserez pour tester (vos comptes perso) — tant que l'app n'est pas publiée, seuls ces comptes peuvent se connecter, ce qui est parfait pour une démo.
4. **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID** :
   - Application type : **Web application**.
   - Authorized redirect URIs : `http://localhost:8000/calendar/oauth/callback`
5. Copiez `Client ID` et `Client secret` dans `backend/.env` (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`), relancez `uvicorn`.

Test : connectez-vous au frontend avec un compte `role=doctor` (ex. `dr.alaoui@mediflow.demo`), allez sur `/profile`, cliquez **Connecter Google Calendar**, validez l'écran Google. Vous êtes redirigé vers `/profile?calendar_connected=true`. Prenez ensuite un RDV pour ce médecin depuis `/appointments` → l'événement doit apparaître dans son Google Calendar réel.

---

## Étape 8 — Tester le pipeline audio (consultation)

1. Connectez-vous avec un compte `doctor`.
2. Allez sur `/consultation/<n'importe-quel-id>` (par exemple un des UUID d'`appointments` visibles dans Supabase Table Editor).
3. Cochez la case de consentement, cliquez **Démarrer l'enregistrement** (le navigateur va demander l'accès au micro — acceptez).
4. Parlez 15-20 secondes en français (ex. : *"Bonjour, le patient se plaint de maux de tête depuis trois jours, pas de fièvre, je prescris du paracétamol 500mg pendant 5 jours."*).
5. Cliquez **Arrêter**.

Le premier appel est plus lent (faster-whisper télécharge son modèle, ~250 Mo, une seule fois). Vous devriez voir apparaître un résumé structuré généré par Groq, modifiable, avec la prescription extraite. Validez.

Si erreur : ouvrez le terminal `uvicorn`, l'erreur Python exacte s'y affiche (souvent : `GROQ_API_KEY` mal copiée, ou bucket Storage mal nommé).

---

## Étape 9 — Vérifier le tableau de bord admin

Connectez-vous avec `admin@mediflow.demo`, allez sur `/admin`. Les graphiques doivent se charger depuis `GET /admin/insights` (testable aussi directement sur [http://localhost:8000/docs](http://localhost:8000/docs)).

---

## Étape 10 — Garder le projet propre pendant 2 semaines

À chaque session de travail :

```bash
git pull                 # récupérer le travail de l'autre
# ... coder ...
git add .
git commit -m "Description claire du changement"
git push
```

Ne **jamais** committer `backend/.env` ni `frontend/.env.local` (le `.gitignore` fourni les bloque déjà — vérifiez avec `git status` qu'ils n'apparaissent jamais dans la liste).

---

## Récapitulatif des 3 terminaux à garder ouverts en permanence pendant le développement

| Terminal | Commande | Rôle |
|---|---|---|
| 1 | `cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000` | API |
| 2 | `cd frontend && npm run dev` | Interface |
| 3 | libre | git, scripts ponctuels (`seed_demo_data.py`, `pytest`...) |

---

## Erreurs fréquentes et solutions rapides

| Symptôme | Cause probable | Solution |
|---|---|---|
| `/queue` affiche le badge "Données de démonstration" en continu | Backend pas lancé, ou mauvaise URL dans `.env.local` | Vérifier terminal 1, vérifier `NEXT_PUBLIC_API_URL` |
| `GROQ_API_KEY manquant` | `.env` backend mal rempli ou pas relu | Vérifier `backend/.env`, relancer `uvicorn` (Ctrl+C puis relancer) |
| `relation "queue_entries" does not exist` | Schéma SQL pas appliqué | Refaire l'étape 2.2 |
| Erreur CORS dans la console du navigateur | `FRONTEND_ORIGIN` dans `backend/.env` ne correspond pas à l'URL du frontend | Vérifier que c'est bien `http://localhost:3000` |
| `User already registered` au seed | Script lancé deux fois | Supprimer les comptes `@mediflow.demo` dans Supabase Auth, relancer |
| Upload audio échoue (403) | Bucket Storage mal nommé ou mal configuré | Vérifier les noms exacts `consultation-audio` / `patient-documents`, étape 2.3 |
| `429 Too Many Requests` sur Groq | Quota gratuit dépassé (rare en dev) | Attendre quelques minutes ; le `triage_agent` a un repli automatique en cas d'échec |
