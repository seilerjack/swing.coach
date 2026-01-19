
import HowItWorksStep from "./HowItWorksStep";
import { Upload, Play, BarChart3 } from "lucide-react";

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24">
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-3xl font-bold text-center mb-4">
          How It Works
        </h2>

        <p className="text-center text-gray-600 max-w-2xl mx-auto mb-16">
          Get started with SwingCoach.io in three simple steps. It&apos;s fast,
          easy, and designed for golfers of all skill levels.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 justify-items-center">
          <HowItWorksStep
            step={1}
            icon={Upload}
            title="Upload Your Video"
            description="Record your swing from any angle and upload it to our platform. We support all major video formats."
          />

          <HowItWorksStep
            step={2}
            icon={Play}
            title="AI Analysis"
            description="Our AI processes your swing in seconds, analyzing posture, alignment, tempo, and more."
          />

          <HowItWorksStep
            step={3}
            icon={BarChart3}
            title="Get Insights"
            description="Review detailed feedback, visualizations, and personalized tips to improve your technique."
          />
        </div>
      </div>
    </section>
  );
}
