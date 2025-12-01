import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const App = () => (
  <main className="app-shell">
    <section>
      <h1>PRJ-AWS-001 Frontend</h1>
      <p>
        Minimal React/Vite scaffold to exercise the backend API and visualize
        CloudFormation drift checks.
      </p>
      <pre className="callout">GET /status → stack/region/drift metadata</pre>
      <p>
        Wire this view to the FastAPI backend before adding charts or
        environment toggles.
      </p>
    </section>
  </main>
);

const root = createRoot(document.getElementById("root")!);
root.render(<App />);
