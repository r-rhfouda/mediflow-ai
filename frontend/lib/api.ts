// Client API minimal vers le backend FastAPI.

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status} sur ${path} : ${body}`);
  }
  return res.json();
}

export const api = {
  getQueue: () => request("/queue"),
  getQueueAlerts: () => request("/queue/alerts"),
  checkIn: (payload: { appointment_id: string; patient_id: string; motif_libre: string; urgence_declaree: boolean }) =>
    request("/queue/checkin", { method: "POST", body: JSON.stringify(payload) }),
  callPatient: (entryId: string) => request(`/queue/${entryId}/call`, { method: "PATCH" }),
  finishPatient: (entryId: string) => request(`/queue/${entryId}/done`, { method: "PATCH" }),

  listAppointments: (params: { doctor_id?: string; patient_id?: string } = {}) => {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    return request(`/appointments${qs ? `?${qs}` : ""}`);
  },
  bookAppointment: (payload: { patient_id: string; doctor_id: string; scheduled_at: string; reason?: string }) =>
    request("/appointments", { method: "POST", body: JSON.stringify(payload) }),

  getPatientHistory: (patientId: string) => request(`/patients/${patientId}/history`),

  getInsights: (period: "day" | "month" | "all" = "all") => request(`/admin/insights?period=${period}`),
};
