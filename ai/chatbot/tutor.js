import { groq } from '../models/groqClient.js';
import { searchCurriculum } from '../rag/vectorStore.js';

/**
 * Handles conversational queries from students using RAG and Groq.
 * @param {string} studentQuestion - The query typed or spoken by the student.
 * @param {Array} history - Previous messages: [{ role: 'user'|'assistant', content: '...' }]
 */
export async function getTutorResponse(studentQuestion, history = []) {
  try {
    // 1. Retrieve matching lesson chunks (falls back smoothly if DB is empty)
    const matchingDocs = await searchCurriculum(studentQuestion, 3);
    const contextText = matchingDocs.map((doc) => doc.content).join('\n---\n');

    // 2. Define tutor instructions
    const systemInstruction = `You are Inteliedu's interactive AI Tutor.
Your goal is to explain concepts clearly, patiently, and engagingly for students.

Rules:
1. Prioritize the lesson context provided below.
2. If the context is empty or lacks the answer, explain using accurate general knowledge.
3. Keep answers structured, encouraging, concise, and easy to understand.

Lesson Context:
${contextText || 'No specific textbook passages retrieved for this question.'}`;

    // 3. Format messages for Groq
    const messages = [
      { role: 'system', content: systemInstruction },
      ...history.map((msg) => ({
        role: msg.role === 'model' ? 'assistant' : msg.role,
        content: msg.text || msg.content,
      })),
      { role: 'user', content: studentQuestion },
    ];

    // 4. Generate response using your account's active model
    const completion = await groq.chat.completions.create({
      model: 'openai/gpt-oss-120b',
      messages,
      temperature: 0.3,
      max_tokens: 1024,
    });

    return {
      answer: completion.choices[0]?.message?.content || '',
      retrievedContexts: matchingDocs,
    };
  } catch (error) {
    console.error('Error generating Groq tutor response:', error);
    throw error;
  }
}