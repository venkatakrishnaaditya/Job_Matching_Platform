import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { profileAPI } from '../services/api';
import BackButton from '../components/BackButton';
import '../styles.css';

function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const data = await profileAPI.getProfile();
      setProfile(data);
      setError('');
    } catch (err) {
      setError('Failed to load profile. Please try again.');
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
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

  if (error) {
    return (
      <section className="jobs-section">
        <div className="jobs-container">
          <div className="error-message">{error}</div>
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
        <div className="profile-header">
          <div className="profile-header-content">
            <div className="profile-photo-section">
              {profile.profilePhoto ? (
                <img 
                  src={profile.profilePhoto} 
                  alt="Profile" 
                  className="profile-photo-large"
                />
              ) : (
                <div className="profile-photo-placeholder">
                  <span className="profile-initials">
                    {profile.name?.charAt(0) || 'U'}
                  </span>
                </div>
              )}
            </div>
            
            <div className="profile-header-info">
              <h1>{profile.name}</h1>
              <p className="profile-role-badge">{profile.role}</p>
              <p className="profile-email">📧 {profile.email}</p>
              {profile.phone && <p className="profile-phone">📱 {profile.phone}</p>}
              
              <div className="profile-actions">
                <Link to="/edit-profile" className="apply-btn">Edit Profile</Link>
              </div>
            </div>
          </div>
        </div>

        <div className="profile-content">
          {/* CANDIDATE PROFILE */}
          {isCandidate && (
            <>
              {/* Bio Section */}
              {profile.bio && (
                <div className="profile-section">
                  <h2>About Me</h2>
                  <p className="profile-bio">{profile.bio}</p>
                </div>
              )}

              {/* Professional Details */}
              <div className="profile-section">
                <h2>Professional Details</h2>
                <div className="profile-details-grid">
                  {profile.location && (
                    <div className="profile-detail-item">
                      <span className="detail-label">Location:</span>
                      <span className="detail-value">{profile.location}</span>
                    </div>
                  )}
                  {profile.experienceLevel && (
                    <div className="profile-detail-item">
                      <span className="detail-label">Experience:</span>
                      <span className="detail-value">{profile.experienceLevel}</span>
                    </div>
                  )}
                  {profile.currentCompany && (
                    <div className="profile-detail-item">
                      <span className="detail-label">Current Company:</span>
                      <span className="detail-value">{profile.currentCompany}</span>
                    </div>
                  )}
                  {profile.currentRole && (
                    <div className="profile-detail-item">
                      <span className="detail-label">Current Role:</span>
                      <span className="detail-value">{profile.currentRole}</span>
                    </div>
                  )}
                </div>

                {/* Links */}
                <div className="profile-links">
                  {profile.linkedIn && (
                    <a href={profile.linkedIn} target="_blank" rel="noopener noreferrer" className="profile-link">
                      LinkedIn
                    </a>
                  )}
                  {profile.github && (
                    <a href={profile.github} target="_blank" rel="noopener noreferrer" className="profile-link">
                      GitHub
                    </a>
                  )}
                  {profile.portfolio && (
                    <a href={profile.portfolio} target="_blank" rel="noopener noreferrer" className="profile-link">
                      Portfolio
                    </a>
                  )}
                </div>
              </div>

              {/* Skills */}
              {profile.skills && profile.skills.length > 0 && (
                <div className="profile-section">
                  <h2>Skills</h2>
                  <div className="job-skills">
                    {profile.skills.map((skill, idx) => (
                      <span key={idx} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Education */}
              {profile.education && profile.education.length > 0 && (
                <div className="profile-section">
                  <h2>Education</h2>
                  {profile.education.map((edu, idx) => (
                    <div key={idx} className="profile-item-card">
                      <h3>{edu.degree}</h3>
                      <p className="profile-item-subtitle">{edu.institution}</p>
                      <p className="profile-item-meta">
                        {edu.field} • {edu.year}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Experience */}
              {profile.experience && profile.experience.length > 0 && (
                <div className="profile-section">
                  <h2>Experience</h2>
                  {profile.experience.map((exp, idx) => (
                    <div key={idx} className="profile-item-card">
                      <h3>{exp.role}</h3>
                      <p className="profile-item-subtitle">{exp.company}</p>
                      <p className="profile-item-meta">
                        {exp.from} - {exp.to}
                      </p>
                      {exp.description && (
                        <p className="profile-item-description">{exp.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {/* RECRUITER PROFILE */}
          {isRecruiter && (
            <>
              {/* Company Details */}
              <div className="profile-section">
                <h2>Company Information</h2>
                
                {profile.companyLogo && (
                  <div className="company-logo-container">
                    <img 
                      src={profile.companyLogo} 
                      alt="Company Logo" 
                      className="company-logo"
                    />
                  </div>
                )}

                <div className="profile-details-grid">
                  {profile.companyName && (
                    <div className="profile-detail-item">
                      <span className="detail-label">Company:</span>
                      <span className="detail-value">{profile.companyName}</span>
                    </div>
                  )}
                  {profile.companyIndustry && (
                    <div className="profile-detail-item">
                      <span className="detail-label">Industry:</span>
                      <span className="detail-value">{profile.companyIndustry}</span>
                    </div>
                  )}
                  {profile.companySize && (
                    <div className="profile-detail-item">
                      <span className="detail-label">Company Size:</span>
                      <span className="detail-value">{profile.companySize} employees</span>
                    </div>
                  )}
                  {profile.companyWebsite && (
                    <div className="profile-detail-item">
                      <span className="detail-label">Website:</span>
                      <a 
                        href={profile.companyWebsite} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="detail-link"
                      >
                        {profile.companyWebsite}
                      </a>
                    </div>
                  )}
                  {profile.companyLinkedIn && (
                    <div className="profile-detail-item">
                      <span className="detail-label">LinkedIn:</span>
                      <a 
                        href={profile.companyLinkedIn} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="detail-link"
                      >
                        Company Page
                      </a>
                    </div>
                  )}
                </div>

                {profile.companyDescription && (
                  <div className="profile-description">
                    <h3>About Company</h3>
                    <p>{profile.companyDescription}</p>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Member Since */}
          {profile.createdAt && (
            <div className="profile-section">
              <p className="profile-member-since">
                Member since {new Date(profile.createdAt).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long'
                })}
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default Profile;
