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
            <p className="mb-3 font-medium text-gray-800">Experience Level</p>
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
            <label className="mb-2 block font-medium text-gray-800">
              Shot Description (optional)
            </label>
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

          {/* Tip */}
          <p className="mt-4 text-center text-xs text-gray-500">
            Pro tip: Ensure your full swing is visible in the frame
          </p>
        </form>
      </div>
    </section>
  );
}
