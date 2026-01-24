"use client";

import { useState } from "react";
import { Upload } from "lucide-react";

type Props = {
  onSubmit: (formData: FormData) => Promise<void>;
};

export default function AnalysisForm({ onSubmit }: Props) {
  const [experience, setExperience] =
    useState<"Beginner" | "Moderate" | "Advanced" | null>(null);
  const [cameraAngle, setCameraAngle] =
    useState<"Down the Line" | "Face On" | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [shotNotes, setShotNotes] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const EXPERIENCE_HELP = {
    Beginner: "18+ handicap",
    Moderate: "18-10 handicap",
    Advanced: "<10 handicap",
  };

  /* ===================== */
  /*   Form Validation     */
  /* ===================== */
  const isFormValid =
    !!experience &&
    !!cameraAngle &&
    !!videoFile;

  const handleSubmit = async () => {
    if (!isFormValid || isLoading) return;

    const formData = new FormData();
    formData.append("video", videoFile as File);
    formData.append("experience_level", experience);
    formData.append("camera_angle", cameraAngle);
    formData.append("metadata", shotNotes);

    try {
      setIsLoading(true);
      await onSubmit(formData);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="mx-auto mt-12 max-w-3xl px-6">
      <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-semibold text-gray-900">
            Analyze Your Swing
          </h1>
          <p className="mt-2 text-gray-600">
            Upload your swing video to receive AI-powered analysis and coaching insights
          </p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          className="rounded-xl border bg-white p-8 shadow-sm"
        >
          {/* Experience Level */}
          <div className="mb-6">
            <div className="mb-3 flex items-center gap-2">
              <p className="font-medium text-gray-800">
                Experience Level
              </p>

              <div className="group relative">
                <span
                  tabIndex={0}
                  className="
                    flex h-4 w-4 items-center justify-center
                    rounded-full border border-gray-400
                    text-[10px] font-bold text-gray-500
                    cursor-help
                  "
                >
                  i
                </span>

                {/* Tooltip */}
                <div
                  className="
                    pointer-events-none absolute left-0 top-full z-10
                    mt-2 w-56 rounded-lg bg-gray-900 px-3 py-2
                    text-xs text-white opacity-0
                    transition-opacity duration-200
                    group-hover:opacity-100
                    group-focus-within:opacity-100
                  "
                >
                  <p><strong>Beginner:</strong> 18+ handicap</p>
                  <p className="mt-1"><strong>Moderate:</strong> 18-10 handicap</p>
                  <p className="mt-1"><strong>Advanced:</strong> &lt;10 handicap</p>
                </div>
              </div>
            </div>
            <div className="flex gap-3">
              {["Beginner", "Moderate", "Advanced"].map((level) => (
                <button
                  key={level}
                  type="button"
                  disabled={isLoading}
                  onClick={() => setExperience(level as any)}
                  className={`flex-1 rounded-lg border px-4 py-3 text-sm font-medium transition-all duration-200
                    ${
                      experience === level
                        ? "border-black bg-gray-100"
                        : "border-gray-300 hover:scale-105"
                    }
                    ${isLoading ? "cursor-not-allowed opacity-60" : ""}
                  `}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Camera Angle */}
          <div className="mb-6">
            <p className="mb-3 font-medium text-gray-800">Camera Angle</p>
            <div className="flex gap-3">
              {["Down the Line", "Face On"].map((angle) => (
                <button
                  key={angle}
                  type="button"
                  disabled={isLoading}
                  onClick={() => setCameraAngle(angle as any)}
                  className={`flex-1 rounded-lg border px-4 py-3 text-sm font-medium transition-all duration-200
                    ${
                      cameraAngle === angle
                        ? "border-black bg-gray-100"
                        : "border-gray-300 hover:scale-105"
                    }
                    ${isLoading ? "cursor-not-allowed opacity-60" : ""}
                  `}
                >
                  {angle}
                </button>
              ))}
            </div>
          </div>

          {/* Shot Notes */}
          <div className="mb-6">
            <div className="mb-2 flex items-center gap-2">
              <label className="font-medium text-gray-800">
                Shot Description (optional)
              </label>

              <div className="group relative">
                <span
                  tabIndex={0}
                  className="
                    flex h-4 w-4 items-center justify-center
                    rounded-full border border-gray-400
                    text-[10px] font-bold text-gray-500
                    cursor-help
                  "
                >
                  i
                </span>

                {/* Tooltip */}
                <div
                  className="
                    pointer-events-none absolute left-0 top-full z-10
                    mt-2 w-64 rounded-lg bg-gray-900 px-3 py-2
                    text-xs text-white opacity-0
                    transition-opacity duration-200
                    group-hover:opacity-100
                    group-focus-within:opacity-100
                  "
                >
                  {/* You fill this in */}
                  <p>
                    Best results come when providing the AI context about your shots results. i.e. "missed left", "felt off balance", "hit a draw".
                  </p>
                </div>
              </div>
            </div>

            <textarea
              value={shotNotes}
              disabled={isLoading}
              onChange={(e) => setShotNotes(e.target.value)}
              placeholder="What are you working on? Any misses or feels?"
              className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 text-sm focus:border-black focus:outline-none disabled:opacity-60"
              rows={3}
            />
          </div>

          {/* Video Upload */}
          <div className="mb-8">
            <label className="mb-2 block font-medium text-gray-800">
              Swing Video
            </label>
            <label
              htmlFor="video-upload"
              className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 text-center transition-all duration-200
                ${
                  videoFile
                    ? "border-gray-400 bg-gray-50"
                    : "border-gray-300 hover:border-black"
                }
                ${isLoading ? "pointer-events-none opacity-60" : "cursor-pointer"}
              `}
            >
              <Upload className="mb-3 h-6 w-6 text-gray-500" />
              {videoFile ? (
                <>
                  <p className="text-sm font-medium text-gray-900">
                    {videoFile.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(videoFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </>
              ) : (
                <p className="text-sm text-gray-600">
                  Click to upload or drag and drop your swing video
                </p>
              )}
              <input
                id="video-upload"
                type="file"
                accept="video/*"
                className="hidden"
                disabled={isLoading}
                onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
              />
            </label>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={!isFormValid || isLoading}
            className={`
              w-full rounded-lg py-3 text-sm font-semibold text-white
              transition-all duration-200
              ${
                !isFormValid || isLoading
                  ? "bg-gray-300 cursor-not-allowed"
                  : "bg-black hover:scale-105 hover:bg-gray-800"
              }
            `}
          >
            {isLoading ? "Analyzing…" : "Analyze My Swing"}
          </button>

          {!isFormValid && !isLoading && (
            <p className="mt-3 text-center text-xs text-gray-500">
              Please select an experience level, camera angle, and upload a video.
            </p>
          )}

        </form>
      </div>
    </section>
  );
}
