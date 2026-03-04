const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://127.0.0.1:5050';

app.use(cors());
app.use(express.json());

// Proxy route to ML Service
app.post('/api/chat', async (req, res) => {
    try {
        const response = await axios.post(`${ML_SERVICE_URL}/query`, req.body);
        res.json(response.data);
    } catch (error) {
        // Pass through the ML Service's response if it actually responded (e.g., 503 Service Unavailable)
        if (error.response) {
            console.error('ML Service Responded with Error:', error.response.status, error.response.data);
            return res.status(error.response.status).json(error.response.data);
        }

        // Generic fallback for actual connection failures (timeout, DNS, service down)
        res.json({
            response: "Connection Error: Could not reach the AI service. Please ensure the Python server is running in the Render dashboard.",
            source: "backend-fallback",
            error: error.message
        });
    }
});

app.get('/health', (req, res) => {
    res.json({ status: 'Backend is running' });
});

app.listen(PORT, () => {
    console.log(`Backend Server running on port ${PORT}`);
});
