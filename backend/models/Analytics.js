/**
 * Analytics Event Model
 */

const mongoose = require('mongoose');

const analyticsSchema = new mongoose.Schema({
  workerId: {
    type: String,
    ref: 'Worker'
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  eventType: {
    type: String,
    required: true,
    trim: true
  },
  eventData: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

// Index for faster queries
analyticsSchema.index({ workerId: 1, eventType: 1, timestamp: -1 });

module.exports = mongoose.model('Analytics', analyticsSchema);
