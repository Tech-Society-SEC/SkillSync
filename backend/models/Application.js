/**
 * Job Application Model
 */

const mongoose = require('mongoose');

const applicationSchema = new mongoose.Schema({
  workerId: {
    type: String,
    required: true,
    ref: 'Worker'
  },
  jobId: {
    type: String,
    required: true,
    ref: 'Job'
  },
  jobTitle: {
    type: String,
    required: true
  },
  matchScore: {
    type: Number,
    default: 0
  },
  status: {
    type: String,
    enum: ['pending', 'reviewed', 'shortlisted', 'contacted', 'hired', 'rejected'],
    default: 'pending'
  },
  notes: {
    type: String
  },
  appliedAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Update timestamp on save
applicationSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('Application', applicationSchema);
