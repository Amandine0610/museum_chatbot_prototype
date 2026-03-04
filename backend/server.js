const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'https://museum-chatbot-ml-1.onrender.com';
console.log('--- BACKEND CONFIGURATION ---');
console.log('ML_SERVICE_URL:', ML_SERVICE_URL);
console.log('PORT:', PORT);
console.log('----------------------------');

app.use(cors());
app.use(express.json());

// Proxy route to ML Service
app.post('/api/chat', async (req, res) => {
    const targetUrl = `${ML_SERVICE_URL}/query`;
    console.log(`[Proxy] Forwarding query to: ${targetUrl}`);

    try {
        const response = await axios.post(targetUrl, req.body, {
            timeout: 85000, // 85 seconds to allow for ML Service cold start
            validateStatus: (status) => status < 500 // Don't throw for 4xx/5xx initially
        });

        // If we get an actual response from the service
        return res.status(response.status).json(response.data);
    } catch (error) {
        console.error(`[CRITICAL] Error reaching ML Service:`, error.message);

        // If we got a response from the Render gateway (502/503 HTML)
        if (error.response) {
            const status = error.response.status;
            const data = error.response.data;

            if (typeof data === 'string' && data.includes('<!DOCTYPE html>')) {
                return res.status(503).json({
                    response: "The AI service is waking up... Please wait 30 seconds and click 'Ask' again. (This happens after inactivity)",
                    status: "waking_up"
                });
            }
            return res.status(status).json(data);
        }

        // Raw timeout or connection failure
        const isTimeout = error.code === 'ECONNABORTED' || error.message.includes('timeout');
        res.status(503).json({
            response: isTimeout
                ? "The AI is still processing. Please try again in 1 minute."
                : "The AI service is currently unreachable.",
            diagnostics: {
                target: targetUrl,
                error: error.message
            }
        });
    }
});

app.get('/health', (req, res) => {
    res.json({ status: 'Backend is running' });
});

app.listen(PORT, () => {
    console.log(`Backend Server running on port ${PORT}`);
});
