# Frontend — MediFlow AI (Next.js)

Interface du système : connexion, profil, rendez-vous, file d'attente priorisée,
consultation (audio + résumé IA), historique patient, admin/BI.

## Installation

```bash
cd frontend
npm install
cp .env.local.example .env.local   # remplir avec vos clés Supabase (gratuites)
npm run dev
```
→ http://localhost:3000

## Pages

| Route | Contenu |
|---|---|
| `/login` | Connexion (Supabase Auth) |
| `/profile` | Infos utilisateur + connexion Google Calendar (médecin) |
| `/appointments` | Liste et prise de rendez-vous |
| `/queue` | **Plateau de triage** — la file d'attente priorisée (page la plus représentative du projet) |
| `/consultation/[id]` | Enregistrement audio, transcription + résumé IA éditable |
| `/history/[patientId]` | Historique patient : consultations, prescriptions, documents |
| `/admin` | Tableau de bord BI (graphiques Recharts) |

## Design

Les tokens (couleurs, typographies) sont centralisés dans `tailwind.config.ts` et `app/layout.tsx` (polices via `next/font`, gratuites et auto-hébergées par Next.js — aucun CDN externe payant). La palette de priorité (`priority.urgence` / `grossesse` / `senior` / `normal`) s'inspire des codes couleur réels utilisés en triage d'urgence (échelle ESI), pour rester cohérente avec ce que les professionnels de santé connaissent déjà.

## Données de démonstration

Plusieurs pages (`/queue`, `/admin`) affichent des **données mockées** tant que le backend FastAPI n'est pas lancé ou pas encore branché — un badge "Données de démonstration" l'indique clairement à l'écran. Une fois `uvicorn` lancé et `python scripts/seed_demo_data.py` exécuté côté backend, ces pages basculent automatiquement sur les vraies données.

## À compléter par l'équipe (voir `docs/PROJECT_PLAN.md`)

- Authentification : redirection selon le rôle (`patient`/`doctor`/`receptionist`/`admin`) après connexion.
- Sélecteurs patient/médecin réels dans le formulaire de prise de RDV (actuellement des champs UUID bruts, à remplacer par une recherche).
- Gestion d'erreurs/notifications centralisée (toasts).
- Responsive complet (le desktop est prioritaire pour la démo, mais un cabinet utilise aussi des tablettes à l'accueil).
