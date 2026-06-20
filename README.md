# MediFlow AI

**Système de gestion de cabinet médical augmenté par des agents IA** — rendez-vous, file d'attente priorisée, transcription & résumé automatique des consultations, dossier patient centralisé, et tableau de bord BI pour l'administration.

> Projet de fin d'année — BI&A · Équipe de 2 · Durée : 2 semaines

---

## 1. Pitch en 30 secondes

Un cabinet médical perd du temps et de la fiabilité quand la prise de rendez-vous, la gestion de la salle d'attente et la rédaction des comptes-rendus se font à la main. **MediFlow AI** automatise tout le parcours patient :

1. Le patient prend RDV en ligne → synchronisation automatique avec **Google Calendar**.
2. À son arrivée, il est placé dans une **file d'attente intelligente** : un agent IA évalue chaque cas (urgence déclarée, grossesse, âge, symptômes décrits en texte libre) et réordonne la file — premier arrivé n'est pas toujours premier servi.
3. Pendant la consultation, l'audio est enregistré (avec consentement) puis **transcrit et résumé automatiquement** (note structurée façon SOAP) — le médecin valide avant archivage.
4. Tout est centralisé dans un **historique patient** (médicaments prescrits, documents, suivi).
5. L'**admin** dispose d'un tableau de bord BI : temps d'attente moyen, volumétrie, diagnostics fréquents, taux de no-show.

## 2. Stack technique

| Couche | Choix | Coût | Carte bancaire requise |
|---|---|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind CSS | 0 | Non |
| Backend / Agents IA | Python + FastAPI | 0 (auto-hébergé ou local) | Non |
| Base de données & Auth | Supabase (PostgreSQL + Auth + Storage), plan Free | 0 | **Non** |
| Calendrier | Google Calendar API (OAuth2), quota gratuit | 0 | Non |
| Transcription audio | `faster-whisper` — modèle open-source exécuté **en local** | 0, pour toujours | Non (aucun compte) |
| LLM (agents) | **Groq** (Llama 3.3 70B via API cloud) | 0, sans carte bancaire | Non |
| Déploiement démo (optionnel) | Vercel Hobby (frontend) + Render Free (backend) | 0 | Non |
| BI / dashboards admin | pandas (agrégation) + Recharts (frontend) | 0 | Non |

> **Aucune brique de ce projet n'exige de paiement ni de carte bancaire.** Le pipeline IA utilise Groq (LLM, gratuit, cloud) + faster-whisper (transcription, gratuit, local) — zéro abonnement. Le code prévoit, à titre purement optionnel, des connecteurs vers des API payantes (Claude/OpenAI) que vous n'avez **pas besoin d'utiliser** : ils sont désactivés par défaut. Trois points de vigilance gratuits à connaître : Supabase met en pause un projet inactif depuis 7 jours (le réactiver suffit, gratuitement, depuis le tableau de bord), Render free met ~30-60s à se "réveiller" après inactivité, et Groq free tier est limité à ~30 requêtes/min et 1000/jour (largement suffisant pour une démo, voir `backend/README.md`) — voir aussi `docs/DEMO_SCRIPT.md`.

## 3. Documentation du projet

- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — schéma du système, flux de données, sécurité & confidentialité
- [`docs/AGENTS.md`](./docs/AGENTS.md) — les 6 agents IA : rôle, entrées/sorties, prompts, logique de priorisation
- [`docs/PROJECT_PLAN.md`](./docs/PROJECT_PLAN.md) — planning jour par jour sur 14 jours, réparti entre les 2 membres
- [`docs/DEMO_SCRIPT.md`](./docs/DEMO_SCRIPT.md) — scénario de démonstration pour la soutenance + checklist jour J
- [`database/schema.sql`](./database/schema.sql) — schéma PostgreSQL complet
- [`frontend/README.md`](./frontend/README.md) — setup Next.js
- [`backend/README.md`](./backend/README.md) — setup FastAPI + agents IA

## 4. Démarrage rapide

```bash
# 1. Cloner et créer un projet Supabase gratuit sur supabase.com
# 2. Appliquer le schéma
psql <SUPABASE_DB_URL> -f database/schema.sql
psql <SUPABASE_DB_URL> -f database/seed_data.sql   # données de démo anonymisées

# 3. Backend (terminal 1)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # à remplir
uvicorn main:app --reload --port 8000

# 4. Frontend (terminal 2)
cd frontend
npm install
cp .env.local.example .env.local   # à remplir
npm run dev   # http://localhost:3000
```

## 5. Structure du dépôt

```
mediflow-ai/
├── docs/              # Documentation projet (archi, agents, planning, démo)
├── database/          # Schéma SQL + données de démo
├── frontend/           # Next.js (UI)
├── backend/            # FastAPI (API + agents IA)
└── README.md           # Ce fichier
```

## 6. Équipe

| Membre | Rôle principal |
|---|---|
| Personne A | Frontend / UX / intégration |
| Personne B | Backend / base de données / agents IA |

## 7. Avertissement

Ce projet est un **prototype académique**. Il ne doit pas être utilisé avec de vraies données patients. Les données de démonstration (`database/seed_data.sql`) sont entièrement fictives. Un déploiement réel nécessiterait une mise en conformité réglementaire (RGPD / loi 09-08 au Maroc) et une validation médicale qui sortent du cadre de ce projet.
