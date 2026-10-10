import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL || 'https://placeholder.supabase.co',
  process.env.SUPABASE_ANON_KEY || 'placeholder'
);

export async function searchCurriculum(query, matchCount = 3) {
  try {
    // Graceful fallback while Nidiya prepares the Supabase vector table
    return [];
  } catch (error) {
    console.warn('Vector search skipped:', error.message);
    return [];
  }
}