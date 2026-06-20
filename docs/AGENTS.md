# Agents IA — MediFlow AI

Le système s'appuie sur **6 agents** spécialisés plutôt qu'un seul agent générique : chacun a une responsabilité étroite, ce qui les rend plus fiables, plus faciles à tester et à expliquer à l'oral qu'un unique "super-agent". Ils vivent dans `backend/agents/` et partagent une interface commune (`base_agent.py`).

Principe transverse — **supervision humaine (human-in-the-loop)** : un agent IA dans un contexte médical *propose*, il ne *décide* jamais seul de façon irréversible. Chaque sortie d'agent porte un champ `needs_human_review` et/ou doit être validée explicitement dans l'UI avant d'être archivée comme définitive. C'est un argument fort à présenter au jury.

---

## 1. Triage Agent (`triage_agent.py`)

**Rôle** : décider qui passe en priorité dans la file d'attente — c'est le cœur du sujet ("premier arrivé n'est pas forcément premier servi").

**Déclencheur** : `POST /queue/checkin`

**Logique hybride** (rapide, peu coûteuse, explicable) :

| Priorité | Règle | Type |
|---|---|---|
| 1 — Urgence vitale | Case "urgence" cochée à l'accueil, ou mots-clés détectés (douleur thoracique, difficulté à respirer, saignement important...) | Règle déterministe |
| 2 — Grossesse | Champ patient `is_pregnant = true` | Règle déterministe |
| 3 — Âgé / pathologie chronique déclarée | Âge ≥ 65 ans, ou antécédent chronique signalé au dossier | Règle déterministe |
| 4 — Normal | Tous les autres cas | FIFO (premier arrivé, premier servi) |

**Cas hors norme** : si le motif décrit en texte libre par le patient ne correspond à aucune règle ci-dessus mais semble préoccupant (formulation inhabituelle, plusieurs symptômes combinés), l'agent appelle un LLM avec un prompt de classification contraint à 4 catégories + un score de confiance. Si la confiance est faible, `needs_human_review = true` et la réceptionniste tranche.

**Entrée** : `{ patient_id, motif_libre, urgence_declaree, is_pregnant, age, antecedents }`
**Sortie** : `{ priority: 1-4, reason: str, confidence: float, needs_human_review: bool }`

---

## 2. Scheduling Agent (`scheduling_agent.py`)

**Rôle** : gérer la prise de RDV, les conflits de créneaux, et la synchronisation Google Calendar.

**Déclencheur** : `POST /appointments`, `PATCH /appointments/{id}`

**Ce qu'il fait** :
- Vérifie qu'il n'y a pas de double réservation pour un médecin donné.
- Crée/met à jour/supprime l'événement correspondant dans Google Calendar (OAuth2, `google-api-python-client`).
- Stocke le rappel (J-1) — optionnel si le temps le permet (`apscheduler` ou tâche planifiée Supabase).

**Entrée** : `{ patient_id, doctor_id, datetime, motif }`
**Sortie** : `{ appointment_id, google_event_id, status }`

---

## 3. Transcription Agent (`transcription_agent.py`)

**Rôle** : transformer l'audio de la consultation en texte.

**Déclencheur** : upload du fichier audio après une consultation (`POST /consultations/{id}/audio`)

**Implémentation gratuite par défaut** : `faster-whisper` (modèle open-source, tourne en local sur CPU, aucune clé API). Bascule possible vers l'API Whisper (OpenAI) si une clé devient disponible — un seul flag dans `.env` (`TRANSCRIPTION_PROVIDER=local|openai`).

**Entrée** : fichier audio (`.wav`/`.mp3`)
**Sortie** : `{ transcript: str, language: str, duration_seconds: float }`

---

## 4. Summarization Agent (`summarization_agent.py`)

**Rôle** : transformer la transcription brute en compte-rendu structuré, façon note **SOAP** (Subjectif / Objectif / Évaluation / Plan), adaptée en français.

**Déclencheur** : une fois la transcription disponible

**Sortie attendue (JSON strict)** :
```json
{
  "resume": "string",
  "symptomes": ["string"],
  "diagnostic_suggere": "string",
  "prescriptions": [
    { "medicament": "string", "dosage": "string", "duree": "string" }
  ],
  "recommandation_suivi": "string",
  "needs_human_review": true
}
```

**Important** : ce résumé est **toujours présenté en édition** au médecin avant sauvegarde (`/consultation/[id]` propose un champ modifiable). Le diagnostic "suggéré" ne remplace jamais le jugement médical — à formuler ainsi explicitement dans l'UI ("suggestion IA — à valider").

---

## 5. Anomaly Agent (`anomaly_agent.py`)

**Rôle** : détecter les "cas hors normal" mentionnés dans le sujet — incohérences ou signaux à remonter.

**Exemples de déclenchement** :
- Une allergie mentionnée dans la transcription contredit une prescription du `summarization_agent`.
- Le motif déclaré à l'accueil ("contrôle de routine") ne correspond pas du tout au contenu réel de la consultation (signe d'un cas mal trié au départ).
- Réutilise le `triage_agent` pour re-scorer la priorité si une urgence apparaît en cours de consultation.

**Sortie** : `{ alert_type: str, severity: "low"|"medium"|"high", message: str, suggested_action: str }` → affiché à l'admin/médecin, jamais auto-appliqué.

---

## 6. Insights Agent (`insights_agent.py`) — la brique BI&A

**Rôle** : transformer les données brutes en indicateurs pour le tableau de bord admin — c'est l'agent qui valorise le plus directement vos compétences Business Intelligence & Analytics.

**Déclencheur** : `GET /admin/insights`

**Indicateurs calculés (pandas)** :
- Temps d'attente moyen, par niveau de priorité.
- Nombre de consultations / jour, / médecin.
- Diagnostics et médicaments les plus fréquents.
- Taux de no-show, taux de cas "hors norme" détectés.
- Répartition des patients par niveau de priorité (pour visualiser concrètement que la file n'est pas du FIFO pur).

**Sortie** : JSON consommé par les graphiques Recharts du frontend (`/admin`).

---

## 7. Abstraction LLM (`base_agent.py`)

Tous les agents qui ont besoin d'un LLM (triage en cas ambigu, résumé, anomalies) passent par une interface commune :

```python
class LLMProvider(Protocol):
    def complete(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str: ...
```

Trois implémentations fournies dans le code, au choix via `LLM_PROVIDER` dans `.env` : `GroqProvider` (recommandé — gratuit, sans carte bancaire, très rapide, clé en 30 secondes sur console.groq.com/keys), et `AnthropicProvider` / `OpenAIProvider` (fournies pour la flexibilité, mais **payantes** — non nécessaires pour ce projet, à laisser désactivées). Par défaut : `LLM_PROVIDER=groq`.
