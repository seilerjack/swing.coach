"use client";

import { TrendingUp, Lightbulb } from "lucide-react";
import { useState } from "react";
import AnalysisForm from "./AnalysisForm";
import AnalysisLoading from "./AnalysisLoading";

/* ===================== */
/*        Types          */
/* ===================== */

type CategoryScore = {
  name: string;
  score: number;
  summary: string;
};

type SwingAnalysis = {
  swingAnalysis: string;
  keyObservations: string[];
  coachingTips: string[];
  letterGrade: string;

  overallScore: number;
  categoryScores: CategoryScore[];
};

type AnalysisResponse = {
  swing_analysis: SwingAnalysis;
  pose_overlay: string;
};

/* ===================== */
/*   Utility Helpers     */
/* ===================== */

export function getScoreColor(score: number) {
  if (score >= 85) return "bg-green-500";
  if (score >= 70) return "bg-orange-500";
  return "bg-red-500";
}

/* ===================== */
/*     Page Wrapper      */
/* ===================== */

export default function AnalyzePage() {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleReset = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
    setResult(null);
  };

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
    <main className="relative mx-auto max-w-6xl px-6 py-12">
      {!result && !isLoading && <AnalysisForm onSubmit={handleAnalyze} />}
      {isLoading && <AnalysisLoading />}
      {result && <ResultsSection result={result} onReset={handleReset} />}
    </main>
  );
}

/* ===================== */
/*     Results UI        */
/* ===================== */

function ResultsSection({ result, onReset }: { result: AnalysisResponse; onReset: () => void }) {
  const { swing_analysis, pose_overlay } = result;

  const sortedCategories = [...swing_analysis.categoryScores].sort(
    (a, b) => a.score - b.score
  );

  const topPriorityFix = sortedCategories[0];

  return (
    <section className="grid gap-10 lg:grid-cols-[420px_1fr] items-start">

      {/* ===================== */}
      {/*      LEFT COLUMN      */}
      {/* ===================== */}
      <div className="space-y-6">
        <div className="rounded-2xl bg-white shadow-sm ring-1 ring-gray-200/60">
          <video
            src={`http://localhost:8000${pose_overlay}`}
            autoPlay
            loop
            muted
            playsInline
            preload="metadata"
            className="w-full rounded-2xl bg-black"
          />
        </div>

        <details className="group rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200/60">
          <summary className="flex cursor-pointer list-none items-center justify-between font-semibold">
            <span>Key Points Analysis</span>
            <span className="text-sm text-gray-500 group-open:hidden">
              Expand
            </span>
            <span className="hidden text-sm text-gray-500 group-open:inline">
              Collapse
            </span>
          </summary>

          <div className="mt-4 space-y-4">
            {sortedCategories.map((category) => {
              const barColor = getScoreColor(category.score);

              return (
                <div key={category.name}>
                  <div className="mb-1 flex justify-between text-sm font-medium">
                    <span>{category.name}</span>
                    <span className="text-gray-600">
                      {category.score}/100
                    </span>
                  </div>

                  <p className="mb-2 text-sm text-gray-700">
                    {category.summary}
                  </p>

                  <div className="h-2 w-full rounded bg-gray-200">
                    <div
                      className={`h-2 rounded ${barColor}`}
                      style={{ width: `${category.score}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </details>
      </div>

      {/* ===================== */}
      {/*     RIGHT COLUMN     */}
      {/* ===================== */}
      <div className="space-y-10">
        <div className="rounded-2xl bg-green-50 p-8 text-center">
          <p className="text-sm font-semibold uppercase tracking-wide text-green-700">
            Overall Score
          </p>
          <p className="mt-2 text-6xl font-bold text-gray-900">
            {swing_analysis.overallScore}
          </p>
          <p className="text-sm text-gray-600">
            out of 100 • Grade {swing_analysis.letterGrade}
          </p>
        </div>

        <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200/60">
          <div className="mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-semibold">Technical Analysis</h3>
          </div>

          <p className="text-sm leading-relaxed text-gray-700">
            {swing_analysis.swingAnalysis}
          </p>
        </div>

        <div className="rounded-2xl border-l-4 border-orange-500 bg-orange-50 p-6">
          <h4 className="mb-1 text-sm font-semibold uppercase tracking-wide text-orange-700">
            Top Priority Fix
          </h4>
          <p className="text-base font-semibold text-gray-900">
            {topPriorityFix.name}
          </p>
          <p className="mt-2 text-sm text-gray-700">
            {topPriorityFix.summary}
          </p>
          <p className="mt-3 text-xs text-gray-600">
            Score: {topPriorityFix.score}/100
          </p>
        </div>

        <details className="group rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200/60">
          <summary className="flex cursor-pointer list-none items-center gap-2 font-semibold">
            <Lightbulb className="h-5 w-5 text-yellow-600" />
            Coaching Tips
          </summary>

          <ul className="mt-4 space-y-3 text-sm">
            {swing_analysis.coachingTips.map((tip, i) => (
              <li
                key={i}
                className="rounded-lg border-l-4 border-orange-500 bg-orange-50 px-4 py-3 text-gray-800"
              >
                {tip}
              </li>
            ))}
          </ul>
        </details>

        <div className="pointer-events-none sticky bottom-6 flex justify-end">
          <button
            onClick={onReset}
            className="
            pointer-events-auto
            rounded-full bg-gray-900 px-5 py-3
              text-sm font-semibold text-white
              shadow-lg transition
              hover:bg-gray-800 hover:scale-105
              active:scale-95
              "
              >
            Analyze another swing
          </button>
        </div>
      </div>

    </section>
  );
}
