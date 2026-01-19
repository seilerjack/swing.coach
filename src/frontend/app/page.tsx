
import Hero from "./components/Hero";
import Features from "./components/Features";
import HowItWorks from "./components/HowItWorks";
import CallToAction from "./components/CallToAction";

export default function HomePage() {
  return (
    <main>
      {/* ===================== */}
      {/* Hero Section */}
      {/* ===================== */}
      <Hero />

      {/* ===================== */}
      {/* Features Section */}
      {/* ===================== */}
      <Features />

      {/* ===================== */}
      {/* How It Works */}
      {/* ===================== */}
      <HowItWorks />

      {/* ===================== */}
      {/* CTA */}
      {/* ===================== */}
      <CallToAction />
    </main>
  );
}
