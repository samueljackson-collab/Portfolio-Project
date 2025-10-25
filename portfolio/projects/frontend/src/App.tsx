import React, { useEffect, useState } from 'react';
import { fetchHealth, fetchProjects, Project, HealthResponse } from './api/client';
import HealthStatus from './components/HealthStatus';

const App: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoadingHealth, setIsLoadingHealth] = useState(true);

  useEffect(() => {
    async function loadProjects() {
      try {
        const data = await fetchProjects();
        setProjects(data);
      } catch (error) {
        console.error('Failed to load projects', error);
      } finally {
        setIsLoadingProjects(false);
      }
    }

    async function loadHealth() {
      try {
        const data = await fetchHealth();
        setHealth(data);
      } catch (error) {
        console.error('Failed to load health', error);
      } finally {
        setIsLoadingHealth(false);
      }
    }

    void loadProjects();
    void loadHealth();
  }, []);

  return (
    <div className="app">
      <header>
        <h1>Portfolio Showcase</h1>
        <HealthStatus health={health} isLoading={isLoadingHealth} />
      </header>
      <main>
        {isLoadingProjects ? (
          <p>Loading projects…</p>
        ) : (
          <section className="projects">
            {projects.map((project) => (
              <article key={project.id} className="project-card">
                <h2>{project.name}</h2>
                <p>{project.description}</p>
                <div className="tags">
                  {project.tags.map((tag) => (
                    <span key={tag} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
                <a href={project.url} className="cta" target="_blank" rel="noreferrer">
                  View project
                </a>
              </article>
            ))}
          </section>
        )}
      </main>
    </div>
  );
};

export default App;
