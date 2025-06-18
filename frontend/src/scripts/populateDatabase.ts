// Script para Popular o Banco de Dados com Conteúdo Massivo
import { ContentGenerator, generateAllContent } from '../data/contentGenerator';

// Configurações do banco de dados
interface DatabaseConfig {
  apiUrl: string;
  batchSize: number;
  delayBetweenBatches: number; // em ms
}

const DB_CONFIG: DatabaseConfig = {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:3001/api',
  batchSize: 50, // Inserir 50 registros por vez
  delayBetweenBatches: 1000 // 1 segundo entre batches
};

// Função para fazer requisições com retry
async function apiRequest(endpoint: string, data: any, retries = 3): Promise<any> {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(`${DB_CONFIG.apiUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Tentativa ${i + 1} falhou:`, error);
      if (i === retries - 1) throw error;
      await delay(2000 * (i + 1)); // Backoff exponencial
    }
  }
}

// Função de delay
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Função para inserir dados em lotes
async function insertInBatches<T>(
  data: T[], 
  endpoint: string, 
  batchSize: number = DB_CONFIG.batchSize
): Promise<void> {
  const batches = [];
  for (let i = 0; i < data.length; i += batchSize) {
    batches.push(data.slice(i, i + batchSize));
  }

  console.log(`📦 Inserindo ${data.length} registros em ${batches.length} lotes de ${batchSize}...`);

  for (let i = 0; i < batches.length; i++) {
    const batch = batches[i];
    try {
      await apiRequest(endpoint, { items: batch });
      console.log(`✅ Lote ${i + 1}/${batches.length} inserido com sucesso`);
      
      // Delay entre lotes para não sobrecarregar o servidor
      if (i < batches.length - 1) {
        await delay(DB_CONFIG.delayBetweenBatches);
      }
    } catch (error) {
      console.error(`❌ Erro no lote ${i + 1}:`, error);
      throw error;
    }
  }
}

// Script principal de população
export async function populateDatabase(): Promise<void> {
  console.log('🚀 Iniciando população massiva do banco de dados...');
  console.log(`📊 Configuração: ${DB_CONFIG.batchSize} registros por lote, ${DB_CONFIG.delayBetweenBatches}ms de delay`);

  try {
    // 1. Gerar todo o conteúdo
    console.log('\n📝 Gerando conteúdo...');
    const content = generateAllContent();

    // 2. Popular questões por matéria
    console.log('\n📚 Populando questões...');
    await insertInBatches(content.questions, '/questions/bulk');

    // 3. Popular documentos legais
    console.log('\n📋 Populando documentos legais...');
    await insertInBatches(content.documents, '/documents/bulk');

    // 4. Popular materiais de estudo
    console.log('\n📖 Populando materiais de estudo...');
    await insertInBatches(content.materials, '/materials/bulk');

    // 5. Popular simulados
    console.log('\n🎯 Populando simulados...');
    await insertInBatches(content.exams, '/exams/bulk');

    // 6. Criar índices para busca
    console.log('\n🔍 Criando índices de busca...');
    await createSearchIndexes();

    // 7. Gerar estatísticas
    console.log('\n📊 Gerando estatísticas...');
    await generateStatistics(content);

    console.log('\n✅ População do banco de dados concluída com sucesso!');
    console.log(`📈 Resumo:`);
    console.log(`   - Questões: ${content.questions.length}`);
    console.log(`   - Documentos: ${content.documents.length}`);
    console.log(`   - Materiais: ${content.materials.length}`);
    console.log(`   - Simulados: ${content.exams.length}`);

  } catch (error) {
    console.error('❌ Erro durante a população do banco:', error);
    throw error;
  }
}

// Função para criar índices de busca
async function createSearchIndexes(): Promise<void> {
  const indexes = [
    { collection: 'questions', fields: ['subject', 'topic', 'difficulty', 'tags'] },
    { collection: 'documents', fields: ['title', 'keywords', 'subject', 'type'] },
    { collection: 'materials', fields: ['title', 'subject', 'topic', 'tags'] },
    { collection: 'exams', fields: ['title', 'examBoard', 'type', 'subjects'] }
  ];

  for (const index of indexes) {
    try {
      await apiRequest('/admin/create-index', index);
      console.log(`✅ Índice criado para ${index.collection}`);
    } catch (error) {
      console.error(`❌ Erro ao criar índice para ${index.collection}:`, error);
    }
  }
}

