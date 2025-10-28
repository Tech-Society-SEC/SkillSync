/**
 * Worker Routes
 * CRUD operations for worker profiles
 */

const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const Worker = require('../models/Worker');

// @route   GET /api/workers
// @desc    Get all workers (with pagination & filters)
// @access  Public
router.get('/', async (req, res) => {
  try {
    const { page = 1, limit = 10, skills, location, search } = req.query;

    // Build query
    const query = {};
    if (skills) query.skills = { $in: skills.split(',') };
    if (location) query.location = new RegExp(location, 'i');
    if (search) {
      query.$or = [
        { name: new RegExp(search, 'i') },
        { jobTitle: new RegExp(search, 'i') }
      ];
    }

    // Execute query with pagination
    const workers = await Worker.find(query)
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ createdAt: -1 });

    const count = await Worker.countDocuments(query);

    res.json({
      success: true,
      data: workers,
      totalPages: Math.ceil(count / limit),
      currentPage: page,
      total: count
    });
  } catch (error) {
    console.error('Get workers error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   GET /api/workers/:id
// @desc    Get worker by ID or workerId
// @access  Public
router.get('/:id', async (req, res) => {
  try {
    const worker = await Worker.findOne({
      $or: [{ _id: req.params.id }, { workerId: req.params.id }]
    });

    if (!worker) {
      return res.status(404).json({ success: false, message: 'Worker not found' });
    }

    res.json({ success: true, data: worker });
  } catch (error) {
    console.error('Get worker error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   POST /api/workers
// @desc    Create new worker profile
// @access  Public
router.post(
  '/',
  [
    body('name').trim().notEmpty().withMessage('Name is required'),
    body('phone').trim().notEmpty().withMessage('Phone is required'),
    body('email').optional().isEmail().withMessage('Valid email required'),
    body('skills').optional().isArray().withMessage('Skills must be an array')
  ],
  async (req, res) => {
    try {
      // Validate input
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ success: false, errors: errors.array() });
      }

      // Generate unique workerId
      const workerId = `WKR_${Date.now()}`;

      const worker = new Worker({
        workerId,
        ...req.body
      });

      await worker.save();

      res.status(201).json({
        success: true,
        message: 'Worker profile created successfully',
        data: worker
      });
    } catch (error) {
      console.error('Create worker error:', error);
      res.status(500).json({ success: false, message: 'Server error', error: error.message });
    }
  }
);

// @route   PUT /api/workers/:id
// @desc    Update worker profile
// @access  Public
router.put('/:id', async (req, res) => {
  try {
    const { name, phone, email, jobTitle, experienceYears, skills, location } = req.body;

    const worker = await Worker.findOneAndUpdate(
      { $or: [{ _id: req.params.id }, { workerId: req.params.id }] },
      {
        $set: {
          name,
          phone,
          email,
          jobTitle,
          experienceYears,
          skills,
          location,
          updatedAt: Date.now()
        }
      },
      { new: true, runValidators: true }
    );

    if (!worker) {
      return res.status(404).json({ success: false, message: 'Worker not found' });
    }

    res.json({
      success: true,
      message: 'Worker profile updated successfully',
      data: worker
    });
  } catch (error) {
    console.error('Update worker error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   DELETE /api/workers/:id
// @desc    Delete worker profile
// @access  Public
router.delete('/:id', async (req, res) => {
  try {
    const worker = await Worker.findOneAndDelete({
      $or: [{ _id: req.params.id }, { workerId: req.params.id }]
    });

    if (!worker) {
      return res.status(404).json({ success: false, message: 'Worker not found' });
    }

    res.json({
      success: true,
      message: 'Worker profile deleted successfully'
    });
  } catch (error) {
    console.error('Delete worker error:', error);
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

// @route   GET /api/workers/:id/skills
// @desc    Get worker skills
// @access  Public
router.get('/:id/skills', async (req, res) => {
  try {
    const worker = await Worker.findOne({
      $or: [{ _id: req.params.id }, { workerId: req.params.id }]
    }).select('skills');

    if (!worker) {
      return res.status(404).json({ success: false, message: 'Worker not found' });
    }

    res.json({ success: true, skills: worker.skills });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Server error', error: error.message });
  }
});

module.exports = router;
