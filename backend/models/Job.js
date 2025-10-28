/**
 * Job Model
 */

const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
  jobId: {
    type: String,
    required: true,
    unique: true
  },
  title: {
    type: String,
    required: true,
    trim: true
  },
  company: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    required: true
  },
  skillsRequired: [{
    type: String,
    trim: true
  }],
  experienceRequired: {
    type: Number,
    default: 0
  },
  location: {
    type: String,
    required: true,
    trim: true
  },
  salaryMin: {
    type: Number
  },
  salaryMax: {
    type: Number
  },
  employmentType: {
    type: String,
    enum: ['full-time', 'part-time', 'contract', 'freelance'],
    default: 'full-time'
  },
  postedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  isActive: {
    type: Boolean,
    default: true
  },
  postedAt: {
    type: Date,
    default: Date.now
  },
  expiresAt: {
    type: Date
  }
});

module.exports = mongoose.model('Job', jobSchema);
