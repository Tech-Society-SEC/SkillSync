/**
 * Job Routes
 * CRUD operations for job postings
 */

const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const Job = require('../models/Job');
const { authenticate, optionalAuth } = require('../middleware/auth');
const { employerOrAdmin, adminOnly } = require('../middleware/roleCheck');

// @route   GET /api/jobs
// @desc    Get all jobs (with pagination & filters)
// @access  Public
router.get('/', async (req, res) => {
  try {
    const { page = 1, limit = 10, location, skills, employmentType, isActive = true } = req.query;

    // Build query
    const query = { isActive };
    if (location) query.location = new RegExp(location, 'i');
    if (skills) query.skillsRequired = { $in: skills.split(',') };
    if (employmentType) query.employmentType = employmentType;

    // Execute query with pagination
    const jobs = await Job.find(query)
      .populate('postedBy', 'name email')
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ postedAt: -1 });

    const count = await Job.countDocuments(query);

    res.json({
      success: true,
      data: jobs,
      totalPages: Math.ceil(count / limit),
      currentPage: page,
      total: count
    });
  } catch (error) {
    console.error('Get jobs error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   GET /api/jobs/:id
// @desc    Get job by ID or jobId
// @access  Public
router.get('/:id', async (req, res) => {
  try {
    const job = await Job.findOne({
      $or: [{ _id: req.params.id }, { jobId: req.params.id }]
    }).populate('postedBy', 'name email company');

    if (!job) {
      return res.status(404).json({ success: false, message: 'Job not found' });
    }

    res.json({ success: true, data: job });
  } catch (error) {
    console.error('Get job error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   POST /api/jobs
// @desc    Create new job posting
// @access  Private (Employer or Admin only)
router.post(
  '/',
  authenticate,
  employerOrAdmin,
  [
    body('title').trim().notEmpty().withMessage('Title is required'),
    body('company').trim().notEmpty().withMessage('Company is required'),
    body('description').trim().notEmpty().withMessage('Description is required'),
    body('location').trim().notEmpty().withMessage('Location is required'),
    body('skillsRequired').isArray().withMessage('Skills must be an array'),
    body('postedBy').notEmpty().withMessage('Posted by user ID is required')
  ],
  async (req, res) => {
    try {
      // Validate input
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ success: false, errors: errors.array() });
      }

      // Generate unique jobId
      const jobId = `JOB_${Date.now()}`;

      const job = new Job({
        jobId,
        ...req.body
      });

      await job.save();

      res.status(201).json({
        success: true,
        message: 'Job posted successfully',
        data: job
      });
    } catch (error) {
      console.error('Create job error:', error);
      res.status(500).json({ success: false, message: 'Server error', error: error.message });
    }
  }
);

// @route   PUT /api/jobs/:id
// @desc    Update job posting
// @access  Private (Employer or Admin only)
router.put('/:id', authenticate, employerOrAdmin, async (req, res) => {
  try {
    const { title, description, skillsRequired, location, salaryMin, salaryMax, isActive } = req.body;

    const job = await Job.findOneAndUpdate(
      { $or: [{ _id: req.params.id }, { jobId: req.params.id }] },
      {
        $set: {
          title,
          description,
          skillsRequired,
          location,
          salaryMin,
          salaryMax,
          isActive
        }
      },
      { new: true, runValidators: true }
    );

    if (!job) {
      return res.status(404).json({ success: false, message: 'Job not found' });
    }

    res.json({
      success: true,
      message: 'Job updated successfully',
      data: job
    });
  } catch (error) {
    console.error('Update job error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   DELETE /api/jobs/:id
// @desc    Delete job posting
// @access  Private (Admin only)
router.delete('/:id', authenticate, adminOnly, async (req, res) => {
  try {
    const job = await Job.findOneAndDelete({
      $or: [{ _id: req.params.id }, { jobId: req.params.id }]
    });

    if (!job) {
      return res.status(404).json({ success: false, message: 'Job not found' });
    }

    res.json({
      success: true,
      message: 'Job deleted successfully'
    });
  } catch (error) {
    console.error('Delete job error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   POST /api/jobs/:id/deactivate
// @desc    Deactivate job posting
// @access  Private (Employer or Admin only)
router.post('/:id/deactivate', authenticate, employerOrAdmin, async (req, res) => {
  try {
    const job = await Job.findOneAndUpdate(
      { $or: [{ _id: req.params.id }, { jobId: req.params.id }] },
      { $set: { isActive: false } },
      { new: true }
    );

    if (!job) {
      return res.status(404).json({ success: false, message: 'Job not found' });
    }

    res.json({
      success: true,
      message: 'Job deactivated successfully',
      data: job
    });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

module.exports = router;
