import Link from "next/link";

export function Header() {
  return (
    <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="font-bold text-xl">
            LLM Dashboard
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Link href="/chat" className="text-gray-600 hover:text-gray-900">
              Chat
            </Link>
            <Link href="/#" className="text-gray-600 hover:text-gray-900">
              Settings
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <p className="text-sm text-gray-600">Admin Panel</p>
        </div>
      </div>
    </header>
  );
}
