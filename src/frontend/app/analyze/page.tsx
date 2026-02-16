"use client";

import { TrendingUp, Lightbulb } from "lucide-react";
import { useState, useEffect, useRef } from "react";
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
  analysis_id: string;
};

/* ===================== */
/*   Utility Helpers     */
/* ===================== */

function getScoreColor(score: number) {
  if (score >= 85) return "#10b981";
  if (score >= 70) return "#f59e0b";
  return "#ef4444";
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

      if (!res.ok) throw new Error("Analysis failed");

      const data: AnalysisResponse = await res.json();
      setResult(data);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="relative mx-auto max-w-7xl px-6 py-14">
      {!result && !isLoading && <AnalysisForm onSubmit={handleAnalyze} />}
      {isLoading && <AnalysisLoading />}
      {result && <ResultsSection result={result} onReset={handleReset} />}
    </main>
  );
}

/* ===================== */
/*     Results UI        */
/* ===================== */

function ResultsSection({
  result,
  onReset,
}: {
  result: AnalysisResponse;
  onReset: () => void;
}) {
  const { swing_analysis, analysis_id } = result;

  const sortedCategories = [...swing_analysis.categoryScores].sort(
    (a, b) => a.score - b.score
  );

  const topPriorityFix = sortedCategories[0];

  const [animatedScore, setAnimatedScore] = useState(0);
  const [collapsed, setCollapsed] = useState(false);
  const headerRef = useRef<HTMLDivElement | null>(null);

  /* Count Up Animation */
  useEffect(() => {
    let start = 0;
    const end = swing_analysis.overallScore;
    const duration = 1200;
    const stepTime = 16;
    const increment = end / (duration / stepTime);

    const counter = setInterval(() => {
      start += increment;
      if (start >= end) {
        start = end;
        clearInterval(counter);
      }
      setAnimatedScore(Math.round(start));
    }, stepTime);

    return () => clearInterval(counter);
  }, [swing_analysis.overallScore]);

  /* Collapse when scrolled past header section */
  useEffect(() => {
    const handleScroll = () => {
      if (!headerRef.current) return;
      const rect = headerRef.current.getBoundingClientRect();
      setCollapsed(rect.bottom < 120);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const strokeColor = getScoreColor(animatedScore);

  /* Large */
  const largeRadius = 70;
  const largeCircumference = 2 * Math.PI * largeRadius;

  return (
    <section className="relative space-y-16">

      {/* ===================== */}
      {/* TOP SECTION           */}
      {/* ===================== */}

      <div
        ref={headerRef}
        className="grid gap-10 lg:grid-cols-4 items-stretch"
      >
        {/* Score (1/4 width) */}
        <div className="rounded-3xl bg-white p-10 shadow-xl ring-1 ring-gray-200 h-full flex flex-col items-center justify-center">

          <p className="text-sm font-semibold uppercase tracking-wide text-gray-500 mb-6">
            Overall Swing Score
          </p>

          <div className="relative h-44 w-44">
            <svg className="-rotate-90 h-44 w-44">
              <circle
                cx="88"
                cy="88"
                r={largeRadius}
                strokeWidth="12"
                stroke="#e5e7eb"
                fill="none"
              />
              <circle
                cx="88"
                cy="88"
                r={largeRadius}
                strokeWidth="12"
                stroke={strokeColor}
                fill="none"
                strokeDasharray={largeCircumference}
                strokeDashoffset={
                  largeCircumference * (1 - animatedScore / 100)
                }
                strokeLinecap="round"
              />
            </svg>

            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-5xl font-bold">
                {animatedScore}
              </span>
              <span className="text-sm text-gray-500 mt-1">
                Grade {swing_analysis.letterGrade}
              </span>
            </div>
          </div>

        </div>

        {/* Technical Analysis (3/4 width) */}
        <div className="lg:col-span-3 rounded-3xl bg-white p-10 shadow-xl ring-1 ring-gray-200">
          <div className="mb-6 flex items-center gap-3">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <h3 className="text-xl font-semibold">
              Technical Analysis
            </h3>
          </div>

          <p className="text-[15px] leading-7 text-gray-700">
            {swing_analysis.swingAnalysis}
          </p>
        </div>
      </div>

      {/* ===================== */}
      {/* VIDEOS                */}
      {/* ===================== */}

      <div className="grid gap-10 lg:grid-cols-2">
        <video
          src={`http://localhost:8000/analysis/${analysis_id}/overlay/face_on`}
          autoPlay
          loop
          muted
          controls
          playsInline
          preload="metadata"
          className="w-full rounded-2xl shadow-xl"
        />

        <video
          src={`http://localhost:8000/analysis/${analysis_id}/overlay/down_the_line`}
          autoPlay
          loop
          muted
          controls
          playsInline
          preload="metadata"
          className="w-full rounded-2xl shadow-xl"
        />
      </div>

      {/* ===================== */}
      {/* LOWER GRID            */}
      {/* ===================== */}

      <div className="grid gap-10 lg:grid-cols-3">

        <div className="rounded-3xl bg-white p-8 shadow-xl ring-1 ring-gray-200">
          <h3 className="mb-6 text-lg font-semibold">
            Performance Breakdown
          </h3>

          <div className="space-y-6">
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

                  <p className="mb-2 text-sm text-gray-600">
                    {category.summary}
                  </p>

                  <div className="h-2 w-full rounded bg-gray-200">
                    <div
                      className="h-2 rounded"
                      style={{
                        width: `${category.score}%`,
                        backgroundColor: barColor,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="rounded-3xl border-l-4 border-orange-500 bg-orange-50 p-8">
          <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-orange-700">
            Top Priority Fix
          </h4>
          <p className="text-base font-semibold text-gray-900">
            {topPriorityFix.name}
          </p>
          <p className="mt-3 text-sm text-gray-700">
            {topPriorityFix.summary}
          </p>
        </div>

        <div className="rounded-3xl bg-white p-8 shadow-xl ring-1 ring-gray-200">
          <div className="mb-4 flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-yellow-600" />
            <h3 className="text-lg font-semibold">
              Coaching Tips
            </h3>
          </div>

          <ul className="space-y-3 text-sm">
            {swing_analysis.coachingTips.map((tip, i) => (
              <li
                key={i}
                className="rounded-lg border-l-4 border-orange-500 bg-orange-50 px-4 py-3 text-gray-800"
              >
                {tip}
              </li>
            ))}
          </ul>
        </div>

      </div>

      <div className="pointer-events-none sticky bottom-6 flex justify-end">
        <button
          onClick={onReset}
          className="pointer-events-auto rounded-full bg-gray-900 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-gray-800 hover:scale-105 active:scale-95"
        >
          Analyze another swing
        </button>
      </div>

    </section>
  );
}
