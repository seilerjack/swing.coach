
import Image from "next/image";

export default function Hero() {
  return (
    /* ===================== */
    /*      Hero Section     */
    /* ===================== */
    <section id="hero" className="px-6 py-24 text-center">
      <div className="mx-auto max-w-3xl">
        <div className="flex justify-center mb-8">
        <div className="relative">
          <Image
              src="/logo/logo_mask.png"
              alt="SwingCoach.io Logo"
              width={256}
              height={256}
              className="object-contain"
          />
          </div>
        </div>

        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Perfect Your Swing with AI
        </h1>

        <p className="mt-6 text-lg text-gray-600">
          Harness the power of artificial intelligence to analyze your golf
          swing, identify areas for improvement, and take your game to the
          next level.
        </p>

        <div className="mt-10 flex flex-col justify-center gap-4 sm:flex-row">
        <a
          href="/analyze"
          className="
            rounded-md bg-black px-6 py-3 text-white
            transition-all duration-200
            hover:scale-105 hover:bg-gray-900
            active:scale-95
          "
        >
          Start Analysis →
        </a>

        <button className="
          rounded-lg border px-6 py-3
          transition-all duration-200
          hover:scale-105 active:scale-95
          "
        >
          Watch Demo
        </button>
        </div>
      </div>
    </section>
  );
}
