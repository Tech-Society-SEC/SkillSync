import { motion } from "framer-motion";

export default function Login(){
  return (
    <div className="min-h-[70vh] flex items-center justify-center px-6">
      <motion.div initial={{ scale: 0.98, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.35 }} className="max-w-md w-full bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6">
        <h2 className="text-2xl font-bold text-indigo-600 mb-4">Welcome back</h2>
        <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">Sign in to access your SkillSync profile and job matches.</p>

        <label className="text-sm text-gray-600 dark:text-gray-300">Email</label>
        <input className="w-full p-3 border rounded mt-2 mb-4 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700" placeholder="you@example.com" />

        <label className="text-sm text-gray-600 dark:text-gray-300">Password</label>
        <input type="password" className="w-full p-3 border rounded mt-2 mb-4 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700" placeholder="••••••" />

        <button className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700">Sign in</button>

        <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">Don't have an account? <a href="#" className="text-indigo-600">Sign up</a></div>
      </motion.div>
    </div>
  );
}
