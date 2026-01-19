import { Camera, Brain, BarChart3, Zap } from "lucide-react";
import FeatureCard from "./FeatureCard";

export default function Features() {
  return (
    <section id="features" className="bg-gray-50 py-20">
      <div className="mx-auto max-w-6xl px-6">
        <h2 className="mb-4 text-center text-3xl font-bold">
          Elevate Your Game
        </h2>
        <p className="mb-12 text-center text-gray-600">
          Professional-grade swing analysis powered by AI.
        </p>

        <div className="grid gap-6 md:grid-cols-2">
          <FeatureCard
            icon={<Camera className="h-5 w-5" />}
            title="Video Analysis"
            description="Upload your swing and receive frame-by-frame insights."
          />
          <FeatureCard
            icon={<Brain className="h-5 w-5" />}
            title="AI Intelligence"
            description="Detect subtle movement patterns even pros miss."
          />
          <FeatureCard
            icon={<BarChart3 className="h-5 w-5" />}
            title="Track Progress"
            description="Monitor improvement with metrics over time."
          />
          <FeatureCard
            icon={<Zap className="h-5 w-5" />}
            title="Instant Feedback"
            description="Actionable coaching suggestions in seconds."
          />
        </div>
      </div>
    </section>
  );
}
