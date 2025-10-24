import { useEffect, useState } from "react";
import { fetchHealth } from "../lib/api";

function Home() {
  const [status, setStatus] = useState<string>("Checking...");
  const [timestamp, setTimestamp] = useState<string>("");

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchHealth();
        setStatus(data.status === "ok" ? "API is healthy" : "API reported an issue");
        setTimestamp(new Date().toLocaleTimeString());
      } catch (error) {
        setStatus("Unable to reach API");
      }
    };

    void load();
  }, []);

  return (
    <section className="space-y-6 rounded-lg border border-slate-800 bg-slate-900/60 p-6 shadow-lg">
      <h1 className="text-3xl font-bold text-emerald-300">Welcome</h1>
      <p className="text-slate-300">
        This portfolio stack demonstrates a production-style FastAPI backend, React frontend, Terraform infrastructure, and
        CI/CD automation.
      </p>
      <div className="rounded-md border border-slate-700 bg-slate-900/70 p-4">
        <p className="font-semibold text-slate-200">Backend health</p>
        <p className="text-sm text-slate-400">{status}</p>
        {timestamp && (
          <p className="text-xs text-slate-500">Last checked at {timestamp}</p>
        )}
      </div>
    </section>
  );
}

export default Home;
