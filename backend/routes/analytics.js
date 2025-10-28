/**
 * Analytics Routes
 * Track events and get analytics data
 */

const express = require('express');
const router = express.Router();
const Analytics = require('../models/Analytics');
const Worker = require('../models/Worker');
const Job = require('../models/Job');
const Application = require('../models/Application');

// @route   POST /api/analytics/event
// @desc    Log an analytics event
// @access  Public
router.post('/event', async (req, res) => {
  try {
    const { workerId, userId, eventType, eventData } = req.body;

    const event = new Analytics({
      workerId,
      userId,
      eventType,
      eventData: eventData || {}
    });

    await event.save();

    res.status(201).json({
      success: true,
      message: 'Event logged successfully',
      data: event
    });
  } catch (error) {
    console.error('Log event error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   GET /api/analytics/dashboard
// @desc    Get dashboard statistics
// @access  Public
router.get('/dashboard', async (req, res) => {
  try {
    const [
      totalWorkers,
      totalJobs,
      totalApplications,
      activeJobs,
      recentWorkers,
      topSkills
    ] = await Promise.all([
      Worker.countDocuments(),
      Job.countDocuments(),
      Application.countDocuments(),
      Job.countDocuments({ isActive: true }),
      Worker.find().sort({ createdAt: -1 }).limit(5).select('name jobTitle createdAt'),
      Worker.aggregate([
        { $unwind: '$skills' },
        { $group: { _id: '$skills', count: { $sum: 1 } } },
        { $sort: { count: -1 } },
        { $limit: 10 }
      ])
    ]);

    res.json({
      success: true,
      data: {
        totalWorkers,
        totalJobs,
        totalApplications,
        activeJobs,
        recentWorkers,
        topSkills: topSkills.map(s => ({ skill: s._id, count: s.count }))
      }
    });
  } catch (error) {
    console.error('Dashboard error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   GET /api/analytics/worker/:workerId
// @desc    Get analytics for a specific worker
// @access  Public
router.get('/worker/:workerId', async (req, res) => {
  try {
    const events = await Analytics.find({ workerId: req.params.workerId })
      .sort({ timestamp: -1 })
      .limit(50);

    const eventsByType = await Analytics.aggregate([
      { $match: { workerId: req.params.workerId } },
      { $group: { _id: '$eventType', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);

    res.json({
      success: true,
      data: {
        events,
        eventsByType: eventsByType.map(e => ({ type: e._id, count: e.count }))
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

module.exports = router;
