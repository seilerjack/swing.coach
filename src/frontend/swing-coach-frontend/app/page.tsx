"use client";

import { useState } from "react";

export default function Home() {
  const [video, setVideo] = useState<File | null>(null);
  const [experienceLevel, setExperienceLevel] = useState("beginner");
  const [cameraAngle, setCameraAngle] = useState("down-the-line");
  const [metadata, setMetadata] = useState("");
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!video) {
      setError("Please upload a swing video.");
      return;
    }

    setError(null);
    setLoading(true);
    setAnalysis(null);
    setVideoUrl(null);

    const formData = new FormData();
    formData.append("video", video);
    formData.append("experience_level", experienceLevel);
    formData.append("camera_angle", cameraAngle);
    formData.append("metadata", metadata);

    try {
      const res = await fetch("http://localhost:8000/analysis", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Analysis failed. Please try again.");
      }

      const data = await res.json();

      setAnalysis(data.swing_analysis);
      setVideoUrl(`http://localhost:8000${data.pose_overlay}`);
    } catch (err) {
      setError("Something went wrong during analysis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-4xl space-y-8">
        {/* Header */}
        <header className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            Swing Coach
          </h1>
          <p className="mt-2 text-gray-600">
            Upload your swing and receive biomechanical feedback instantly.
          </p>
        </header>

        {/* Upload Card */}
        <section className="rounded-xl bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold text-gray-800">
            Upload Swing
          </h2>

          <div className="space-y-4">
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setVideo(e.target.files?.[0] || null)}
              className="block w-full text-sm"
            />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Experience Level
                </label>
                <select
                  className="mt-1 w-full rounded border px-3 py-2"
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Camera Angle
                </label>
                <select
                  className="mt-1 w-full rounded border px-3 py-2"
                  value={cameraAngle}
                  onChange={(e) => setCameraAngle(e.target.value)}
                >
                  <option value="down-the-line">Down the Line</option>
                  <option value="face-on">Face On</option>
                </select>
              </div>
            </div>

            <textarea
              placeholder="Describe the shot outcome (e.g. push fade, thin strike)"
              className="w-full rounded border p-3 text-sm"
              rows={3}
              onChange={(e) => setMetadata(e.target.value)}
            />

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full rounded bg-black px-4 py-2 text-white hover:bg-gray-800 disabled:opacity-50"
            >
              {loading ? "Analyzing Swing..." : "Analyze Swing"}
            </button>

            {error && (
              <p className="text-sm text-red-600">{error}</p>
            )}
          </div>
        </section>

        {/* Results */}
        {(analysis || videoUrl) && (
          <section className="grid gap-6 md:grid-cols-2">
            {/* Video */}
            {videoUrl && (
              <div className="rounded-xl bg-white p-4 shadow">
                <h3 className="mb-2 font-semibold text-gray-800">
                  Pose Overlay
                </h3>
                <video
                  key={videoUrl}
                  src={videoUrl}
                  controls
                  autoPlay // Enable autoplay (camelCase in JSX)
                  loop     // Loop the video continuously
                  muted    // Mute the video to bypass browser autoplay policies
                  playsInline // Required for autoplay on iOS devices to prevent fullscreen by default
                  className="w-full rounded"
                />
              </div>
            )}

            {/* Analysis */}
            {analysis && (
              <div className="rounded-xl bg-white p-4 shadow">
                <h3 className="mb-2 font-semibold text-gray-800">
                  Coaching Feedback
                </h3>
                <div className="space-y-2 text-sm text-gray-700 whitespace-pre-line">
                  {analysis}
                </div>
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
