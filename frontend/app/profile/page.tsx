"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CalendarCheck2, LogOut } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { supabase } from "@/lib/supabaseClient";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ProfilePage() {
  const router = useRouter();
  const [fullName, setFullName] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [signingOut, setSigningOut] = useState(false);

  useEffect(() => {
    supabase.auth.getUser().then(async ({ data }) => {
      if (!data.user) return;
      setUserId(data.user.id);
      const { data: profile } = await supabase
        .from("profiles")
        .select("full_name, role")
        .eq("id", data.user.id)
        .single();
      if (profile) {
        setFullName(profile.full_name);
        setRole(profile.role);
      }
    });
  }, []);

  async function handleSignOut() {
    setSigningOut(true);
    await supabase.auth.signOut();
    router.push("/login");
  }

  return (
    <AppShell>
      <h1 className="mb-6 font-display text-2xl font-semibold text-ink">Profil</h1>

      <div className="grid max-w-xl gap-4">
        <Card>
          <CardTitle>Informations</CardTitle>
          <dl className="mt-3 grid grid-cols-[120px_1fr] gap-y-2 text-sm">
            <dt className="text-ink/50">Nom</dt>
            <dd className="text-ink">{fullName ?? "—"}</dd>
            <dt className="text-ink/50">Rôle</dt>
            <dd className="text-ink capitalize">{role ?? "—"}</dd>
          </dl>
        </Card>

        {role === "doctor" && (
          <Card>
            <CardTitle>Agenda Google</CardTitle>
            <p className="mt-2 text-sm text-ink/60">
              Connectez votre agenda Google pour que vos rendez-vous s&apos;y synchronisent
              automatiquement (gratuit, OAuth2).
            </p>
            <Button
              variant="secondary"
              className="mt-3"
              onClick={() => {
                if (userId) window.location.href = `${API_URL}/calendar/oauth/start?doctor_id=${userId}`;
              }}
            >
              <CalendarCheck2 className="h-4 w-4" /> Connecter Google Calendar
            </Button>
          </Card>
        )}

        <Card>
          <CardTitle>Session</CardTitle>
          <p className="mt-2 text-sm text-ink/60">
            Vous êtes connecté(e). Déconnectez-vous pour fermer la session en cours.
          </p>
          <Button variant="danger" className="mt-3" disabled={signingOut} onClick={handleSignOut}>
            <LogOut className="h-4 w-4" /> {signingOut ? "Déconnexion..." : "Se déconnecter"}
          </Button>
        </Card>
      </div>
    </AppShell>
  );
}
