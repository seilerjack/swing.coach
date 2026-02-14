"use client";

import { useState } from "react";
import { Upload } from "lucide-react";

type Props = {
  onSubmit: (formData: FormData) => Promise<void>;
};

export default function AnalysisForm({ onSubmit }: Props) {
  const [experience, setExperience] =
    useState<"Beginner" | "Moderate" | "Advanced" | null>(null);

  const [downTheLineFile, setDownTheLineFile] = useState<File | null>(null);
  const [faceOnFile, setFaceOnFile] = useState<File | null>(null);

  const [isLoading, setIsLoading] = useState(false);

  const isFormValid =
    !!experience &&
    !!downTheLineFile &&
    !!faceOnFile;

  const handleSubmit = async () => {
    if (!isFormValid || isLoading) return;

    const formData = new FormData();
    formData.append("down_the_line", downTheLineFile as File);
    formData.append("face_on", faceOnFile as File);
    formData.append("experience_level", experience);

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
            Upload both swing angles to receive AI-powered analysis and coaching insights
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
          <div className="mb-8">
            <div className="mb-3 flex items-center gap-2">
              <p className="font-medium text-gray-800">
                Experience Level
              </p>

              {/* Tooltip */}
              <div className="group relative">
                <span
                  tabIndex={0}
                  className="flex h-4 w-4 items-center justify-center
                             rounded-full border border-gray-400
                             text-[10px] font-bold text-gray-500
                             cursor-help"
                >
                  i
                </span>

                <div
                  className="pointer-events-none absolute left-0 top-full z-10
                             mt-2 w-56 rounded-lg bg-gray-900 px-3 py-2
                             text-xs text-white opacity-0
                             transition-opacity duration-200
                             group-hover:opacity-100
                             group-focus-within:opacity-100"
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

          {/* Down the Line Upload */}
          <VideoUpload
            label="Down the Line Video"
            tooltipText="Placeholder text explaining ideal Down the Line camera positioning."
            file={downTheLineFile}
            setFile={setDownTheLineFile}
            isLoading={isLoading}
          />

          {/* Face On Upload */}
          <VideoUpload
            label="Face On Video"
            tooltipText="Placeholder text explaining ideal Face On camera positioning."
            file={faceOnFile}
            setFile={setFaceOnFile}
            isLoading={isLoading}
          />

          {/* Submit */}
          <button
            type="submit"
            disabled={!isFormValid || isLoading}
            className={`
              mt-6 w-full rounded-lg py-3 text-sm font-semibold text-white
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
              Please select experience level and upload both swing videos.
            </p>
          )}

        </form>
      </div>
    </section>
  );
}

/* ===================== */
/* Upload Block w Tooltip */
/* ===================== */

function VideoUpload({
  label,
  tooltipText,
  file,
  setFile,
  isLoading,
}: {
  label: string;
  tooltipText: string;
  file: File | null;
  setFile: (file: File | null) => void;
  isLoading: boolean;
}) {
  return (
    <div className="mb-8">
      <div className="mb-2 flex items-center gap-2">
        <label className="font-medium text-gray-800">
          {label}
        </label>

        {/* Tooltip */}
        <div className="group relative">
          <span
            tabIndex={0}
            className="flex h-4 w-4 items-center justify-center
                       rounded-full border border-gray-400
                       text-[10px] font-bold text-gray-500
                       cursor-help"
          >
            i
          </span>

          <div
            className="pointer-events-none absolute left-0 top-full z-10
                       mt-2 w-64 rounded-lg bg-gray-900 px-3 py-2
                       text-xs text-white opacity-0
                       transition-opacity duration-200
                       group-hover:opacity-100
                       group-focus-within:opacity-100"
          >
            <p>{tooltipText}</p>
          </div>
        </div>
      </div>

      <label
        className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 text-center transition-all duration-200
          ${
            file
              ? "border-gray-400 bg-gray-50"
              : "border-gray-300 hover:border-black"
          }
          ${isLoading ? "pointer-events-none opacity-60" : "cursor-pointer"}
        `}
      >
        <Upload className="mb-3 h-6 w-6 text-gray-500" />

        {file ? (
          <>
            <p className="text-sm font-medium text-gray-900">
              {file.name}
            </p>
            <p className="text-xs text-gray-500">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </p>
          </>
        ) : (
          <p className="text-sm text-gray-600">
            Click to upload or drag and drop
          </p>
        )}

        <input
          type="file"
          accept="video/*"
          className="hidden"
          disabled={isLoading}
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
      </label>
    </div>
  );
}
