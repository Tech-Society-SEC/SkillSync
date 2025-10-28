/**
 * MongoDB Atlas Database Configuration
 */
const mongoose = require('mongoose');
require('dotenv').config({ path: '../.env' });

const connectDB = async () => {
  try {
    console.log('[CONNECTING] MongoDB Atlas...');
    
    // Remove deprecated options - Mongoose 6+ handles these automatically
    const conn = await mongoose.connect(process.env.MONGO_URI);

    console.log(`[OK] MongoDB Connected: ${conn.connection.host}`);
    console.log(`  Database: ${conn.connection.name}`);
    
    return conn;
  } catch (error) {
    console.error(`[ERROR] MongoDB Connection Failed: ${error.message}`);
    console.error('[INFO] Check your internet connection and MongoDB Atlas settings');
    process.exit(1);
  }
};
module.exports = connectDB;