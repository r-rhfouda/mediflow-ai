# Architecture — MediFlow AI

## 1. Vue d'ensemble

MediFlow AI est composé de trois couches qui communiquent par API REST :

```
┌─────────────────────────┐
│   FRONTEND (Next.js)     │  UI : login, profil, RDV, file d'attente,
│   React + TypeScript     │  consultation, historique, admin
└────────────┬─────────────┘
             │ REST / fetch
             ▼
┌─────────────────────────┐        ┌──────────────────────────┐
│  BACKEND (FastAPI)        │ ────▶ │  Supabase                │
│  - Routers métier         │        │  - PostgreSQL (données)  │
│  - 6 Agents IA             │ ◀────│  - Auth (login/rôles)     │
└────────────┬─────────────┘        │  - Storage (audio, docs) │
             │                       └──────────────────────────┘
             ▼
┌─────────────────────────┐
│  Services externes        │
│  - Google Calendar API     │
│  - LLM (Claude/OpenAI/      │
│    Groq, gratuit)        │
│  - faster-whisper (local)  │
└─────────────────────────┘
```

Le frontend ne parle **jamais directement** aux LLM ou à Google Calendar : tout passe par le backend FastAPI, qui centralise la logique métier, la sécurité des clés API, et l'orchestration des agents.

## 2. Pourquoi cette répartition Next.js / FastAPI

- **Next.js** peut interroger Supabase directement pour les opérations CRUD simples (lecture du profil, liste des RDV) via `@supabase/supabase-js` — ça évite de réécrire un CRUD basique côté Python.
- **FastAPI** héberge tout ce qui est "intelligent" ou sensible : agents IA, appels Google Calendar, transcription audio, agrégations BI. C'est le seul endroit où vivent les clés API (LLM, Google).
- Cette séparation correspond exactement aux compétences de l'équipe : Personne A (frontend) n'a pas besoin de toucher à Python, Personne B (IA/data) n'a pas besoin de toucher à React.

## 3. Flux de données — scénario principal

1. **Prise de RDV** : le patient choisit un créneau dans `/appointments` → le frontend appelle `POST /appointments` (FastAPI) → le backend crée la ligne en base **et** crée l'événement Google Calendar via le `scheduling_agent` → l'`event_id` Google est stocké pour resynchronisation.
2. **Arrivée au cabinet (check-in)** : la réceptionniste (ou le patient via une borne) déclenche `POST /queue/checkin` avec les infos de contexte (motif déclaré, grossesse, urgence signalée, âge calculé) → le `triage_agent` calcule un score de priorité → le patient est inséré dans la file PostgreSQL `queue_entries`, triée par `(priority, arrival_time)`.
3. **Consultation** : le médecin ouvre `/consultation/[id]`, démarre l'enregistrement (consentement affiché à l'écran) → l'audio est uploadé sur Supabase Storage → le `transcription_agent` transcrit → le `summarization_agent` génère une note structurée (motif, symptômes, diagnostic suggéré, prescriptions, suivi) → **le médecin valide ou corrige avant sauvegarde définitive** (principe de supervision humaine, voir `AGENTS.md`).
4. **Anomalies** : à tout moment, l'`anomaly_agent` peut être déclenché (ex. allergie mentionnée dans la transcription qui contredit une prescription) et remonter une alerte à l'admin / au médecin.
5. **Historique** : `/history/[patientId]` agrège consultations, prescriptions et documents pour un patient donné.
6. **Admin** : `/admin` appelle `GET /admin/insights`, qui exécute l'`insights_agent` (agrégations pandas) pour produire les indicateurs BI.

## 4. Modèle de données (résumé)

Voir le détail complet dans [`database/schema.sql`](../database/schema.sql). Entités principales :

`users` → `patients` / `staff` (médecin, réceptionniste, admin) · `appointments` · `queue_entries` · `consultations` · `prescriptions` · `documents` · `audit_log`.

## 5. Sécurité & confidentialité (important pour la soutenance)

Ce sont des **données de santé** : même en contexte académique, le projet doit le démontrer.

- **Row-Level Security (RLS)** activée sur Supabase : un patient ne peut lire que ses propres lignes (`patients`, `consultations`, `documents`), les rôles `staff`/`admin` ont des policies plus larges.
- **Consentement explicite** avant tout enregistrement audio (case à cocher visible, horodatée en base).
- **Aucune donnée réelle** : seules des données fictives (`seed_data.sql`) doivent être utilisées en démo.
- **Supervision humaine obligatoire** : aucune sortie d'agent IA (résumé, priorité, diagnostic suggéré) n'est enregistrée comme définitive sans validation par un humain (médecin/admin). C'est un point fort à mettre en avant à l'oral : l'IA assiste, elle ne décide pas seule.
- En conditions réelles, une mise en conformité RGPD / loi 09-08 (Maroc) et une certification médicale seraient nécessaires — à mentionner comme limite du prototype, pas à implémenter.

## 6. Tout est gratuit — détails pratiques

Aucune dépendance du projet ne nécessite une carte bancaire ou un paiement, à aucun moment :

- **Supabase, Vercel, Render** → plans gratuits, vérifiés sans carte bancaire requise. Seul point d'attention : un projet Supabase **inactif depuis 7 jours est mis en pause** automatiquement (pas supprimé) — pensez à le rouvrir 24-48h avant la soutenance pour avoir le temps de vérifier que tout fonctionne. Un service Render gratuit "s'endort" après 15 min d'inactivité et prend 30-60s à redémarrer à la première requête : pour la démo live, privilégier un lancement local (`uvicorn`) en backup, voir `docs/DEMO_SCRIPT.md`.
- **Transcription** → `faster-whisper` tourne en local sur CPU (modèle `small` ou `base`, suffisant pour une démo en français), sans aucun compte ni clé.
- **LLM** → `agents/base_agent.py` (backend) utilise **Groq** par défaut : une API cloud gratuite et sans carte bancaire (modèle `llama-3.3-70b-versatile`), avec une inférence très rapide grâce à leur matériel dédié (LPU). Une connexion internet est nécessaire (c'est un appel API, pas un modèle local), mais aucune installation ni téléchargement de modèle. Les classes `AnthropicProvider`/`OpenAIProvider` existent dans le code pour la flexibilité future, mais sont payantes et **ne sont pas nécessaires** pour réussir ce projet — ne les activez pas sauf si vous le souhaitez explicitement plus tard.

## 7. Déploiement (optionnel, pour la soutenance)

- Frontend → Vercel (plan Hobby, gratuit, sans carte bancaire, déploiement automatique depuis GitHub).
- Backend → Render (plan Free, gratuit, sans carte bancaire). ⚠️ Éviter Railway : son plan gratuit nécessite désormais une carte bancaire.
- Dans tous les cas, garder un lancement **local** (`uvicorn` + `npm run dev`) comme plan B pour la démo en direct — voir `docs/DEMO_SCRIPT.md`.
