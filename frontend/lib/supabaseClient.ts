import { createClient } from "@supabase/supabase-js";

// Clé "anon" — publique par design, le RLS (Row Level Security) côté
// Supabase garantit qu'un utilisateur ne voit que ce qu'il est autorisé à voir.
// Ne JAMAIS mettre ici la clé service_role (réservée au backend FastAPI).
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
