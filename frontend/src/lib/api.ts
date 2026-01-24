const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type AnalysisResult = {
  email_id: string;
  priority_score: number;
  priority_level: string;
  intent: string;
  sentiment: string;
  urgency_keywords: string[];
  sender_importance: number;
  processing_time_ms: number;
  subject?: string;
  sender?: string;
  error?: string;
};

export type ResponseResult = {
  generated_response: string;
  tone: string;
};

export async function analyzeEmail(data: {
  subject: string;
  sender: string;
  recipient: string;
  body: string;
  received_at: string;
}): Promise<AnalysisResult> {
  const res = await fetch(`${API_URL}/api/v1/emails/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function generateResponse(data: {
  email_subject: string;
  email_body: string;
  tone?: string;
}): Promise<ResponseResult> {
  const res = await fetch(`${API_URL}/api/v1/responses/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tone: "professional", ...data }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function parseFetchError(text: string): string {
  try {
    const json = JSON.parse(text) as { detail?: string };
    let msg = json.detail ?? text;
    // Clean up Python bytes repr e.g. b'[AUTHENTICATIONFAILED] ...'
    msg = msg.replace(/^b['"](.+)['"]$/, "$1").trim();
    if (/AUTHENTICATIONFAILED|Invalid credentials/i.test(msg)) {
      return "Invalid credentials. For Gmail: use an App Password, not your regular password. Enable 2FA, then create one at Google Account → Security → App passwords.";
    }
    return msg;
  } catch {
    return text;
  }
}

export async function fetchAndAnalyzeEmails(data: {
  email: string;
  password: string;
  limit?: number;
}): Promise<{ results: AnalysisResult[]; total: number }> {
  const res = await fetch(`${API_URL}/api/v1/emails/fetch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: data.email,
      password: data.password,
      limit: data.limit ?? 10,
    }),
  });
  if (!res.ok) throw new Error(parseFetchError(await res.text()));
  return res.json();
}

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error("API unavailable");
  return res.json();
}
