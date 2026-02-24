const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:5000';

app.use(cors());
app.use(express.json());

// Proxy route to ML Service
app.post('/api/chat', async (req, res) => {
    try {
        const response = await axios.post(`${ML_SERVICE_URL}/query`, req.body);
        res.json(response.data);
    } catch (error) {
        console.error('Error connecting to ML Service:', error.message);
        // Fallback mock response if ML service is down
        res.json({
            response: "Network Error: Could not reach the AI service. Please ensure the Python server is running.",
            source: "backend-fallback"
        });
    }
});

app.get('/health', (req, res) => {
    res.json({ status: 'Backend is running' });
});

app.listen(PORT, () => {
    console.log(`Backend Server running on port ${PORT}`);
});
