import React from 'react';

function ConfirmDeleteModal({ isOpen, onClose, onConfirm, itemName }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content confirm-delete-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <div className="confirm-delete-icon">⚠️</div>
        <h2 className="confirm-delete-title">Remove Resume?</h2>
        
        <p className="confirm-delete-message">
          This will permanently delete your resume <strong>"{itemName}"</strong>. 
          You won't be able to apply for jobs until you upload a new resume.
        </p>

        <div className="confirm-delete-actions">
          <button onClick={onClose} className="cancel-btn">
            Cancel
          </button>
          <button onClick={onConfirm} className="delete-btn">
            Delete Resume
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDeleteModal;
