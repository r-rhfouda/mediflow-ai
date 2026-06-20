"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, Loader2 } from "lucide-react";
import { supabase } from "@/lib/supabaseClient";
import { Button } from "@/components/ui/Button";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const { error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
      setError("Email ou mot de passe incorrect.");
      setLoading(false);
      return;
    }

    // TODO (équipe) : router vers /admin si role === 'admin', /queue sinon,
    // une fois la table "profiles" lue après connexion.
    router.push("/queue");
  }

  return (
    <div className="flex min-h-screen">
      {/* Panneau de marque */}
      <div className="hidden w-1/2 flex-col justify-between bg-brand-deep p-12 text-white lg:flex">
        <div className="flex items-center gap-2">
          <Activity className="h-7 w-7" strokeWidth={2.5} />
          <span className="font-display text-xl font-semibold">MediFlow AI</span>
        </div>
        <div className="max-w-sm">
          <p className="font-display text-3xl font-semibold leading-tight">
            La file d&apos;attente la plus juste n&apos;est pas toujours la plus rapide.
          </p>
          <p className="mt-4 text-sm text-white/70">
            Rendez-vous, priorisation des patients et comptes-rendus de consultation,
            assistés par des agents IA supervisés à chaque étape par votre équipe.
          </p>
        </div>
        <p className="text-xs text-white/40 font-mono">Projet académique — données fictives</p>
      </div>

      {/* Formulaire */}
      <div className="flex w-full flex-col items-center justify-center bg-canvas px-8 lg:w-1/2">
        <div className="w-full max-w-sm">
          <h1 className="mb-1 font-display text-2xl font-semibold text-ink">Connexion</h1>
          <p className="mb-8 text-sm text-ink/60">Accédez à l&apos;espace cabinet médical.</p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-ink">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded border border-line bg-white px-3 py-2 text-sm outline-none focus:border-brand"
                placeholder="reception@mediflow.demo"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-ink">Mot de passe</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded border border-line bg-white px-3 py-2 text-sm outline-none focus:border-brand"
                placeholder="••••••••"
              />
            </div>

            {error && <p className="text-sm text-priority-urgence">{error}</p>}

            <Button type="submit" disabled={loading} className="mt-2 w-full">
              {loading && <Loader2 className="h-4 w-4 animate-spin" />}
              Se connecter
            </Button>
          </form>

          <p className="mt-6 text-xs text-ink/40">
            Après <code className="font-mono">python scripts/seed_demo_data.py</code>, utilisez par
            exemple <code className="font-mono">reception@mediflow.demo</code>.
          </p>
        </div>
      </div>
    </div>
  );
}
