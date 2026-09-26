/**
 * Inteliedu Backend Server Entrypoint
 * Architecture Placeholder - Express & WebSocket Bootstrap
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Core Middleware
app.use(cors({ origin: process.env.CORS_ORIGIN || 'http://localhost:5173' }));
app.use(express.json());

// Health Check Endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'Inteliedu Backend API',
  });
});

// Root API v1 Route Placeholder
app.get('/api/v1', (req, res) => {
  res.status(200).json({
    message: 'Inteliedu API v1 initialized. Awaiting route module mounting.',
  });
});

if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`[Inteliedu] Server running on http://localhost:${PORT}`);
  });
}

export default app;
