/**
 * Learning Resource Model
 */

const mongoose = require('mongoose');

const learningResourceSchema = new mongoose.Schema({
  resourceId: {
    type: String,
    required: true,
    unique: true
  },
  title: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String
  },
  url: {
    type: String,
    required: true
  },
  resourceType: {
    type: String,
    enum: ['video', 'article', 'course', 'tutorial'],
    default: 'video'
  },
  skills: [{
    type: String,
    trim: true
  }],
  language: {
    type: String,
    default: 'en'
  },
  durationMinutes: {
    type: Number
  },
  difficultyLevel: {
    type: String,
    enum: ['beginner', 'intermediate', 'advanced'],
    default: 'beginner'
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('LearningResource', learningResourceSchema);
