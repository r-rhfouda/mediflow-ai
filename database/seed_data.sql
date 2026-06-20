-- ============================================================
-- MediFlow AI — Données de démonstration (100% fictives)
-- ============================================================
-- MÉTHODE RECOMMANDÉE : utilisez plutôt backend/scripts/seed_demo_data.py
-- qui crée les comptes Supabase Auth ET insère toutes les données ci-dessous
-- automatiquement, avec les vrais UUID générés — aucune manipulation manuelle.
--
-- Ce fichier .sql est conservé comme référence lisible de ce que contient
-- le jeu de données, et comme méthode alternative "manuelle" si vous préférez :
--   1. Créez les comptes de test via Supabase Dashboard > Authentication > Add user
--   2. Remplacez les UUID ci-dessous par les UUID réels générés par Supabase Auth.
-- ============================================================

-- ---------------- STAFF ----------------
insert into profiles (id, role, full_name, phone) values
  ('00000000-0000-0000-0000-000000000001', 'admin',        'Sara Admin',          '0600000001'),
  ('00000000-0000-0000-0000-000000000002', 'receptionist', 'Nadia Réception',     '0600000002'),
  ('00000000-0000-0000-0000-000000000003', 'doctor',       'Dr. Yassine Alaoui',  '0600000003'),
  ('00000000-0000-0000-0000-000000000004', 'doctor',       'Dr. Imane Benali',    '0600000004');

insert into doctors (id, specialty) values
  ('00000000-0000-0000-0000-000000000003', 'Médecine générale'),
  ('00000000-0000-0000-0000-000000000004', 'Gynécologie');

-- ---------------- PATIENTS (profils volontairement variés pour démontrer le triage) ----------------
insert into profiles (id, role, full_name, phone) values
  ('00000000-0000-0000-0000-000000000101', 'patient', 'Karim Idrissi',   '0611111101'),  -- normal
  ('00000000-0000-0000-0000-000000000102', 'patient', 'Salma Tazi',      '0611111102'),  -- enceinte
  ('00000000-0000-0000-0000-000000000103', 'patient', 'Mohamed Senhaji', '0611111103'),  -- âgé
  ('00000000-0000-0000-0000-000000000104', 'patient', 'Laila Cherkaoui', '0611111104'),  -- urgence déclarée
  ('00000000-0000-0000-0000-000000000105', 'patient', 'Youssef Amrani',  '0611111105');  -- cas ambigu (texte libre)

insert into patients (id, date_of_birth, is_pregnant, chronic_conditions, allergies) values
  ('00000000-0000-0000-0000-000000000101', '1990-04-12', false, '{}',               '{}'),
  ('00000000-0000-0000-0000-000000000102', '1996-09-03', true,  '{}',               '{}'),
  ('00000000-0000-0000-0000-000000000103', '1952-01-20', false, '{"diabète"}',      '{"pénicilline"}'),
  ('00000000-0000-0000-0000-000000000104', '1988-07-15', false, '{}',               '{}'),
  ('00000000-0000-0000-0000-000000000105', '1979-11-30', false, '{"hypertension"}', '{}');

-- ---------------- RENDEZ-VOUS (aujourd'hui) ----------------
insert into appointments (id, patient_id, doctor_id, scheduled_at, reason, status) values
  ('00000000-0000-0000-0000-000000000201', '00000000-0000-0000-0000-000000000101', '00000000-0000-0000-0000-000000000003', now() - interval '1 hour', 'Contrôle de routine', 'checked_in'),
  ('00000000-0000-0000-0000-000000000202', '00000000-0000-0000-0000-000000000102', '00000000-0000-0000-0000-000000000004', now() - interval '50 minutes', 'Suivi de grossesse', 'checked_in'),
  ('00000000-0000-0000-0000-000000000203', '00000000-0000-0000-0000-000000000103', '00000000-0000-0000-0000-000000000003', now() - interval '40 minutes', 'Suivi diabète', 'checked_in'),
  ('00000000-0000-0000-0000-000000000204', '00000000-0000-0000-0000-000000000104', '00000000-0000-0000-0000-000000000003', now() - interval '10 minutes', 'Douleur thoracique', 'checked_in'),
  ('00000000-0000-0000-0000-000000000205', '00000000-0000-0000-0000-000000000105', '00000000-0000-0000-0000-000000000003', now() - interval '5 minutes', 'Fatigue inhabituelle depuis 3 jours, vertiges', 'checked_in');

-- ---------------- FILE D'ATTENTE ----------------
-- Notez que Karim (normal) est arrivé en PREMIER (il y a 1h) mais se retrouve
-- DERNIER dans la file car les autres ont une priorité plus haute : c'est
-- exactement le comportement que le triage_agent doit produire.
insert into queue_entries (appointment_id, patient_id, priority, priority_reason, needs_human_review, arrival_time, status) values
  ('00000000-0000-0000-0000-000000000204', '00000000-0000-0000-0000-000000000104', 1, 'Urgence déclarée : douleur thoracique',              false, now() - interval '10 minutes', 'waiting'),
  ('00000000-0000-0000-0000-000000000202', '00000000-0000-0000-0000-000000000102', 2, 'Patiente enceinte',                                   false, now() - interval '50 minutes', 'waiting'),
  ('00000000-0000-0000-0000-000000000203', '00000000-0000-0000-0000-000000000103', 3, 'Patient âgé (74 ans) avec pathologie chronique',      false, now() - interval '40 minutes', 'waiting'),
  ('00000000-0000-0000-0000-000000000205', '00000000-0000-0000-0000-000000000105', 2, 'Symptômes combinés jugés préoccupants par l''agent IA (confiance modérée)', true, now() - interval '5 minutes', 'waiting'),
  ('00000000-0000-0000-0000-000000000201', '00000000-0000-0000-0000-000000000101', 4, 'Aucun facteur de priorité détecté',                   false, now() - interval '1 hour', 'waiting');

-- ---------------- UNE CONSULTATION TERMINÉE (exemple pour l'historique) ----------------
insert into consultations (id, appointment_id, audio_url, consent_given, transcript, summary, validated_by_doctor, validated_at) values
(
  '00000000-0000-0000-0000-000000000301',
  '00000000-0000-0000-0000-000000000203',
  null,
  true,
  'Le patient rapporte une glycémie instable depuis deux semaines, fatigue le matin, pas de douleur particulière. Poursuite du traitement habituel, dose ajustée.',
  '{
    "resume": "Suivi de diabète de type 2, glycémie instable depuis 2 semaines, fatigue matinale rapportée.",
    "symptomes": ["fatigue matinale", "glycémie instable"],
    "diagnostic_suggere": "Déséquilibre glycémique à surveiller",
    "prescriptions": [{"medicament": "Metformine", "dosage": "850mg", "duree": "30 jours"}],
    "recommandation_suivi": "Contrôle glycémique dans 2 semaines",
    "needs_human_review": false
  }'::jsonb,
  true,
  now() - interval '30 minutes'
);

insert into prescriptions (consultation_id, patient_id, medication, dosage, duration) values
  ('00000000-0000-0000-0000-000000000301', '00000000-0000-0000-0000-000000000103', 'Metformine', '850mg', '30 jours');

-- ---------------- UNE ALERTE D'EXEMPLE (anomaly_agent) ----------------
insert into audit_log (related_table, related_id, event_type, severity, message) values
  ('consultations', '00000000-0000-0000-0000-000000000301', 'info', 'low', 'Consultation validée par le médecin sans anomalie détectée.');
