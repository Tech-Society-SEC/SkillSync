export default function Footer(){
  return (
    <footer className="bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800">
      <div className="max-w-6xl mx-auto px-6 py-6 text-center text-sm text-gray-600 dark:text-gray-400">
        © {new Date().getFullYear()} SkillSync. All rights reserved.
      </div>
    </footer>
  );
}
