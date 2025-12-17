// To run use npm run dev from swing-coach-frontend

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

  const handleSubmit = async () => {
    if (!video) return alert("Please upload a video");

    const formData = new FormData();
    formData.append("video", video);
    formData.append("experience_level", experienceLevel);
    formData.append("camera_angle", cameraAngle);
    formData.append("metadata", metadata);

    setLoading(true);

    const res = await fetch("http://localhost:8000/analysis", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    console.log( data )

    setAnalysis(data.swing_analysis);
    setVideoUrl(`http://localhost:8000${data.pose_overlay}`);
    setLoading(false);
  };

  return (
    <main style={{ padding: 20 }}>
      <h1>Swing Coach MVP</h1>

      <input
        type="file"
        accept="video/*"
        onChange={(e) => setVideo(e.target.files?.[0] || null)}
      />

      <div>
        <label>Experience Level:</label>
        <select onChange={(e) => setExperienceLevel(e.target.value)}>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      <div>
        <label>Camera Angle:</label>
        <select onChange={(e) => setCameraAngle(e.target.value)}>
          <option value="down-the-line">Down the Line</option>
          <option value="face-on">Face On</option>
        </select>
      </div>

      <textarea
        placeholder="Describe shot outcome..."
        onChange={(e) => setMetadata(e.target.value)}
      />

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze Swing"}
      </button>

      {analysis && (
        <>
          <h2>Analysis</h2>
          <pre>{analysis}</pre>
        </>
      )}

      {videoUrl && (
        <>
          <h2>Pose Overlay</h2>
          <video
            src={videoUrl}
            controls
            muted
            playsInline
            width={500}
            
          />
        </>
      )}
    </main>
  );
}
