"use client";

import { useState } from "react";
import {
  analyzeEmail,
  fetchAndAnalyzeEmails,
  type AnalysisResult,
} from "@/lib/api";

const PRIORITY_COLORS: Record<string, string> = {
  urgent: "bg-red-500/20 text-red-600 border-red-500/40",
  high: "bg-amber-500/20 text-amber-600 border-amber-500/40",
  normal: "bg-sky-500/20 text-sky-600 border-sky-500/40",
  low: "bg-slate-500/20 text-slate-600 border-slate-500/40",
  spam: "bg-zinc-500/20 text-zinc-600 border-zinc-500/40",
};

function AnalysisCard({
  a,
  subject,
  sender,
}: {
  a: AnalysisResult;
  subject?: string;
  sender?: string;
}) {
  const style = PRIORITY_COLORS[a.priority_level] || PRIORITY_COLORS.normal;
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-2">
      {(subject != null || sender != null) && (
        <div className="space-y-0.5">
          {subject != null && (
            <p className="font-medium text-white truncate">{subject}</p>
          )}
          {sender != null && (
            <p className="text-sm text-white/50 truncate">{sender}</p>
          )}
        </div>
      )}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <span
          className={`inline-flex items-center px-2.5 py-1 rounded-full text-sm font-medium border ${style}`}
        >
          {a.priority_level}
        </span>
        <span className="text-sm text-white/60">
          Score: {a.priority_score.toFixed(1)}/100 · {a.processing_time_ms.toFixed(0)}ms
        </span>
      </div>
      <div className="flex flex-wrap gap-2 text-xs">
        <span className="text-white/50">Intent: {a.intent}</span>
        <span className="text-white/50">Sentiment: {a.sentiment}</span>
        {a.urgency_keywords?.length ? (
          <span className="text-white/50">
            Keywords: {a.urgency_keywords.join(", ")}
          </span>
        ) : null}
      </div>
    </div>
  );
}

