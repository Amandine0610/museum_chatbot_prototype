import express from 'express';
import axios from 'axios';

const router = express.Router();

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

/**
 * GET /api/health
 * Health check endpoint
 */
router.get('/', async (req, res) => {
  try {
    // Check ML service health
    let mlStatus = 'unknown';
    try {
      const mlHealth = await axios.get(`${ML_SERVICE_URL}/health`, {
        timeout: 5000
      });
      mlStatus = mlHealth.data.status === 'ok' ? 'healthy' : 'unhealthy';
    } catch (e) {
      mlStatus = 'unreachable';
    }

    res.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      services: {
        backend: 'healthy',
        ml_service: mlStatus
      }
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: error.message
    });
  }
});

export default router;