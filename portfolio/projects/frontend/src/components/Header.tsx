import { Link } from "react-router-dom";

function Header() {
  return (
    <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
        <Link to="/" className="text-xl font-semibold text-emerald-400">
          Portfolio Platform
        </Link>
        <nav className="space-x-4 text-sm text-slate-300">
          <a href="https://github.com/sams-jackson" target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href="https://www.linkedin.com/in/sams-jackson" target="_blank" rel="noreferrer">
            LinkedIn
          </a>
        </nav>
      </div>
    </header>
  );
}

export default Header;
