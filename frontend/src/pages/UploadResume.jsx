import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { resumeAPI } from "../services/api";

function UploadResume() {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    validateAndSetFile(selectedFile);
  };

  const validateAndSetFile = (selectedFile) => {
    setError("");
    if (!selectedFile) return;

    const allowedTypes = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!allowedTypes.includes(selectedFile.type)) {
      setError("Please upload a PDF or Word document (.pdf, .doc, .docx)");
      return;
    }

    if (selectedFile.size > maxSize) {
      setError("File size must be less than 5MB");
      return;
    }

    setFile(selectedFile);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    validateAndSetFile(droppedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a resume file");
      return;
    }

    setUploading(true);
    setError("");

 try {
  const response = await resumeAPI.upload(file);

      // Store resume data in localStorage for immediate display
      const resumeData = {
        filename: file.name,
        uploadDate: new Date().toISOString(),
        resumeUrl: response.resumeUrl || response.resume_url
      };
      localStorage.setItem('resumeData', JSON.stringify(resumeData));

      setUploadSuccess(true);
      setFile(null);

      // Redirect to dashboard after success
      setTimeout(() => {
        navigate("/student-dashboard");
      }, 2000);
    } catch (err) {
      setError(err.message || "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setUploadSuccess(false);
    setError("");
  };

  return (
    <section className="upload-section">
      <div className="upload-container">
        <div className="upload-header">
          <h1>Upload Your Resume</h1>
          <p>Let our AI analyze your resume and find your perfect job matches</p>
        </div>

        {uploadSuccess ? (
          <div className="upload-success">
            <div className="success-icon">✓</div>
            <h2>Resume Uploaded Successfully!</h2>
            <p>Your resume is being processed by our AI engine</p>
            <p className="success-detail">We're analyzing your skills and finding matching opportunities...</p>
            <p className="redirect-message">Redirecting to jobs in a moment...</p>
          </div>
        ) : (
          <div className="upload-content">
            <div className="upload-card">
              {error && <div className="upload-error">{error}</div>}

              {/* DRAG & DROP AREA */}
              <div
                className={`drag-drop-area ${dragActive ? "active" : ""} ${
                  file ? "has-file" : ""
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => !file && fileInputRef.current?.click()}
                style={{ cursor: file ? 'default' : 'pointer' }}
              >
                {file ? (
                  <div className="file-selected">
                    <div className="file-icon">📄</div>
                    <p className="file-name">{file.name}</p>
                    <p className="file-size">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                    <div className="file-actions">
                      <button
                        type="button"
                        onClick={handleRemoveFile}
                        className="file-remove-btn"
                      >
                        Remove File
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="drag-drop-content">
                    <div className="upload-icon">📤</div>
                    <h3>Drag and drop your resume</h3>
                    <p>or click to browse your files</p>
                    <p className="supported-formats">
                      Supported: PDF, DOC, DOCX (Max 5MB)
                    </p>
                  </div>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                  className="file-input"
                  disabled={uploading}
                  style={{ display: 'none' }}
                />
              </div>

              {/* ACTION BUTTONS */}
              <div className="upload-actions">
                <button
                  onClick={handleUpload}
                  className="upload-btn"
                  disabled={!file || uploading}
                >
                  {uploading ? "Uploading..." : "Upload Resume"}
                </button>
              </div>

              {/* INFO CARDS */}
              <div className="upload-info">
                <div className="info-card">
                  <div className="info-icon">🤖</div>
                  <h4>AI Analysis</h4>
                  <p>Extracts skills, education, and experience</p>
                </div>
                <div className="info-card">
                  <div className="info-icon">🎯</div>
                  <h4>Smart Matching</h4>
                  <p>Get personalized job recommendations</p>
                </div>
                <div className="info-card">
                  <div className="info-icon">⚡</div>
                  <h4>Instant Results</h4>
                  <p>Start applying to matched jobs immediately</p>
                </div>
              </div>
            </div>

            {/* REQUIREMENTS SECTION */}
            <div className="upload-requirements">
              <h3>Resume Requirements</h3>
              <div className="requirements-list">
                <div className="requirement-item">
                  <span className="req-check">✓</span>
                  <p>PDF, Word (.doc or .docx) format</p>
                </div>
                <div className="requirement-item">
                  <span className="req-check">✓</span>
                  <p>File size should be under 5MB</p>
                </div>
                <div className="requirement-item">
                  <span className="req-check">✓</span>
                  <p>Include contact information</p>
                </div>
                <div className="requirement-item">
                  <span className="req-check">✓</span>
                  <p>List relevant skills and experience</p>
                </div>
                <div className="requirement-item">
                  <span className="req-check">✓</span>
                  <p>Education and certifications</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export default UploadResume;
