"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import NeonButton from "./NeonButton";

const FORMATS = [
  { slug: "tailwind", label: "Tailwind CSS", desc: "React + utility classes" },
  { slug: "mui", label: "MUI", desc: "Material UI + React" },
  { slug: "html", label: "HTML/CSS/JS", desc: "Single file, no deps" },
];

const MAX_SIZE = 10 * 1024 * 1024; // 10 MB
const ACCEPTED_TYPES = ["image/png", "image/jpeg", "image/webp"];

export default function DesignUploadForm({ onSubmit, loading }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [outputFormat, setOutputFormat] = useState("tailwind");
  const [additionalInstructions, setAdditionalInstructions] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [fileError, setFileError] = useState("");
  const inputRef = useRef(null);

  // Create / revoke preview URL
  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const validateAndSet = useCallback((f) => {
    setFileError("");
    if (!ACCEPTED_TYPES.includes(f.type)) {
      setFileError("Unsupported format. Please use PNG, JPG, or WEBP.");
      return;
    }
    if (f.size > MAX_SIZE) {
      setFileError("Image must be under 10 MB.");
      return;
    }
    setFile(f);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragActive(false);
      const f = e.dataTransfer.files?.[0];
      if (f) validateAndSet(f);
    },
    [validateAndSet]
  );

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
  }, []);

  const handleFileChange = useCallback(
    (e) => {
      const f = e.target.files?.[0];
      if (f) validateAndSet(f);
    },
    [validateAndSet]
  );

  const removeFile = useCallback(() => {
    setFile(null);
    setFileError("");
    if (inputRef.current) inputRef.current.value = "";
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) {
      setFileError("Please upload a design image.");
      return;
    }
    onSubmit({ file, outputFormat, additionalInstructions });
  };

  return (
    <motion.div
      className="panel"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
    >
      <form onSubmit={handleSubmit}>
        {/* Upload zone */}
        <label className="form-label">Design image</label>
        <div
          className={`upload-zone ${dragActive ? "upload-zone--active" : ""} ${file ? "upload-zone--has-file" : ""}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !file && inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />

          {preview ? (
            <div className="upload-preview">
              <img src={preview} alt="Design preview" />
              <button
                type="button"
                className="upload-remove-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile();
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          ) : (
            <div className="upload-placeholder">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.5 }}>
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
              <p className="upload-text">
                Drag & drop a screenshot or{" "}
                <span className="upload-link">browse</span>
              </p>
              <p className="upload-hint">PNG, JPG, or WEBP — max 10 MB</p>
            </div>
          )}
        </div>
        {fileError && <p className="field-error">{fileError}</p>}

        {/* Format selector */}
        <label className="form-label" style={{ marginTop: 16 }}>
          Output format
        </label>
        <div className="tool-selector">
          {FORMATS.map((f) => (
            <button
              key={f.slug}
              type="button"
              className={`tool-card ${outputFormat === f.slug ? "tool-card--active" : ""}`}
              onClick={() => setOutputFormat(f.slug)}
            >
              <span className="tool-card-label">{f.label}</span>
              <span className="tool-card-desc">{f.desc}</span>
            </button>
          ))}
        </div>

        {/* Additional instructions */}
        <label className="form-label" style={{ marginTop: 16 }}>
          Additional instructions{" "}
          <span style={{ opacity: 0.5, fontWeight: 400 }}>(optional)</span>
        </label>
        <textarea
          className="idea-input"
          style={{ minHeight: 60 }}
          value={additionalInstructions}
          onChange={(e) => setAdditionalInstructions(e.target.value)}
          placeholder="e.g. Use a dark theme, make the sidebar collapsible, add hover effects..."
          maxLength={1000}
        />

        {/* Submit */}
        <div className="row" style={{ marginTop: 10 }}>
          <NeonButton type="submit" disabled={loading || !file}>
            {loading ? "Generating..." : "Generate Code"}
          </NeonButton>
        </div>
      </form>
    </motion.div>
  );
}
