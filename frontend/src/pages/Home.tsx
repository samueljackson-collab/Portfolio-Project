function Home() {
  return (
    <section className="space-y-6">
      <header className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-primary">Samuel Jackson - Systems Development Engineer</h1>
        <p className="text-gray-600">Building secure, scalable systems with visibility baked in.</p>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Spotlight the themes showcased in the dashboard. */}
        {["Infrastructure automation", "Observability dashboards", "Quality engineering"].map((item) => (
          <div key={item} className="bg-white shadow rounded p-4">
            <h2 className="text-lg font-semibold text-secondary">{item}</h2>
            <p className="text-sm text-gray-600">Detailed guides, code samples, and runbooks showcasing production-ready delivery.</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Home;
