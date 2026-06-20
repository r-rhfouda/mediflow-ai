# Script de démo & checklist jour J

## Scénario de démonstration (≈ 6-8 minutes)

1. **Login** — se connecter en tant que réceptionniste/staff.
2. **Prise de RDV** — montrer la prise d'un RDV et, en parallèle, l'événement qui apparaît dans Google Calendar (ouvrir l'onglet à l'avance).
3. **Check-in de 3-4 patients** — arriver avec des profils volontairement différents :
   - Patient "normal" arrivé en premier.
   - Patient enceinte arrivée après.
   - Patient âgé arrivé après.
   - Patient avec un motif décrit en texte libre ambigu (déclenche le fallback LLM du `triage_agent`).
   → Montrer que la file se réordonne **automatiquement** et expliquer pourquoi (priorité affichée + raison).
4. **Consultation** — ouvrir une consultation pré-enregistrée (audio de test déjà préparé, voir ci-dessous) et montrer le résumé structuré généré, **puis le modifier** pour montrer la validation humaine.
5. **Historique patient** — montrer les prescriptions et documents centralisés.
6. **Admin / BI** — terminer sur le tableau de bord : c'est le moment de mettre en avant la dimension BI&A du projet.

## Ce qu'il faut préparer avant le jour J

- [ ] Jeu de données de démo chargé (`database/seed_data.sql`) — données 100% fictives.
- [ ] **Projet Supabase réactivé** au moins 24-48h avant (un projet free se met en pause après 7 jours d'inactivité — le rouvrir suffit, gratuitement, depuis le dashboard, mais laissez du temps pour vérifier que tout répond bien).
- [ ] 1 à 2 fichiers audio de test courts (15-30s, en français, motif clair) déjà enregistrés pour ne pas dépendre d'un micro qui grésille en salle.
- [ ] Vidéo de démo complète enregistrée en backup (au cas où le wifi/serveur déployé est capricieux).
- [ ] Backend lancé **en local** (`uvicorn`) en plus de la version déployée — le local ne dépend pas du wifi de la salle ni du cold-start d'un free tier.
- [ ] Compte Google Calendar de test (pas un vrai compte personnel) déjà connecté.
- [ ] Variables d'environnement (`.env`, `.env.local`) vérifiées sur la machine de présentation.
- [ ] Notifications désactivées sur l'ordinateur utilisé pour la démo.

## Points à anticiper dans les questions du jury

- *"Et si l'IA se trompe de priorité ?"* → expliquer le principe de supervision humaine : la réceptionniste peut toujours surclasser/déclasser manuellement, le score IA est une aide à la décision, pas une décision automatique.
- *"Qu'en est-il du RGPD / de la confidentialité ?"* → renvoyer à `docs/ARCHITECTURE.md` section sécurité : RLS, consentement audio, données fictives en démo, mention explicite que la mise en conformité réelle est hors-cadre du prototype.
- *"Pourquoi pas un seul agent IA générique ?"* → 6 agents spécialisés = plus simple à tester, à déboguer et à expliquer ; chaque agent a un périmètre et une sortie clairement définis (`docs/AGENTS.md`).
- *"Combien ça coûte à faire tourner ?"* → expliquer le mode 100% gratuit (Groq pour le LLM + faster-whisper en local pour la transcription + plans gratuits Supabase/Vercel) et la bascule possible vers des API payantes en changeant une variable d'environnement.
