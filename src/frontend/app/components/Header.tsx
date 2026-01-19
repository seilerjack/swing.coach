import Image from "next/image";
import Link from "next/link";

export default function Header() {
  return (
    <header
      className="
        sticky top-0 z-50
        bg-white/80 backdrop-blur
        border-b border-gray-200
        shadow-sm
      "
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        
        {/* Logo */}
        <Link
          href="/#hero"
          className="flex items-center gap-2 cursor-pointer"
        >
          <div className="
            flex items-center gap-3">
            <Image
              src="/logo/logo_mask.png"
              alt="SwingCoach.io"
              width={40}
              height={40}
            />
            <div>
              <p className="text-lg font-semibold text-gray-900 tracking-tight">
                SwingCoach.io
              </p>
              <p className="text-sm text-gray-500">
                AI-Powered Swing Analysis
              </p>
            </div>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-8 text-base font-medium text-gray-700">
          <Link href="/#hero" className="transition-colors hover:text-gray-900">
            Home
          </Link>

          <Link href="/#features" className="transition-colors hover:text-gray-900">
            Features
          </Link>

          <Link
            href="/#how-it-works"
            className="transition-colors hover:text-gray-900"
          >
            How It Works
          </Link>

          <Link
            href="/analyze"
            className="
              rounded bg-black px-5 py-2.5 text-base text-white
              transition-all duration-200
              hover:bg-gray-800 hover:scale-105 active:scale-95
            "
          >
            Get Started
          </Link>
        </nav>
      </div>
    </header>
  );
}
