# Plan de projet — 14 jours

Équipe de 2 : **Personne A** (Frontend / UX / intégration) et **Personne B** (Backend / base de données / agents IA). Travailler en parallèle sur des branches Git séparées (`feature/frontend-*`, `feature/backend-*`) et merger en fin de journée pour éviter les conflits de dernière minute.

Règle d'or : à la fin de **chaque** journée, le projet doit pouvoir se lancer (`npm run dev` + `uvicorn`) sans crasher, même si une fonctionnalité est incomplète. Ne jamais laisser le repo dans un état cassé d'un jour sur l'autre.

## Semaine 1 — Fondations (un parcours patient simple mais réel, de bout en bout)

**Jour 1 — Setup**
- Tous les deux : créer le repo GitHub, le projet Supabase (gratuit), le scaffold (déjà fait si vous utilisez la structure fournie).
- A : installer le frontend, vérifier que `npm run dev` tourne, configurer Tailwind.
- B : installer le backend, vérifier `uvicorn main:app --reload`, appliquer `database/schema.sql` sur Supabase, charger `seed_data.sql`.
- Objectif fin de journée : les deux serveurs tournent, la DB contient des données de test.

**Jour 2 — Auth & données de base**
- A : pages `/login` et layout général (sidebar/navigation) connectés à Supabase Auth.
- B : endpoints CRUD de base (`patients`, `appointments`) + RLS policies Supabase.
- Sync : tester un login réel de bout en bout.

**Jour 3 — Rendez-vous**
- A : page `/appointments` (calendrier de créneaux disponibles, formulaire de prise de RDV).
- B : `scheduling_agent` — création d'événement Google Calendar (OAuth2), endpoint `POST /appointments`.
- Objectif fin de journée : prendre un RDV depuis l'UI crée bien un événement dans un vrai Google Calendar de test.

**Jour 4 — File d'attente (cœur du sujet)**
- A : page `/queue` — le "plateau de triage" (liste ordonnée, badges de priorité colorés).
- B : `triage_agent` (règles déterministes + fallback LLM), endpoint `POST /queue/checkin` et `GET /queue`.
- Objectif fin de journée : insérer 4 patients avec des profils différents (urgence, enceinte, âgé, normal) et voir la file se réordonner correctement.

**Jour 5 — Intégration & robustesse**
- A : brancher la page `/queue` sur l'API réelle (suppression des données mockées), gestion des états de chargement/erreur.
- B : `scheduling_agent` — gestion des conflits de créneaux, rappels (si le temps le permet).
- Tous les deux : corriger les bugs d'intégration.

**Jour 6-7 — Revue de sprint 1 + tampon**
- Démo interne : un patient peut prendre RDV → arriver → être placé dans la file avec la bonne priorité.
- Documenter les décisions techniques prises (`docs/ARCHITECTURE.md` si des choix ont changé).
- Jour tampon pour rattraper le retard — il y en a toujours un peu, c'est normal.

## Semaine 2 — Agents IA avancés & finition

**Jour 8 — Consultation : audio**
- A : page `/consultation/[id]` — bouton d'enregistrement (MediaRecorder API), affichage du consentement, upload vers Supabase Storage.
- B : `transcription_agent` (`faster-whisper` en local).

**Jour 9 — Consultation : résumé IA**
- A : affichage du résumé généré, **champ éditable** pour validation médecin avant sauvegarde.
- B : `summarization_agent` (prompt structuré, sortie JSON).
- Objectif fin de journée : enregistrer un faux échange vocal → obtenir un résumé structuré affiché et modifiable.

**Jour 10 — Historique patient**
- A : page `/history/[patientId]` — consultations passées, prescriptions, documents, upload de fichiers.
- B : `anomaly_agent`, endpoints `prescriptions` et `documents`.

**Jour 11 — Admin panel & BI**
- A : page `/admin` — dashboards Recharts (temps d'attente, volumétrie, répartition des priorités).
- B : `insights_agent` (agrégations pandas), endpoint `GET /admin/insights`.

**Jour 12 — Tests de bout en bout**
- Tous les deux : parcourir TOUT le workflow plusieurs fois (login → RDV → file → consultation → résumé → historique → admin).
- Préparer un jeu de données de démo réaliste et varié (couvrant les 4 niveaux de priorité, plusieurs médecins, quelques documents).
- Corriger les bugs bloquants en priorité absolue ; les bugs cosmétiques peuvent attendre.

**Jour 13 — Polish & déploiement**
- A : cohérence visuelle (mêmes composants partout), responsive, messages d'erreur clairs.
- B : nettoyage du code, variables d'environnement documentées, tests unitaires basiques sur le `triage_agent`.
- Tous les deux : déployer (frontend → Vercel, backend → Render/Railway) ET enregistrer une **vidéo de démo en backup** au cas où le live échoue le jour J.
- Rédiger/finaliser le support de présentation (slides) en s'appuyant sur `docs/AGENTS.md` et `docs/ARCHITECTURE.md`.

**Jour 14 — Répétition**
- Répéter la soutenance au moins 2 fois en conditions réelles (chrono, ordre de passage des deux personnes).
- Vérifier la checklist de `docs/DEMO_SCRIPT.md`.
- Marge de sécurité : ne rien coder de nouveau ce jour-là, seulement stabiliser.

## Priorités si le temps manque

Si tout n'est pas terminé le jour 12, voici l'ordre de sacrifice (du moins important au plus important à garder) :
1. Rappels automatiques de RDV → coupable en premier, n'apporte rien à la démo.
2. Agrégations BI avancées de l'admin → garder 2-3 indicateurs simples plutôt que 10 complexes.
3. Détection d'anomalies → peut être présentée "en cours d'implémentation" à l'oral sans casser la démo.
4. **Ne jamais sacrifier** : la file d'attente priorisée (c'est le cœur du sujet) et le résumé IA de consultation (c'est la partie la plus impressionnante).
