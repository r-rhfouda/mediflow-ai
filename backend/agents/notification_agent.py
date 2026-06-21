"""
Notification Agent — envoie le rapport de consultation validé par email au
médecin responsable et à la réception, une fois la validation effectuée
(voir routers/consultations.py).

Implémentation gratuite par défaut : SMTP via Gmail (ou tout fournisseur
SMTP gratuit équivalent). Aucun service tiers payant requis — un compte
Gmail standard suffit, avec un "mot de passe d'application" généré
gratuitement (voir backend/README.md pour la procédure).

Comme pour les autres agents, un échec d'envoi d'email NE DOIT JAMAIS
bloquer la validation de la consultation : on logue l'erreur et on
continue. Le rapport reste de toute façon consultable depuis l'historique
patient — l'email n'est qu'une notification de confort, pas la source de
vérité des données.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings
from models.schemas import ConsultationSummary


def _build_report_html(patient_name: str, doctor_name: str, summary: ConsultationSummary) -> str:
    prescriptions_html = "".join(
        f"<li>{p.medicament} — {p.dosage or '—'} — {p.duree or '—'}</li>" for p in summary.prescriptions
    ) or "<li>Aucune prescription</li>"
    symptomes_html = "".join(f"<li>{s}</li>" for s in summary.symptomes) or "<li>Non renseigné</li>"

    return f"""
    <html>
      <body style="font-family: sans-serif; color: #3B2832;">
        <h2 style="color: #D6608C;">Compte-rendu de consultation — {patient_name}</h2>
        <p><strong>Médecin :</strong> {doctor_name}</p>
        <h3>Résumé</h3>
        <p>{summary.resume}</p>
        <h3>Symptômes</h3>
        <ul>{symptomes_html}</ul>
        <h3>Diagnostic suggéré</h3>
        <p>{summary.diagnostic_suggere}</p>
        <h3>Prescriptions</h3>
        <ul>{prescriptions_html}</ul>
        <h3>Recommandation de suivi</h3>
        <p>{summary.recommandation_suivi}</p>
        <hr>
        <p style="font-size: 12px; color: #888;">
          Rapport généré automatiquement par MediFlow AI, validé par le médecin.
          Document à usage interne du cabinet — ne pas transférer sans précaution RGPD.
        </p>
      </body>
    </html>
    """


def send_consultation_report(
    patient_name: str,
    doctor_name: str,
    doctor_email: str,
    secretary_email: str,
    summary: ConsultationSummary,
) -> bool:
    """Envoie le rapport au médecin et à la réception. Retourne True si
    l'email est parti, False sinon (jamais d'exception levée vers
    l'appelant — un email perdu ne doit pas casser la validation)."""
    if not settings.smtp_user or not settings.smtp_password:
        print("[notification_agent] SMTP non configuré — envoi d'email ignoré.")
        return False

    recipients = [addr for addr in [doctor_email, secretary_email] if addr]
    if not recipients:
        print("[notification_agent] Aucun destinataire valide — envoi ignoré.")
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Compte-rendu de consultation — {patient_name}"
    message["From"] = settings.smtp_user
    message["To"] = ", ".join(recipients)
    message.attach(MIMEText(_build_report_html(patient_name, doctor_name, summary), "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_user, recipients, message.as_string())
        return True
    except Exception as exc:  # pragma: no cover — dépend d'un service externe
        print(f"[notification_agent] Échec de l'envoi d'email : {exc}")
        return False
