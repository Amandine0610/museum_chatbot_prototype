import express from 'express';
import axios from 'axios';

const router = express.Router();

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

/**
 * POST /api/chat
 * Send a message to the chatbot and get a response
 */
router.post('/', async (req, res) => {
  try {
    const { message, language, museum_id } = req.body;

    // Validate required fields
    if (!message || !language || !museum_id) {
      return res.status(400).json({
        error: 'Missing required fields',
        required: ['message', 'language', 'museum_id']
      });
    }

    // Validate language
    const validLanguages = ['en', 'fr', 'rw'];
    if (!validLanguages.includes(language)) {
      return res.status(400).json({
        error: 'Invalid language',
        valid: validLanguages
      });
    }

    console.log(`[Chat] Processing message: "${message.substring(0, 50)}..."`);
    console.log(`[Chat] Language: ${language}, Museum: ${museum_id}`);

    // Forward to ML service
    const mlResponse = await axios.post(`${ML_SERVICE_URL}/api/query`, {
      message,
      language,
      museum_id
    }, {
      timeout: 25000
    });

    console.log('[Chat] Response received from ML service');

    res.json({
      response: mlResponse.data.response,
      sources: mlResponse.data.sources || [],
      language: mlResponse.data.detected_language || language
    });

  } catch (error) {
    console.error('[Chat] Error:', error.message);

    // Return fallback response if ML service is unavailable
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
      return res.json({
        response: getFallbackResponse(req.body.language),
        sources: [],
        fallback: true
      });
    }

    res.status(500).json({
      error: 'Failed to process message',
      message: error.message
    });
  }
});

/**
 * Get fallback response when ML service is unavailable
 */
function getFallbackResponse(language) {
  const responses = {
    en: "I apologize, but I'm having trouble connecting to my knowledge base right now. Please try again in a few moments, or feel free to ask about our museum's general information.",
    fr: "Je m'excuse, mais j'ai du mal à me connecter à ma base de connaissances pour le moment. Veuillez réessayer dans quelques instants, ou n'hésitez pas à poser des questions sur les informations générales de notre musée.",
    rw: "Munyihanganire,mfite ikibazo cyo kwihuza n'ububiko bw'ibitekerezo. Mwongere mugerageze mukanya gato, cyangwa mubaze ibijyanye n'amakuru yerekeye inzu ndangamurage yacu."
  };
  return responses[language] || responses.en;
}

export default router;