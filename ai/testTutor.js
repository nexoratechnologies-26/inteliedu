import { getTutorResponse } from './chatbot/tutor.js';

async function runTest() {
  console.log('🤖 Sending query to Inteliedu AI Tutor (via Groq)...\n');

  const testQuestion = 'Can you explain why the Earth experiences seasons?';

  try {
    const result = await getTutorResponse(testQuestion);
    console.log('--- 🎓 AI Tutor Response ---');
    console.log(result.answer);
    console.log('----------------------------');
    console.log('\nRetrieved context passages used:', result.retrievedContexts.length);
  } catch (err) {
    console.error('❌ Test failed with error:', err.message);
  }
}

runTest();