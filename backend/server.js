const express = require('express');
const cors = require('cors');
const swaggerUi = require('swagger-ui-express');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:5000';

app.use(cors());
app.use(express.json());

// Swagger Setup
const swaggerDocument = {
    openapi: '3.0.0',
    info: {
        title: 'Museum Chatbot API',
        version: '1.0.0',
        description: 'API Gateway for the Rwandan Museum Chatbot'
    },
    servers: [
        {
            url: `http://localhost:${PORT}`,
            description: 'Local server'
        }
    ],
    paths: {
        '/chat': {
            post: {
                summary: 'Send a message to the chatbot',
                requestBody: {
                    required: true,
                    content: {
                        'application/json': {
                            schema: {
                                type: 'object',
                                properties: {
                                    message: {
                                        type: 'string',
                                        example: 'Tell me about the King\'s Palace.'
                                    },
                                    language: {
                                        type: 'string',
                                        example: 'en'
                                    }
                                }
                            }
                        }
                    }
                },
                responses: {
                    200: {
                        description: 'Successful response',
                        content: {
                            'application/json': {
                                schema: {
                                    type: 'object',
                                    properties: {
                                        response: {
                                            type: 'string'
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        '/health': {
            get: {
                summary: 'Check server health',
                responses: {
                    200: {
                        description: 'Server is running'
                    }
                }
            }
        }
    }
};

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// Routes
app.get('/health', (req, res) => {
    res.json({ status: 'ok', message: 'Backend is running' });
});

app.post('/chat', async (req, res) => {
    const { message, language } = req.body;

    if (!message) {
        return res.status(400).json({ error: 'Message is required' });
    }

    try {
        // Forward to ML Service
        // For demo purposes, if ML service is not running, we catch the error and return a mock response
        try {
            const response = await axios.post(`${ML_SERVICE_URL}/query`, {
                query: message,
                language: language || 'en'
            });
            res.json(response.data);
        } catch (mlError) {
            console.warn('ML Service unreachable, returning mock response:', mlError.message);
            res.json({
                response: `[Mock Response] ML Service unavailable. You asked: "${message}". The King's Palace Museum is located in Nyanza...`,
                source: 'backend-mock'
            });
        }

    } catch (error) {
        console.error('Error processing chat:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.listen(PORT, () => {
    console.log(`Backend Server running on port ${PORT}`);
    console.log(`Swagger UI available at http://localhost:${PORT}/api-docs`);
});