// Função para gerar estatísticas
async function generateStatistics(content: any): Promise<void> {
  const stats = {
    totalQuestions: content.questions.length,
    totalDocuments: content.documents.length,
    totalMaterials: content.materials.length,
    totalExams: content.exams.length,
    questionsBySubject: {},
    questionsByDifficulty: { easy: 0, medium: 0, hard: 0 },
    documentsByType: {},
    materialsByType: {},
    examsByType: {},
    lastUpdated: new Date().toISOString()
  };

  // Calcular estatísticas detalhadas
  content.questions.forEach((q: any) => {
    stats.questionsBySubject[q.subject] = (stats.questionsBySubject[q.subject] || 0) + 1;
    stats.questionsByDifficulty[q.difficulty]++;
  });

  content.documents.forEach((d: any) => {
    stats.documentsByType[d.type] = (stats.documentsByType[d.type] || 0) + 1;
  });

  content.materials.forEach((m: any) => {
    stats.materialsByType[m.type] = (stats.materialsByType[m.type] || 0) + 1;
  });

  content.exams.forEach((e: any) => {
    stats.examsByType[e.type] = (stats.examsByType[e.type] || 0) + 1;
  });

  try {
    await apiRequest('/admin/update-stats', stats);
    console.log('✅ Estatísticas atualizadas');
  } catch (error) {
    console.error('❌ Erro ao atualizar estatísticas:', error);
  }
}

// Função para popular conteúdo específico por matéria
export async function populateSubjectContent(subject: string, questionCount = 500): Promise<void> {
  console.log(`📚 Populando conteúdo específico para: ${subject}`);

  try {
    // Gerar questões específicas
    const questions = ContentGenerator.generateQuestions(subject, questionCount);
    await insertInBatches(questions, '/questions/bulk');

    // Gerar documentos relacionados
    const documents = ContentGenerator.generateLegalDocuments(50).filter(d => d.subject === subject);
    if (documents.length > 0) {
      await insertInBatches(documents, '/documents/bulk');
    }

    // Gerar materiais de estudo
    const materials = ContentGenerator.generateStudyMaterials(20).filter(m => m.subject === subject);
    if (materials.length > 0) {
      await insertInBatches(materials, '/materials/bulk');
    }

    console.log(`✅ Conteúdo para ${subject} populado com sucesso!`);
  } catch (error) {
    console.error(`❌ Erro ao popular ${subject}:`, error);
    throw error;
  }
}

// Função para limpar banco de dados
export async function clearDatabase(): Promise<void> {
  console.log('🗑️ Limpando banco de dados...');

  const collections = ['questions', 'documents', 'materials', 'exams'];

  for (const collection of collections) {
    try {
      await apiRequest(`/admin/clear/${collection}`, {});
      console.log(`✅ ${collection} limpo`);
    } catch (error) {
      console.error(`❌ Erro ao limpar ${collection}:`, error);
    }
  }

  console.log('✅ Banco de dados limpo!');
}

// Função para backup do banco
export async function backupDatabase(): Promise<void> {
  console.log('💾 Criando backup do banco de dados...');

  try {
    const backup = await apiRequest('/admin/backup', {});
    
    // Salvar backup localmente
    const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `duolingo-juridico-backup-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('✅ Backup criado e baixado!');
  } catch (error) {
    console.error('❌ Erro ao criar backup:', error);
    throw error;
  }
}

// Função para restaurar backup
export async function restoreDatabase(backupFile: File): Promise<void> {
  console.log('📥 Restaurando backup...');

  try {
    const backupData = JSON.parse(await backupFile.text());
    await apiRequest('/admin/restore', backupData);
    console.log('✅ Backup restaurado com sucesso!');
  } catch (error) {
    console.error('❌ Erro ao restaurar backup:', error);
    throw error;
  }
}

// Executar se chamado diretamente
if (require.main === module) {
  populateDatabase()
    .then(() => {
      console.log('🎉 Script executado com sucesso!');
      process.exit(0);
    })
    .catch((error) => {
      console.error('💥 Erro fatal:', error);
      process.exit(1);
    });
} 