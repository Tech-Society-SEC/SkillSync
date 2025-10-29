import { motion } from "framer-motion";

export default function Dashboard(){
  const skills = ["Masonry","Plastering","Brickwork"];
  const jobs = [
    { title: "Local Mason (Chennai)", link: "#" },
    { title: "Construction Assistant (Hyderabad)", link: "#" }
  ];
  const resources = [
    { title: "Masonry Basics - YouTube", url: "https://youtu.be/example" },
    { title: "Free construction course - Coursera", url: "https://coursera.org" }
  ];

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <motion.h2 initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-3xl font-bold text-gray-900 dark:text-white mb-6">Dashboard</motion.h2>

      <div className="grid md:grid-cols-3 gap-6">
        <motion.div initial={{ y: 8, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-white dark:bg-gray-900 rounded-xl shadow p-5">
          <h3 className="font-semibold text-indigo-600 mb-2">Extracted Skills</h3>
          <ul className="list-disc list-inside text-gray-700 dark:text-gray-300">
            {skills.map((s,i) => <li key={i}>{s}</li>)}
          </ul>
        </motion.div>

        <motion.div initial={{ y: 8, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.05 }} className="bg-white dark:bg-gray-900 rounded-xl shadow p-5">
          <h3 className="font-semibold text-indigo-600 mb-2">Recent Job Matches</h3>
          <ul className="text-gray-700 dark:text-gray-300">
            {jobs.map((j,i) => <li key={i} className="py-1"><a href={j.link} className="text-indigo-600 hover:underline">{j.title}</a></li>)}
          </ul>
        </motion.div>

        <motion.div initial={{ y: 8, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 }} className="bg-white dark:bg-gray-900 rounded-xl shadow p-5">
          <h3 className="font-semibold text-indigo-600 mb-2">Learning Resources</h3>
          <ul className="text-gray-700 dark:text-gray-300">
            {resources.map((r,i) => <li className="py-1" key={i}><a className="text-indigo-600 hover:underline" href={r.url}>{r.title}</a></li>)}
          </ul>
        </motion.div>
      </div>

      <div className="mt-8 bg-white dark:bg-gray-900 rounded-xl shadow p-5">
        <h3 className="font-semibold text-indigo-600 mb-2">Improvement Tips</h3>
        <p className="text-gray-700 dark:text-gray-300">Enroll in short courses for advanced plastering techniques and health & safety.</p>
      </div>
    </div>
  );
}
