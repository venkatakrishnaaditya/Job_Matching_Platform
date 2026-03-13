import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { profileAPI } from '../services/api';
import BackButton from '../components/BackButton';
import '../styles.css';

function EditProfile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [uploadingPhoto, setUploadingPhoto] = useState(false);

  // Form state - will be populated based on role
  const [formData, setFormData] = useState({});
  const [removingPhoto, setRemovingPhoto] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const data = await profileAPI.getProfile();
      setProfile(data);
      setFormData(data); // Initialize form with current data
      setError('');
    } catch (err) {
      setError('Failed to load profile');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSkillsChange = (e) => {
    const skillsArray = e.target.value.split(',').map(s => s.trim()).filter(s => s);
    setFormData(prev => ({
      ...prev,
      skills: skillsArray
    }));
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    try {
      setUploadingPhoto(true);
      const response = await profileAPI.uploadPhoto(file);
      setFormData(prev => ({
        ...prev,
        profilePhoto: response.photoUrl
      }));
      alert('Photo uploaded successfully!');
    } catch (err) {
      alert('Failed to upload photo');
      console.error('Error:', err);
    } finally {
      setUploadingPhoto(false);
    }
  };

  const handleLogoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    try {
      setUploadingPhoto(true);
      const response = await profileAPI.uploadCompanyLogo(file);
      setFormData(prev => ({
        ...prev,
        companyLogo: response.logoUrl
      }));
      alert('Logo uploaded successfully!');
    } catch (err) {
      alert('Failed to upload logo');
      console.error('Error:', err);
    } finally {
      setUploadingPhoto(false);
    }
  };

  const handleRemovePhoto = async () => {
    if (!window.confirm('Are you sure you want to remove your profile photo?')) {
      return;
    }

    try {
      setRemovingPhoto(true);
      await profileAPI.removePhoto();
      setFormData(prev => ({
        ...prev,
        profilePhoto: null
      }));
      alert('Profile photo removed successfully!');
    } catch (err) {
      alert('Failed to remove photo');
      console.error('Error:', err);
    } finally {
      setRemovingPhoto(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setSubmitting(true);
      setError('');

      // Build update payload based on role
      const updateData = { ...formData };
      delete updateData.userId;
      delete updateData.role;
      delete updateData.createdAt;
      delete updateData.profilePhoto;
      delete updateData.companyLogo;

      await profileAPI.updateProfile(updateData);
      alert('Profile updated successfully!');
      navigate('/profile');
    } catch (err) {
      setError(err.message || 'Failed to update profile');
      console.error('Error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <section className="jobs-section">
        <div className="jobs-container">
          <div className="loading-message">Loading profile...</div>
        </div>
      </section>
    );
  }

  if (!profile) return null;

  const isCandidate = profile.role === 'CANDIDATE';
  const isRecruiter = profile.role === 'RECRUITER';

  return (
    <section className="jobs-section">
      <div className="jobs-container">
        <BackButton />
        <div className="jobs-header">
          <h1>Edit Profile</h1>
          <p>Update your profile information</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="profile-edit-container">
          <form onSubmit={handleSubmit} className="profile-edit-form">
            
            {/* Photo Upload Section */}
            <div className="profile-photo-upload-section">
              <div className="profile-photo-preview-container">
                <div className="profile-photo-preview">
                  {formData.profilePhoto ? (
                    <>
                      <img src={formData.profilePhoto} alt="Profile" className="profile-photo-large" />
                      <button
                        type="button"
                        className="remove-photo-btn"
                        onClick={handleRemovePhoto}
                        disabled={removingPhoto}
                        title="Remove photo"
                      >
                        ✕
                      </button>
                    </>
                  ) : (
                    <div className="profile-photo-placeholder">
                      <span className="profile-initials">
                        {formData.name?.charAt(0) || 'U'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <div className="photo-upload-controls">
                <label className="photo-upload-btn">
                  {uploadingPhoto ? 'Uploading...' : 'Upload Photo'}
                  <input
                    type="file"
                    accept="image/jpeg,image/jpg,image/png,image/webp"
                    onChange={handlePhotoUpload}
                    disabled={uploadingPhoto}
                    style={{ display: 'none' }}
                  />
                </label>
                <p className="photo-upload-hint">Max size: 5MB (JPEG, PNG, WebP)</p>
              </div>
            </div>

            {/* Basic Info - Common for both roles */}
            <div className="form-section">
              <h2>Basic Information</h2>
              
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name || ''}
                  onChange={handleChange}
                  required
                  minLength={2}
                  maxLength={100}
                />
              </div>

              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email || ''}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone || ''}
                  onChange={handleChange}
                  placeholder="+1234567890"
                />
              </div>
            </div>

            {/* CANDIDATE-SPECIFIC FIELDS */}
            {isCandidate && (
              <>
                <div className="form-section">
                  <h2>Professional Details</h2>
                  
                  <div className="form-group">
                    <label>Bio</label>
                    <textarea
                      name="bio"
                      value={formData.bio || ''}
                      onChange={handleChange}
                      rows={4}
                      maxLength={500}
                      placeholder="Tell us about yourself..."
                    />
                  </div>

                  <div className="form-group">
                    <label>Location</label>
                    <input
                      type="text"
                      name="location"
                      value={formData.location || ''}
                      onChange={handleChange}
                      placeholder="City, Country"
                    />
                  </div>

                  <div className="form-group">
                    <label>Experience Level</label>
                    <select
                      name="experienceLevel"
                      value={formData.experienceLevel || ''}
                      onChange={handleChange}
                    >
                      <option value="">Select experience level</option>
                      <option value="Fresher">Fresher</option>
                      <option value="0-1 years">0-1 years</option>
                      <option value="1-3 years">1-3 years</option>
                      <option value="3-5 years">3-5 years</option>
                      <option value="5-10 years">5-10 years</option>
                      <option value="10+ years">10+ years</option>
                    </select>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Current Company</label>
                      <input
                        type="text"
                        name="currentCompany"
                        value={formData.currentCompany || ''}
                        onChange={handleChange}
                      />
                    </div>

                    <div className="form-group">
                      <label>Current Role</label>
                      <input
                        type="text"
                        name="currentRole"
                        value={formData.currentRole || ''}
                        onChange={handleChange}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Skills (comma-separated)</label>
                    <input
                      type="text"
                      name="skills"
                      value={formData.skills?.join(', ') || ''}
                      onChange={handleSkillsChange}
                      placeholder="JavaScript, React, Node.js, MongoDB"
                    />
                  </div>
                </div>

                <div className="form-section">
                  <h2>Links</h2>
                  
                  <div className="form-group">
                    <label>LinkedIn</label>
                    <input
                      type="url"
                      name="linkedIn"
                      value={formData.linkedIn || ''}
                      onChange={handleChange}
                      placeholder="https://linkedin.com/in/yourprofile"
                    />
                  </div>

                  <div className="form-group">
                    <label>GitHub</label>
                    <input
                      type="url"
                      name="github"
                      value={formData.github || ''}
                      onChange={handleChange}
                      placeholder="https://github.com/yourusername"
                    />
                  </div>

                  <div className="form-group">
                    <label>Portfolio</label>
                    <input
                      type="url"
                      name="portfolio"
                      value={formData.portfolio || ''}
                      onChange={handleChange}
                      placeholder="https://yourportfolio.com"
                    />
                  </div>
                </div>
              </>
            )}

            {/* RECRUITER-SPECIFIC FIELDS */}
            {isRecruiter && (
              <>
                {/* Company Logo Upload */}
                <div className="form-section">
                  <h2>Company Logo</h2>
                  <div className="profile-photo-upload-section">
                    {formData.companyLogo && (
                      <div className="company-logo-preview">
                        <img src={formData.companyLogo} alt="Company Logo" className="company-logo" />
                      </div>
                    )}
                    <div className="photo-upload-controls">
                      <label className="photo-upload-btn">
                        {uploadingPhoto ? 'Uploading...' : 'Upload Logo'}
                        <input
                          type="file"
                          accept="image/jpeg,image/jpg,image/png,image/webp"
                          onChange={handleLogoUpload}
                          disabled={uploadingPhoto}
                          style={{ display: 'none' }}
                        />
                      </label>
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h2>Company Information</h2>
                  
                  <div className="form-group">
                    <label>Company Name</label>
                    <input
                      type="text"
                      name="companyName"
                      value={formData.companyName || ''}
                      onChange={handleChange}
                      maxLength={200}
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Industry</label>
                      <input
                        type="text"
                        name="companyIndustry"
                        value={formData.companyIndustry || ''}
                        onChange={handleChange}
                        placeholder="IT, Finance, Healthcare..."
                      />
                    </div>

                    <div className="form-group">
                      <label>Company Size</label>
                      <select
                        name="companySize"
                        value={formData.companySize || ''}
                        onChange={handleChange}
                      >
                        <option value="">Select size</option>
                        <option value="1-10">1-10 employees</option>
                        <option value="10-50">10-50 employees</option>
                        <option value="50-200">50-200 employees</option>
                        <option value="200-500">200-500 employees</option>
                        <option value="500-1000">500-1000 employees</option>
                        <option value="1000+">1000+ employees</option>
                      </select>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Company Website</label>
                    <input
                      type="url"
                      name="companyWebsite"
                      value={formData.companyWebsite || ''}
                      onChange={handleChange}
                      placeholder="https://company.com"
                    />
                  </div>

                  <div className="form-group">
                    <label>Company LinkedIn</label>
                    <input
                      type="url"
                      name="companyLinkedIn"
                      value={formData.companyLinkedIn || ''}
                      onChange={handleChange}
                      placeholder="https://linkedin.com/company/yourcompany"
                    />
                  </div>

                  <div className="form-group">
                    <label>Company Description</label>
                    <textarea
                      name="companyDescription"
                      value={formData.companyDescription || ''}
                      onChange={handleChange}
                      rows={5}
                      maxLength={1000}
                      placeholder="Tell us about your company..."
                    />
                  </div>
                </div>
              </>
            )}

            {/* Submit Buttons */}
            <div className="form-actions">
              <button 
                type="button" 
                className="save-btn"
                onClick={() => navigate('/profile')}
                disabled={submitting}
              >
                Cancel
              </button>
              <button 
                type="submit" 
                className="apply-btn"
                disabled={submitting}
              >
                {submitting ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}

export default EditProfile;
