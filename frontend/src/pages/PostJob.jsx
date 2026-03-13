import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { jobAPI } from '../services/api';
import BackButton from '../components/BackButton';
import './PostJob.css';

function PostJob() {
  const navigate = useNavigate();
  const { jobId } = useParams(); // Get jobId from URL for edit mode
  const isEditMode = !!jobId;
  
  const [loading, setLoading] = useState(false);
  const [fetchingJob, setFetchingJob] = useState(isEditMode);
  const [error, setError] = useState('');
  const [skillInput, setSkillInput] = useState('');
  const [preferredSkillInput, setPreferredSkillInput] = useState('');
  
  // Auto-parse state
  const [parsing, setParsing] = useState(false);
  const parseTimeoutRef = useRef(null);

  const [formData, setFormData] = useState({
    title: '',
    company: '',
    numberOfOpenings: 1,
    jobType: 'Full-time',
    workplaceType: 'On-site',
    location: '',
    description: '',
    requiredSkills: [],
    minExperience: 0,
    maxExperience: 0,
    educationLevel: '',
    salaryMin: '',
    salaryMax: '',
    currency: 'INR',
    preferredSkills: [],
    applicationDeadline: '',
    jobLevel: '',
    department: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Auto-parse description on change (debounced)
    if (name === 'description' && value.length > 100) {
      // Clear existing timeout
      if (parseTimeoutRef.current) {
        clearTimeout(parseTimeoutRef.current);
      }
      
      // Set new timeout for parsing
      parseTimeoutRef.current = setTimeout(() => {
        parseDescription(value);
      }, 2000); // Parse 2 seconds after user stops typing
    }
  };

  const handleNumberChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseInt(value) || 0
    }));
  };

  // Handle skills as chips/tags
  const handleAddSkill = (e) => {
    if (e.key === 'Enter' && skillInput.trim()) {
      e.preventDefault();
      if (!formData.requiredSkills.includes(skillInput.trim())) {
        setFormData(prev => ({
          ...prev,
          requiredSkills: [...prev.requiredSkills, skillInput.trim()]
        }));
      }
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setFormData(prev => ({
      ...prev,
      requiredSkills: prev.requiredSkills.filter(skill => skill !== skillToRemove)
    }));
  };

  const handleAddPreferredSkill = (e) => {
    if (e.key === 'Enter' && preferredSkillInput.trim()) {
      e.preventDefault();
      if (!formData.preferredSkills.includes(preferredSkillInput.trim())) {
        setFormData(prev => ({
          ...prev,
          preferredSkills: [...prev.preferredSkills, preferredSkillInput.trim()]
        }));
      }
      setPreferredSkillInput('');
    }
  };

  const handleRemovePreferredSkill = (skillToRemove) => {
    setFormData(prev => ({
      ...prev,
      preferredSkills: prev.preferredSkills.filter(skill => skill !== skillToRemove)
    }));
  };

  // Parse job description function with direct pre-fill
  const parseDescription = async (description) => {
    if (!description || description.length < 100) return;
    
    try {
      setParsing(true);
      const response = await jobAPI.parseJobDescription(description);
      
      console.log('Parse API Response:', response);
      
      if (response.success && response.parsedData) {
        const parsed = response.parsedData;
        console.log('Parsed Data:', parsed);
        console.log('Education Level from parser:', parsed.educationLevel);
        console.log('Min Experience from parser:', parsed.minExperience);
        
        // Direct pre-fill: merge parsed data into form (recruiter can edit before submit)
        setFormData(prev => {
          const newData = {
            ...prev,
            // Merge skills (keep manually added + add parsed)
            requiredSkills: parsed.requiredSkills && parsed.requiredSkills.length > 0
              ? [...new Set([...prev.requiredSkills, ...parsed.requiredSkills])]
              : prev.requiredSkills,
            preferredSkills: parsed.optionalSkills && parsed.optionalSkills.length > 0
              ? [...new Set([...prev.preferredSkills, ...parsed.optionalSkills])]
              : prev.preferredSkills,
            // Only pre-fill if field is empty
            minExperience: prev.minExperience || parsed.minExperience || 0,
            educationLevel: prev.educationLevel || parsed.educationLevel || ''
          };
          console.log('New form data after merge:', newData);
          return newData;
        });
        
        // Show success message
        setError('');
        console.log('✅ Pre-filled requirements from description');
      }
    } catch (err) {
      console.error('Parsing error:', err);
      setError('Failed to parse job description');
    } finally {
      setParsing(false);
    }
  };

  // Handle paste event for instant parsing
  const handleDescriptionPaste = (e) => {
    const pastedText = e.clipboardData.getData('text');
    if (pastedText.length > 100) {
      // Parse immediately on paste
      setTimeout(() => {
        parseDescription(formData.description + pastedText);
      }, 100);
    }
  };

  // Fetch job data if in edit mode
  useEffect(() => {
    if (isEditMode && jobId) {
      const fetchJobData = async () => {
        try {
          setFetchingJob(true);
          const job = await jobAPI.getJobById(jobId);
          
          // Pre-fill form with existing job data
          setFormData({
            title: job.title || '',
            company: job.company || '',
            numberOfOpenings: job.numberOfOpenings || 1,
            jobType: job.jobType || 'Full-time',
            workplaceType: job.workplaceType || 'On-site',
            location: job.location || '',
            description: job.description || '',
            requiredSkills: job.requiredSkills || [],
            minExperience: job.minExperience || 0,
            maxExperience: job.maxExperience || 0,
            educationLevel: job.educationLevel || '',
            salaryMin: job.salaryMin || '',
            salaryMax: job.salaryMax || '',
            currency: job.currency || 'INR',
            preferredSkills: job.preferredSkills || [],
            applicationDeadline: job.applicationDeadline || '',
            jobLevel: job.jobLevel || '',
            department: job.department || ''
          });
        } catch (err) {
          setError('Failed to load job data. Please try again.');
          console.error('Error fetching job:', err);
        } finally {
          setFetchingJob(false);
        }
      };

      fetchJobData();
    }
  }, [isEditMode, jobId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (formData.requiredSkills.length === 0) {
      setError('Please add at least one required skill');
      return;
    }

    if (formData.maxExperience < formData.minExperience) {
      setError('Max experience must be greater than or equal to min experience');
      return;
    }

    if (formData.salaryMin && formData.salaryMax && parseInt(formData.salaryMax) < parseInt(formData.salaryMin)) {
      setError('Max salary must be greater than or equal to min salary');
      return;
    }

    setLoading(true);

    try {
      // Convert empty strings to null for optional fields
      const payload = {
        ...formData,
        salaryMin: formData.salaryMin ? parseInt(formData.salaryMin) : null,
        salaryMax: formData.salaryMax ? parseInt(formData.salaryMax) : null,
        applicationDeadline: formData.applicationDeadline || null,
        jobLevel: formData.jobLevel || null,
        department: formData.department || null
      };

      if (isEditMode) {
        await jobAPI.updateJob(jobId, payload);
        alert('Job updated successfully!');
      } else {
        await jobAPI.createJob(payload);
        alert('Job posted successfully!');
      }
      
      navigate('/recruiter-dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to ${isEditMode ? 'update' : 'post'} job. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="post-job-container">
      <div className="post-job-card">
        <BackButton />
        <h1>{isEditMode ? 'Edit Job Posting' : 'Post a New Job'}</h1>
        <p className="subtitle">
          {isEditMode ? 'Update the job posting details below' : 'Fill in the details below to create a job posting'}
        </p>

        {fetchingJob && <div className="loading-message">Loading job data...</div>}

        {error && <div className="error-message">{error}</div>}

        {!fetchingJob && (
          <form onSubmit={handleSubmit} className="post-job-form">
          
          {/* Section 1: Basic Information */}
          <div className="form-section">
            <h2>Basic Information</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="title">Job Title <span className="required">*</span></label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  placeholder="e.g., Senior Software Engineer"
                  required
                  minLength={3}
                  maxLength={200}
                />
              </div>

              <div className="form-group">
                <label htmlFor="company">Company Name <span className="required">*</span></label>
                <input
                  type="text"
                  id="company"
                  name="company"
                  value={formData.company}
                  onChange={handleChange}
                  placeholder="e.g., Tech Corp"
                  required
                  minLength={2}
                  maxLength={200}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="numberOfOpenings">Number of Openings <span className="required">*</span></label>
                <input
                  type="number"
                  id="numberOfOpenings"
                  name="numberOfOpenings"
                  value={formData.numberOfOpenings}
                  onChange={handleNumberChange}
                  min={1}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="jobType">Job Type <span className="required">*</span></label>
                <select
                  id="jobType"
                  name="jobType"
                  value={formData.jobType}
                  onChange={handleChange}
                  required
                >
                  <option value="Full-time">Full-time</option>
                  <option value="Part-time">Part-time</option>
                  <option value="Contract">Contract</option>
                  <option value="Internship">Internship</option>
                  <option value="Temporary">Temporary</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="workplaceType">Workplace Type <span className="required">*</span></label>
                <select
                  id="workplaceType"
                  name="workplaceType"
                  value={formData.workplaceType}
                  onChange={handleChange}
                  required
                >
                  <option value="On-site">On-site</option>
                  <option value="Remote">Remote</option>
                  <option value="Hybrid">Hybrid</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="location">Location <span className="required">*</span></label>
              <input
                type="text"
                id="location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., Bangalore, India"
                required
                minLength={2}
                maxLength={200}
              />
            </div>
          </div>

          {/* Section 2: Job Description */}
          <div className="form-section">
            <h2>Job Description</h2>
            
            <div className="form-group">
              <label htmlFor="description">Full Description <span className="required">*</span></label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                onPaste={handleDescriptionPaste}
                placeholder="Describe the role, responsibilities, and day-to-day tasks..."
                required
                minLength={50}
                rows={8}
              />
              <small className="char-count">{formData.description.length} characters (minimum 50)</small>
              
              {/* Parsing indicator */}
              {parsing && (
                <div className="parsing-indicator">
                  <span className="spinner">🔄</span>
                  <span>Extracting requirements from description...</span>
                </div>
              )}
            </div>
          </div>

          {/* Section 3: Requirements */}
          <div className="form-section">
            <h2>Requirements</h2>
            
            <div className="form-group">
              <label htmlFor="requiredSkills">Required Skills <span className="required">*</span></label>
              <div className="skills-input-wrapper">
                <input
                  type="text"
                  id="requiredSkills"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyDown={handleAddSkill}
                  placeholder="Type a skill and press Enter (e.g., Python, React, AWS)"
                />
                <small>Press Enter to add each skill</small>
              </div>
              <div className="skills-chips">
                {formData.requiredSkills.map((skill, index) => (
                  <span key={index} className="skill-chip">
                    {skill}
                    <button type="button" onClick={() => handleRemoveSkill(skill)}>×</button>
                  </span>
                ))}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="minExperience">Min Experience (years) <span className="required">*</span></label>
                <input
                  type="number"
                  id="minExperience"
                  name="minExperience"
                  value={formData.minExperience}
                  onChange={handleNumberChange}
                  min={0}
                  max={50}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="maxExperience">Max Experience (years) <span className="required">*</span></label>
                <input
                  type="number"
                  id="maxExperience"
                  name="maxExperience"
                  value={formData.maxExperience}
                  onChange={handleNumberChange}
                  min={0}
                  max={50}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="educationLevel">Education Level <span className="required">*</span></label>
              <select
  id="educationLevel"
  name="educationLevel"
  value={formData.educationLevel}
  onChange={handleChange}
  required
>
  <option value="">Select education level</option>
  <option value="Bachelor's Degree">Bachelor's Degree</option>
  <option value="Master's Degree">Master's Degree</option>
  <option value="PhD">PhD</option>
  <option value="Any Degree">Any Degree</option>
  <option value="Not Required">Not Required</option>
</select>
            </div>

            <div className="form-group">
              <label htmlFor="preferredSkills">Preferred Skills (Optional)</label>
              <div className="skills-input-wrapper">
                <input
                  type="text"
                  id="preferredSkills"
                  value={preferredSkillInput}
                  onChange={(e) => setPreferredSkillInput(e.target.value)}
                  onKeyDown={handleAddPreferredSkill}
                  placeholder="Type a skill and press Enter"
                />
                <small>Nice-to-have skills - Press Enter to add</small>
              </div>
              <div className="skills-chips">
                {formData.preferredSkills.map((skill, index) => (
                  <span key={index} className="skill-chip preferred">
                    {skill}
                    <button type="button" onClick={() => handleRemovePreferredSkill(skill)}>×</button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Section 4: Compensation & Additional Details */}
          <div className="form-section">
            <h2>Compensation & Additional Details</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="salaryMin">Min Salary (Optional)</label>
                <input
                  type="number"
                  id="salaryMin"
                  name="salaryMin"
                  value={formData.salaryMin}
                  onChange={handleChange}
                  placeholder="e.g., 500000"
                  min={0}
                />
              </div>

              <div className="form-group">
                <label htmlFor="salaryMax">Max Salary (Optional)</label>
                <input
                  type="number"
                  id="salaryMax"
                  name="salaryMax"
                  value={formData.salaryMax}
                  onChange={handleChange}
                  placeholder="e.g., 800000"
                  min={0}
                />
              </div>

              <div className="form-group">
                <label htmlFor="currency">Currency</label>
                <select
                  id="currency"
                  name="currency"
                  value={formData.currency}
                  onChange={handleChange}
                >
                  <option value="INR">INR</option>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="applicationDeadline">Application Deadline (Optional)</label>
                <input
                  type="date"
                  id="applicationDeadline"
                  name="applicationDeadline"
                  value={formData.applicationDeadline}
                  onChange={handleChange}
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>

              <div className="form-group">
                <label htmlFor="jobLevel">Job Level (Optional)</label>
                <select
                  id="jobLevel"
                  name="jobLevel"
                  value={formData.jobLevel}
                  onChange={handleChange}
                >
                  <option value="">Select level</option>
                  <option value="Entry Level">Entry Level</option>
                  <option value="Mid-Senior Level">Mid-Senior Level</option>
                  <option value="Senior Level">Senior Level</option>
                  <option value="Lead/Manager">Lead/Manager</option>
                  <option value="Executive">Executive</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="department">Department (Optional)</label>
                <input
                  type="text"
                  id="department"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  placeholder="e.g., Engineering, Marketing"
                  maxLength={100}
                />
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              onClick={() => navigate('/recruiter-dashboard')} 
              className="btn-cancel"
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn-submit"
              disabled={loading || fetchingJob}
            >
              {loading ? (isEditMode ? 'Updating Job...' : 'Posting Job...') : (isEditMode ? 'Update Job' : 'Post Job')}
            </button>
          </div>
        </form>
        )}
      </div>
    </div>
  );
}

export default PostJob;
