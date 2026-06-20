# Backend — MediFlow AI (FastAPI)

API + agents IA. Stack **100% gratuite**, aucune carte bancaire nécessaire à aucune étape.

## Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # puis remplir les valeurs (voir ci-dessous)
```

## Configuration pas à pas (tout gratuit)

### 1. Supabase (base de données + auth + stockage)
1. Créer un compte sur [supabase.com](https://supabase.com) (gratuit, aucune carte requise).
2. Créer un projet → copier `Project URL` et `service_role key` dans `.env` (Settings > API).
3. Appliquer le schéma : SQL Editor > coller le contenu de `database/schema.sql` > Run.
4. Créer deux buckets de Storage (privés) : `consultation-audio` et `patient-documents`.
5. ⚠️ Un projet inactif depuis 7 jours est mis en pause (pas supprimé) — pensez à le réactiver depuis le dashboard avant une démo après une longue pause.

### 2. Groq (LLM gratuit — RECOMMANDÉ)
1. Aller sur [console.groq.com/keys](https://console.groq.com/keys), se créer un compte (email seulement, **aucune carte bancaire**).
2. Cliquer "Create API Key", copier la clé.
3. La coller dans `.env` : `GROQ_API_KEY=gsk_...`
4. C'est tout — pas d'installation locale, pas de téléchargement de modèle.

Limites du tier gratuit (largement suffisantes pour un prototype/une démo) : ~30 requêtes/minute, ~1000/jour sur `llama-3.3-70b-versatile`. Si vous dépassez (improbable en démo), l'erreur HTTP 429 est gérée par le code : le `triage_agent` retombe automatiquement sur une priorité prudente plutôt que de planter.

### 3. faster-whisper (transcription gratuite et locale)
Rien à installer en plus de `pip install -r requirements.txt` : le modèle (`small` par défaut) se télécharge automatiquement au premier appel et est ensuite mis en cache localement.

### 4. Google Calendar (gratuit)
1. [console.cloud.google.com](https://console.cloud.google.com) → créer un projet (gratuit).
2. Activer "Google Calendar API".
3. Créer des identifiants OAuth2 (type "Application Web"), ajouter `http://localhost:8000/calendar/oauth/callback` comme URI de redirection autorisée.
4. Copier `Client ID` / `Client secret` dans `.env`.

## Lancer le serveur

```bash
uvicorn main:app --reload --port 8000
```
Documentation interactive (Swagger) : http://localhost:8000/docs

## Charger les données de démo

```bash
python scripts/seed_demo_data.py
```
Crée d'un coup les comptes de test (staff + 5 patients aux profils volontairement variés) et remplit la file d'attente pour démontrer immédiatement la logique de priorisation.

## Lancer les tests

```bash
pytest tests/ -v
```
`test_triage_agent.py` ne nécessite ni réseau ni LLM (il teste uniquement les règles déterministes) — rapide et toujours reproductible, y compris sans clé Groq configurée.

## Structure

```
backend/
├── main.py              # point d'entrée FastAPI
├── core/config.py        # toutes les variables d'environnement, centralisées
├── db/
│   ├── database.py        # client Supabase (clé service_role — jamais côté frontend)
│   └── google_oauth.py     # stockage des tokens OAuth2 Google Calendar par médecin
├── models/schemas.py      # tous les schémas Pydantic (requêtes/réponses)
├── routers/                # endpoints HTTP, un fichier par domaine métier
├── agents/                 # les 6 agents IA — voir docs/AGENTS.md
├── scripts/seed_demo_data.py
└── tests/
```

## Si vous voulez basculer vers une API payante plus tard

Changez simplement `LLM_PROVIDER=anthropic` (ou `openai`) et `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` dans `.env`, puis `pip install anthropic` (ou `openai`, décommenté dans `requirements.txt`). Aucune autre ligne de code à toucher — c'est tout l'intérêt de l'abstraction dans `agents/base_agent.py`. Mais ce n'est **pas nécessaire** pour réussir ce projet.
