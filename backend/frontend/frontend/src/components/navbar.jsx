import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Sun, Moon, Menu, X } from "lucide-react";
import { motion } from "framer-motion";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "light");
  const location = useLocation();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    setOpen(false); // close mobile menu on route change
  }, [location]);

  return (
    <header className="bg-white dark:bg-gray-900 shadow-md">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <motion.div
          className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <Link to="/">SkillSync</Link>
        </motion.div>

        {/* Desktop links */}
        <nav className="hidden md:flex items-center space-x-6 text-gray-700 dark:text-gray-200">
          <Link className="hover:text-indigo-600" to="/">Home</Link>
          <Link className="hover:text-indigo-600" to="/dashboard">Dashboard</Link>
          <Link className="hover:text-indigo-600" to="/login">Login</Link>
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label="Toggle theme"
            className="ml-4 p-2 rounded-md border bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </nav>

        {/* Mobile buttons */}
        <div className="md:hidden flex items-center gap-3">
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label="Toggle theme"
            className="p-2 rounded-md border bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <button className="p-2" onClick={() => setOpen(!open)} aria-label="Toggle menu">
            {open ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <motion.div
        initial={{ height: 0 }}
        animate={{ height: open ? "auto" : 0 }}
        className="overflow-hidden md:hidden"
      >
        <div className="px-6 pb-6 space-y-3 flex flex-col">
          <Link to="/" className="py-2 px-3 rounded hover:bg-gray-100 dark:hover:bg-gray-800">Home</Link>
          <Link to="/dashboard" className="py-2 px-3 rounded hover:bg-gray-100 dark:hover:bg-gray-800">Dashboard</Link>
          <Link to="/login" className="py-2 px-3 rounded hover:bg-gray-100 dark:hover:bg-gray-800">Login</Link>
        </div>
      </motion.div>
    </header>
  );
}
