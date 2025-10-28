/**
 * SkillSync Backend Server
 * Node.js + Express + MongoDB Atlas
 */

const express = require('express');
const cors = require('cors');
const connectDB = require('./config/db');
require('dotenv').config({ path: '../.env' });

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Connect to MongoDB
connectDB();

// Basic route
app.get('/', (req, res) => {
  res.json({
    message: 'SkillSync Backend API',
    version: '1.0.0',
    status: 'running'
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    database: 'connected',
    timestamp: new Date()
  });
});

// API Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/workers', require('./routes/workers'));
app.use('/api/jobs', require('./routes/jobs'));
app.use('/api/applications', require('./routes/applications'));
app.use('/api/analytics', require('./routes/analytics'));

const PORT = process.env.PORT || 5000;

console.log(`[DEBUG] PORT from .env: ${process.env.PORT}`);
console.log(`[DEBUG] Using PORT: ${PORT}`);

app.listen(PORT, () => {
  console.log('\n' + '='.repeat(70));
  console.log(`[SERVER] SkillSync Backend running on port ${PORT}`);
  console.log(`[URL] http://localhost:${PORT}`);
  console.log('='.repeat(70) + '\n');
});
