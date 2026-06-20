-- ============================================================
-- MediFlow AI — Schéma de base de données (PostgreSQL / Supabase)
-- ============================================================
-- À exécuter dans l'éditeur SQL de Supabase, ou via :
--   psql <SUPABASE_DB_URL> -f database/schema.sql
-- ============================================================

create extension if not exists "uuid-ossp";

-- ----------------------------------------------------------------
-- 1. RÔLES & UTILISATEURS
-- ----------------------------------------------------------------
-- On s'appuie sur auth.users (géré par Supabase Auth) et on stocke
-- les infos métier dans une table "profiles" liée en 1-1.

create type user_role as enum ('patient', 'doctor', 'receptionist', 'admin');

create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  role user_role not null default 'patient',
  full_name text not null,
  phone text,
  created_at timestamptz not null default now()
);

-- ----------------------------------------------------------------
-- 2. PATIENTS (infos médicales/contexte utilisées par le triage_agent)
-- ----------------------------------------------------------------
create table patients (
  id uuid primary key references profiles(id) on delete cascade,
  date_of_birth date not null,
  is_pregnant boolean not null default false,
  chronic_conditions text[],          -- ex: ['diabète', 'hypertension']
  allergies text[],
  created_at timestamptz not null default now()
);

-- ----------------------------------------------------------------
-- 3. MÉDECINS / STAFF
-- ----------------------------------------------------------------
create table doctors (
  id uuid primary key references profiles(id) on delete cascade,
  specialty text not null default 'Médecine générale'
);

-- Jetons OAuth2 Google Calendar par médecin (un médecin connecte son propre
-- agenda Google). Stockage simplifié pour un prototype académique — en
-- production, ces tokens devraient être chiffrés au repos.
create table google_credentials (
  doctor_id uuid primary key references doctors(id) on delete cascade,
  refresh_token text not null,
  access_token text,
  token_expiry timestamptz,
  updated_at timestamptz not null default now()
);

-- ----------------------------------------------------------------
-- 4. RENDEZ-VOUS
-- ----------------------------------------------------------------
create type appointment_status as enum ('scheduled', 'checked_in', 'in_consultation', 'completed', 'cancelled', 'no_show');

create table appointments (
  id uuid primary key default uuid_generate_v4(),
  patient_id uuid not null references patients(id) on delete cascade,
  doctor_id uuid not null references doctors(id) on delete cascade,
  scheduled_at timestamptz not null,
  reason text,
  status appointment_status not null default 'scheduled',
  google_event_id text,                -- lien vers l'événement Google Calendar
  created_at timestamptz not null default now()
);

create index idx_appointments_doctor_time on appointments(doctor_id, scheduled_at);
create index idx_appointments_patient on appointments(patient_id);

-- ----------------------------------------------------------------
-- 5. FILE D'ATTENTE (sortie du triage_agent)
-- ----------------------------------------------------------------
create type queue_status as enum ('waiting', 'in_consultation', 'done', 'left');

create table queue_entries (
  id uuid primary key default uuid_generate_v4(),
  appointment_id uuid references appointments(id) on delete set null,
  patient_id uuid not null references patients(id) on delete cascade,
  priority smallint not null check (priority between 1 and 4),  -- 1=urgence ... 4=normal
  priority_reason text,                 -- explication donnée par le triage_agent
  needs_human_review boolean not null default false,
  arrival_time timestamptz not null default now(),
  status queue_status not null default 'waiting',
  ticket_number serial,                 -- numéro de passage affiché à l'écran
  called_at timestamptz,                -- horodatage du passage à 'in_consultation' (sert au calcul du temps d'attente)
  created_at timestamptz not null default now()
);

-- Index clé : c'est CETTE requête qui matérialise "premier arrivé n'est pas
-- forcément premier servi" → tri par priorité d'abord, puis par heure d'arrivée.
create index idx_queue_order on queue_entries(priority asc, arrival_time asc) where status = 'waiting';

-- ----------------------------------------------------------------
-- 6. CONSULTATIONS (transcription + résumé)
-- ----------------------------------------------------------------
create table consultations (
  id uuid primary key default uuid_generate_v4(),
  appointment_id uuid not null references appointments(id) on delete cascade,
  audio_url text,                       -- chemin dans Supabase Storage
  consent_given boolean not null default false,
  transcript text,
  summary jsonb,                        -- sortie structurée du summarization_agent
  validated_by_doctor boolean not null default false,
  validated_at timestamptz,
  created_at timestamptz not null default now()
);

-- ----------------------------------------------------------------
-- 7. PRESCRIPTIONS
-- ----------------------------------------------------------------
create table prescriptions (
  id uuid primary key default uuid_generate_v4(),
  consultation_id uuid not null references consultations(id) on delete cascade,
  patient_id uuid not null references patients(id) on delete cascade,
  medication text not null,
  dosage text,
  duration text,
  created_at timestamptz not null default now()
);

create index idx_prescriptions_patient on prescriptions(patient_id);

-- ----------------------------------------------------------------
-- 8. DOCUMENTS (analyses, ordonnances scannées, etc.)
-- ----------------------------------------------------------------
create table documents (
  id uuid primary key default uuid_generate_v4(),
  patient_id uuid not null references patients(id) on delete cascade,
  consultation_id uuid references consultations(id) on delete set null,
  file_url text not null,
  document_type text,                   -- 'analyse', 'ordonnance', 'autre'
  uploaded_at timestamptz not null default now()
);

-- ----------------------------------------------------------------
-- 9. JOURNAL D'AUDIT (alertes de l'anomaly_agent, actions admin)
-- ----------------------------------------------------------------
create table audit_log (
  id uuid primary key default uuid_generate_v4(),
  related_table text,
  related_id uuid,
  event_type text not null,             -- 'anomaly_detected', 'priority_overridden', ...
  severity text,
  message text,
  created_at timestamptz not null default now()
);

-- ============================================================
-- 10. ROW LEVEL SECURITY — exemples (à compléter selon vos rôles)
-- ============================================================
alter table patients enable row level security;
alter table consultations enable row level security;
alter table documents enable row level security;

-- Un patient ne voit que ses propres données.
create policy "patients_select_own" on patients
  for select using (auth.uid() = id);

-- Le staff (médecin/réceptionniste/admin) voit tout.
create policy "staff_select_all_patients" on patients
  for select using (
    exists (select 1 from profiles p where p.id = auth.uid() and p.role in ('doctor', 'receptionist', 'admin'))
  );

-- (Répliquer le même pattern pour consultations, documents, prescriptions.)
