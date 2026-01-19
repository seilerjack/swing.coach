
import { Loader2 } from "lucide-react";

export default function AnalysisLoading() {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border bg-white py-20 text-center shadow-sm">
      
      <Loader2 className="mb-6 h-10 w-10 animate-spin text-gray-900" />

      <h2 className="mb-2 text-xl font-semibold">
        Analyzing Your Swing
      </h2>

      <p className="max-w-sm text-sm text-gray-600">
        Our AI is reviewing posture, alignment, tempo, and movement patterns.
        This usually takes a few seconds.
      </p>

    </div>
  );
}
