/**
 * Role-Based Access Control Middleware
 * Check user roles for protected routes
 */

/**
 * Check if user has required role(s)
 * @param {string|string[]} roles - Required role(s) (e.g., 'admin' or ['admin', 'employer'])
 */
const checkRole = (...roles) => {
  return (req, res, next) => {
    // Check if user is authenticated
    if (!req.user || !req.userRole) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required. Please login.'
      });
    }

    // Check if user has required role
    if (!roles.includes(req.userRole)) {
      return res.status(403).json({
        success: false,
        message: `Access denied. Required role: ${roles.join(' or ')}. Your role: ${req.userRole}`
      });
    }

    next();
  };
};

/**
 * Admin only access
 */
const adminOnly = checkRole('admin');

/**
 * Employer only access
 */
const employerOnly = checkRole('employer');

/**
 * Worker only access
 */
const workerOnly = checkRole('worker');

/**
 * Employer or Admin access
 */
const employerOrAdmin = checkRole('employer', 'admin');

/**
 * Worker or Admin access
 */
const workerOrAdmin = checkRole('worker', 'admin');

/**
 * Any authenticated user
 */
const anyAuthenticated = checkRole('worker', 'employer', 'admin');

/**
 * Check if user owns the resource
 * Useful for endpoints where users can only access their own data
 */
const checkOwnership = (resourceUserIdField = 'userId') => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required.'
      });
    }

    // Admin can access everything
    if (req.userRole === 'admin') {
      return next();
    }

    // Check if user owns the resource
    const resourceUserId = req.params[resourceUserIdField] || req.body[resourceUserIdField];
    
    if (resourceUserId && resourceUserId !== req.userId.toString()) {
      return res.status(403).json({
        success: false,
        message: 'Access denied. You can only access your own resources.'
      });
    }

    next();
  };
};

module.exports = {
  checkRole,
  adminOnly,
  employerOnly,
  workerOnly,
  employerOrAdmin,
  workerOrAdmin,
  anyAuthenticated,
  checkOwnership
};
