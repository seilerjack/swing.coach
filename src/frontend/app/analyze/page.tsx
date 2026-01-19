"use client";

import { useState } from "react";
import AnalysisForm from "./AnalysisForm";
import AnalysisLoading from "./AnalysisLoading";

type SwingAnalysis = {
  swingAnalysis: string;
  keyObservations: string[];
  coachingTips: string[];
  letterGrade: string;
};

type AnalysisResponse = {
  swing_analysis: SwingAnalysis;
  pose_overlay: string;
};

export default function AnalyzePage() {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = async (formData: FormData) => {
    try {
      setIsLoading(true);

      const res = await fetch("http://localhost:8000/analysis", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Analysis failed");
      }

      const data: AnalysisResponse = await res.json();
      setResult(data);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      {!result && !isLoading && (
        <AnalysisForm onSubmit={handleAnalyze} />
      )}

      {isLoading && (
        <AnalysisLoading />
      )}

      {result && (
        <ResultsSection result={result} />
      )}
    </main>
  );
}

/* ===================== */
/*     Results UI        */
/* ===================== */

function ResultsSection({ result }: { result: AnalysisResponse }) {
  const { swing_analysis, pose_overlay } = result;

  return (
    <section className="grid gap-10 lg:grid-cols-2">
      
      {/* Video */}
      <div className="rounded-2xl border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold">
          Swing Overlay
        </h2>

        <video
          src={`http://localhost:8000${pose_overlay}`}
          autoPlay
          loop
          muted
          playsInline
          className="w-full rounded-xl border"
        />
      </div>

      {/* Analysis */}
      <div className="space-y-8">
        
        {/* Summary + Grade */}
        <div className="rounded-2xl border bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              Swing Summary
            </h2>

            <span className="rounded-lg bg-gray-900 px-3 py-1 text-sm font-semibold text-white">
              Grade: {swing_analysis.letterGrade}
            </span>
          </div>

          <p className="text-sm leading-relaxed text-gray-700">
            {swing_analysis.swingAnalysis}
          </p>
        </div>

        {/* Key Observations */}
        <div className="rounded-2xl border bg-white p-6 shadow-sm">
          <h3 className="mb-3 text-md font-semibold">
            Key Observations
          </h3>

          <ul className="list-disc space-y-2 pl-5 text-sm text-gray-700">
            {swing_analysis.keyObservations.map((obs, i) => (
              <li key={i}>{obs}</li>
            ))}
          </ul>
        </div>

        {/* Coaching Tips */}
        <div className="rounded-2xl border bg-white p-6 shadow-sm">
          <h3 className="mb-3 text-md font-semibold">
            Coaching Tips
          </h3>

          <ul className="list-disc space-y-2 pl-5 text-sm text-gray-700">
            {swing_analysis.coachingTips.map((tip, i) => (
              <li key={i}>{tip}</li>
            ))}
          </ul>
        </div>

      </div>
    </section>
  );
}
