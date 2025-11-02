import { drizzle } from 'drizzle-orm/neon-http';
import { neon } from '@neondatabase/serverless';
import * as dotenv from 'dotenv';

dotenv.config({ path: 'ai-chatbot-main/.env.local' });

const sql = neon(process.env.DATABASE_URL!);
const db = drizzle(sql);

async function checkTables() {
  console.log('🔍 Checking database tables...\n');
  
  const result = await sql`
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
  `;
  
  console.log('📋 Tables in database:');
  result.forEach((row: any) => {
    console.log(`  - ${row.table_name}`);
  });
  
  console.log('\n🔍 Checking research_tasks table structure...\n');
  
  const columns = await sql`
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'research_tasks'
    ORDER BY ordinal_position;
  `;
  
  if (columns.length > 0) {
    console.log('✅ research_tasks table exists!');
    console.log('\nColumns:');
    columns.forEach((col: any) => {
      console.log(`  - ${col.column_name}: ${col.data_type} (nullable: ${col.is_nullable})`);
    });
  } else {
    console.log('❌ research_tasks table does NOT exist!');
  }
}

checkTables().catch(console.error);
