/**
 * Worker Profile Model
 */

const mongoose = require('mongoose');

const workerSchema = new mongoose.Schema({
  workerId: {
    type: String,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  phone: {
    type: String,
    required: true,
    trim: true
  },
  email: {
    type: String,
    lowercase: true,
    trim: true
  },
  language: {
    type: String,
    default: 'en'
  },
  jobTitle: {
    type: String,
    trim: true
  },
  experienceYears: {
    type: Number,
    default: 0
  },
  skills: [{
    type: String,
    trim: true
  }],
  location: {
    type: String,
    trim: true
  },
  audioFilePath: {
    type: String
  },
  transcription: {
    type: String
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Update timestamp on save
workerSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('Worker', workerSchema);
