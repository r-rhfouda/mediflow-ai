import { redirect } from "next/navigation";

export default function RootPage() {
  // TODO (équipe) : une fois l'auth Supabase branchée, rediriger vers /queue
  // si une session existe déjà, sinon vers /login.
  redirect("/login");
}