export default function Home() {
  const [tab, setTab] = useState<"analyze" | "inbox">("analyze");

  // Analyze
  const [subject, setSubject] = useState("");
  const [sender, setSender] = useState("");
  const [body, setBody] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [analyzeLoading, setAnalyzeLoading] = useState(false);
  const [analyzeError, setAnalyzeError] = useState("");

  // Inbox
  const [imapEmail, setImapEmail] = useState("");
  const [imapPassword, setImapPassword] = useState("");
  const [inboxResults, setInboxResults] = useState<AnalysisResult[]>([]);
  const [inboxLoading, setInboxLoading] = useState(false);
  const [inboxError, setInboxError] = useState("");

  const handleAnalyze = async () => {
    setAnalyzeError("");
    setAnalysis(null);
    setAnalyzeLoading(true);
    try {
      const res = await analyzeEmail({
        subject: subject || "(No subject)",
        sender: sender || "unknown@example.com",
        recipient: "you@company.com",
        body: body || "(No body)",
        received_at: new Date().toISOString(),
      });
      setAnalysis(res);
    } catch (e) {
      setAnalyzeError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setAnalyzeLoading(false);
    }
  };

  const handleFetchInbox = async () => {
    setInboxError("");
    setInboxResults([]);
    setInboxLoading(true);
    try {
      const { results } = await fetchAndAnalyzeEmails({
        email: imapEmail,
        password: imapPassword,
        limit: 10,
      });
      setInboxResults(results);
    } catch (e) {
      setInboxError(e instanceof Error ? e.message : "Fetch failed");
    } finally {
      setInboxLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      <div className="max-w-4xl mx-auto px-4 py-10">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight mb-2">
            Email Prioritizer
          </h1>
          <p className="text-white/60">
            AI-powered email prioritization
          </p>
        </header>

        <nav className="flex gap-2 justify-center mb-8 flex-wrap">
          {(
            [
              ["analyze", "Analyze email"],
              ["inbox", "Connect inbox"],
            ] as const
          ).map(([t, label]) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                tab === t
                  ? "bg-white/15 text-white"
                  : "bg-white/5 text-white/60 hover:bg-white/10"
              }`}
            >
              {label}
            </button>
          ))}
        </nav>

        <main className="space-y-8">
          {tab === "analyze" && (
            <section className="rounded-2xl border border-white/10 bg-white/5 p-6 space-y-4">
              <h2 className="text-xl font-semibold">Analyze an email</h2>
              <input
                type="text"
                placeholder="Subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full rounded-lg bg-white/10 border border-white/20 px-4 py-2.5 text-white placeholder-white/40 outline-none focus:ring-2 focus:ring-sky-500"
              />
              <input
                type="email"
                placeholder="Sender (e.g. boss@company.com)"
                value={sender}
                onChange={(e) => setSender(e.target.value)}
                className="w-full rounded-lg bg-white/10 border border-white/20 px-4 py-2.5 text-white placeholder-white/40 outline-none focus:ring-2 focus:ring-sky-500"
              />
              <textarea
                placeholder="Body"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                rows={4}
                className="w-full rounded-lg bg-white/10 border border-white/20 px-4 py-2.5 text-white placeholder-white/40 outline-none focus:ring-2 focus:ring-sky-500 resize-none"
              />
              <button
                onClick={handleAnalyze}
                disabled={analyzeLoading}
                className="px-5 py-2.5 rounded-lg bg-sky-500 text-white font-medium hover:bg-sky-600 disabled:opacity-50"
              >
                {analyzeLoading ? "Analyzing…" : "Analyze"}
              </button>
              {analyzeError && (
                <p className="text-red-400 text-sm">{analyzeError}</p>
              )}
              {analysis && (
                <AnalysisCard
                  a={analysis}
                  subject={subject || undefined}
                  sender={sender || undefined}
                />
              )}
            </section>
          )}

          {tab === "inbox" && (
            <section className="rounded-2xl border border-white/10 bg-white/5 p-6 space-y-4">
              <h2 className="text-xl font-semibold">Connect your inbox</h2>
              <p className="text-white/60 text-sm">
                Use your email and app password (Gmail: enable 2FA, then create
                an app password)
              </p>
              <p className="text-white/40 text-xs">
                Note: Your email and app password are used only to connect via IMAP and are never stored.
              </p>
              <input
                type="email"
                placeholder="Email"
                value={imapEmail}
                onChange={(e) => setImapEmail(e.target.value)}
                className="w-full rounded-lg bg-white/10 border border-white/20 px-4 py-2.5 text-white placeholder-white/40 outline-none focus:ring-2 focus:ring-sky-500"
              />
              <input
                type="password"
                placeholder="App password"
                value={imapPassword}
                onChange={(e) => setImapPassword(e.target.value)}
                className="w-full rounded-lg bg-white/10 border border-white/20 px-4 py-2.5 text-white placeholder-white/40 outline-none focus:ring-2 focus:ring-sky-500"
              />
              <button
                onClick={handleFetchInbox}
                disabled={inboxLoading}
                className="px-5 py-2.5 rounded-lg bg-sky-500 text-white font-medium hover:bg-sky-600 disabled:opacity-50"
              >
                {inboxLoading ? "Fetching & analyzing…" : "Analyze"}
              </button>
              {inboxError && (
                <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-3">
                  <p className="text-red-400 text-sm">{inboxError}</p>
                </div>
              )}
              {inboxResults.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-medium">Results ({inboxResults.length})</h3>
                  {inboxResults.map((a, i) => (
                    <AnalysisCard
                      key={i}
                      a={a}
                      subject={a.subject}
                      sender={a.sender}
                    />
                  ))}
                </div>
              )}
            </section>
          )}

        </main>

        <footer className="mt-16 text-center text-white/40 text-sm">
          Email Prioritizer
        </footer>
      </div>
    </div>
  );
}
