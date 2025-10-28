/**
 * Application Routes
 * CRUD operations for job applications
 */

const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const Application = require('../models/Application');
const Worker = require('../models/Worker');
const Job = require('../models/Job');
const { authenticate } = require('../middleware/auth');
const { employerOrAdmin, workerOrAdmin } = require('../middleware/roleCheck');

// @route   GET /api/applications
// @desc    Get all applications (with filters)
// @access  Public
router.get('/', async (req, res) => {
  try {
    const { workerId, jobId, status, page = 1, limit = 10 } = req.query;

    // Build query
    const query = {};
    if (workerId) query.workerId = workerId;
    if (jobId) query.jobId = jobId;
    if (status) query.status = status;

    // Execute query with pagination
    const applications = await Application.find(query)
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ appliedAt: -1 });

    const count = await Application.countDocuments(query);

    res.json({
      success: true,
      data: applications,
      totalPages: Math.ceil(count / limit),
      currentPage: page,
      total: count
    });
  } catch (error) {
    console.error('Get applications error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   GET /api/applications/:id
// @desc    Get application by ID
// @access  Public
router.get('/:id', async (req, res) => {
  try {
    const application = await Application.findById(req.params.id);

    if (!application) {
      return res.status(404).json({ success: false, message: 'Application not found' });
    }

    // Populate worker and job details
    const worker = await Worker.findOne({ workerId: application.workerId });
    const job = await Job.findOne({ jobId: application.jobId });

    res.json({
      success: true,
      data: {
        ...application.toObject(),
        worker,
        job
      }
    });
  } catch (error) {
    console.error('Get application error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   POST /api/applications
// @desc    Create new job application
// @access  Public
router.post(
  '/',
  [
    body('workerId').notEmpty().withMessage('Worker ID is required'),
    body('jobId').notEmpty().withMessage('Job ID is required'),
    body('jobTitle').notEmpty().withMessage('Job title is required')
  ],
  async (req, res) => {
    try {
      // Validate input
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ success: false, errors: errors.array() });
      }

      const { workerId, jobId, jobTitle, matchScore } = req.body;

      // Check if application already exists
      const existingApplication = await Application.findOne({ workerId, jobId });
      if (existingApplication) {
        return res.status(400).json({
          success: false,
          message: 'Application already exists for this job'
        });
      }

      // Verify worker and job exist
      const worker = await Worker.findOne({ workerId });
      const job = await Job.findOne({ jobId });

      if (!worker) {
        return res.status(404).json({ success: false, message: 'Worker not found' });
      }
      if (!job) {
        return res.status(404).json({ success: false, message: 'Job not found' });
      }

      const application = new Application({
        workerId,
        jobId,
        jobTitle,
        matchScore: matchScore || 0
      });

      await application.save();

      res.status(201).json({
        success: true,
        message: 'Application submitted successfully',
        data: application
      });
    } catch (error) {
      console.error('Create application error:', error);
      res.status(500).json({ success: false, message: 'Server error', error: error.message });
    }
  }
);

// @route   PUT /api/applications/:id
// @desc    Update application status
// @access  Public (should be protected - employer only)
router.put('/:id', async (req, res) => {
  try {
    const { status, notes } = req.body;

    const application = await Application.findByIdAndUpdate(
      req.params.id,
      {
        $set: {
          status,
          notes,
          updatedAt: Date.now()
        }
      },
      { new: true, runValidators: true }
    );

    if (!application) {
      return res.status(404).json({ success: false, message: 'Application not found' });
    }

    res.json({
      success: true,
      message: 'Application updated successfully',
      data: application
    });
  } catch (error) {
    console.error('Update application error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   DELETE /api/applications/:id
// @desc    Delete application
// @access  Public
router.delete('/:id', async (req, res) => {
  try {
    const application = await Application.findByIdAndDelete(req.params.id);

    if (!application) {
      return res.status(404).json({ success: false, message: 'Application not found' });
    }

    res.json({
      success: true,
      message: 'Application deleted successfully'
    });
  } catch (error) {
    console.error('Delete application error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   GET /api/applications/worker/:workerId
// @desc    Get all applications for a worker
// @access  Public
router.get('/worker/:workerId', async (req, res) => {
  try {
    const applications = await Application.find({ workerId: req.params.workerId })
      .sort({ appliedAt: -1 });

    res.json({
      success: true,
      count: applications.length,
      data: applications
    });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   GET /api/applications/job/:jobId
// @desc    Get all applications for a job
// @access  Public (should be protected - employer only)
router.get('/job/:jobId', async (req, res) => {
  try {
    const applications = await Application.find({ jobId: req.params.jobId })
      .sort({ matchScore: -1, appliedAt: -1 });

    res.json({
      success: true,
      count: applications.length,
      data: applications
    });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

module.exports = router;
