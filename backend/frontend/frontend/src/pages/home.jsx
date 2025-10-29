import { Link } from "react-router-dom";
import { motion } from "framer-motion";

export default function Home() {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 to-white dark:from-indigo-900 dark:to-gray-800 opacity-90"></div>

      <div className="relative max-w-6xl mx-auto px-6 py-24">
        <div className="grid md:grid-cols-2 gap-10 items-center">
          <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ duration: 0.6 }}>
            <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white leading-tight">
              Empower your career with <span className="text-indigo-600 dark:text-indigo-400">SkillSync</span>
            </h1>
            <p className="mt-6 text-gray-700 dark:text-gray-300 max-w-xl">
              Speak in your native language, discover your strengths, get matched to jobs, and follow curated learning paths — all in one place.
            </p>

            <div className="mt-8 flex gap-4">
              <Link to="/dashboard" className="bg-indigo-600 text-white px-6 py-3 rounded-lg shadow hover:bg-indigo-700 transition">
                Get My Match
              </Link>
              <Link to="/login" className="px-6 py-3 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition">
                Sign in
              </Link>
            </div>

            <div className="mt-6 text-sm text-gray-600 dark:text-gray-400">
              Example: “I am a mason with 5 years experience in plastering and brickwork”.
            </div>
          </motion.div>

          <motion.div initial={{ scale: 0.97, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.6 }}>
            <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-indigo-600 mb-3">Quick Demo</h3>
              <p className="text-gray-700 dark:text-gray-300">Paste a short transcript to see how SkillSync extracts skills and suggests jobs.</p>

              <DemoCard />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

function DemoCard(){
  const example = "I am a mason with 5 years experience good at brickwork and plastering.";
  return (
    <div className="mt-6">
      <textarea defaultValue={example} className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-sm" rows={4} />
      <div className="mt-4 flex gap-2">
        <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">Analyze</button>
        <button className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700">Clear</button>
      </div>
      <small className="text-gray-500 dark:text-gray-400 block mt-3">This demo is local only — backend integration comes next.</small>
    </div>
  );
}
