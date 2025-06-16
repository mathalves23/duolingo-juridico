"""
Sistema Avançado de Pesquisa Jurídica - Duolingo Jurídico
Integra múltiplas fontes legais com IA para pesquisas avançadas
"""

import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import requests
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SearchType(Enum):
    JURISPRUDENCE = "jurisprudence"
    LEGISLATION = "legislation"
    DOCTRINE = "doctrine"
    NEWS = "news"
    MIXED = "mixed"

class Court(Enum):
    STF = "stf"
    STJ = "stj"
    TST = "tst"
    TRF = "trf"
    TRT = "trt"
    TJSP = "tjsp"
    TJRJ = "tjrj"
    ALL = "all"

@dataclass
class LegalDocument:
    """Documento jurídico encontrado"""
    id: str
    title: str
    summary: str
    content: str
    source: str
    court: Optional[str]
    date: datetime
    relevance_score: float
    document_type: str
    url: str
    citations: List[str]
    keywords: List[str]
    legal_area: str

@dataclass
class SearchResult:
    """Resultado de pesquisa jurídica"""
    query: str
    documents: List[LegalDocument]
    total_found: int
    search_time_ms: int
    sources_searched: List[str]
    suggestions: List[str]
    related_topics: List[str]
    ai_summary: str

class LegalResearchAPI:
    """API para pesquisa jurídica avançada"""
    
    def __init__(self):
        self.stf_api_url = "https://jurisprudencia.stf.jus.br/pages/search"
        self.stj_api_url = "https://www.stj.jus.br/SCON"
        self.planalto_api_url = "http://www4.planalto.gov.br/legislacao"
        self.session = requests.Session()
        
        # Headers para evitar bloqueios
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        })
    
    async def search(self, 
                    query: str, 
                    search_type: SearchType = SearchType.MIXED,
                    courts: List[Court] = None,
                    date_from: Optional[datetime] = None,
                    date_to: Optional[datetime] = None,
                    limit: int = 50) -> SearchResult:
        """Executa pesquisa jurídica avançada"""
        
        start_time = datetime.now()
        
        # Cache key para evitar pesquisas duplicadas
        cache_key = self._generate_cache_key(query, search_type, courts, date_from, date_to, limit)
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return SearchResult(**cached_result)
        
        # Executa pesquisas paralelas em diferentes fontes
        search_tasks = []
        sources_searched = []
        
        if search_type in [SearchType.JURISPRUDENCE, SearchType.MIXED]:
            if not courts or Court.STF in courts or Court.ALL in courts:
                search_tasks.append(self._search_stf(query, date_from, date_to))
                sources_searched.append("STF")
            
            if not courts or Court.STJ in courts or Court.ALL in courts:
                search_tasks.append(self._search_stj(query, date_from, date_to))
                sources_searched.append("STJ")
        
        if search_type in [SearchType.LEGISLATION, SearchType.MIXED]:
            search_tasks.append(self._search_legislation(query, date_from, date_to))
            sources_searched.append("Planalto")
        
        if search_type in [SearchType.DOCTRINE, SearchType.MIXED]:
            search_tasks.append(self._search_doctrine(query))
            sources_searched.append("Doutrina")
        
        if search_type in [SearchType.NEWS, SearchType.MIXED]:
            search_tasks.append(self._search_legal_news(query))
            sources_searched.append("Notícias Jurídicas")
        
        # Executa todas as pesquisas em paralelo
        try:
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
        except Exception as e:
            results = []
        
        # Combina e processa resultados
        all_documents = []
        for result in results:
            if isinstance(result, list):
                all_documents.extend(result)
        
        # Ordena por relevância e remove duplicatas
        unique_documents = self._remove_duplicates(all_documents)
        sorted_documents = sorted(unique_documents, key=lambda x: x.relevance_score, reverse=True)
        
        # Limita resultados
        final_documents = sorted_documents[:limit]
        
        # Gera sugestões e análise com IA
        suggestions = await self._generate_search_suggestions(query, final_documents)
        related_topics = await self._extract_related_topics(final_documents)
        ai_summary = await self._generate_ai_summary(query, final_documents)
        
        search_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        result = SearchResult(
            query=query,
            documents=final_documents,
            total_found=len(all_documents),
            search_time_ms=search_time,
            sources_searched=sources_searched,
            suggestions=suggestions,
            related_topics=related_topics,
            ai_summary=ai_summary
        )
        
        # Cache por 1 hora
        cache.set(cache_key, asdict(result), 3600)
        
        return result
    
    async def _search_stf(self, query: str, date_from: Optional[datetime], date_to: Optional[datetime]) -> List[LegalDocument]:
        """Pesquisa no STF"""
        try:
            # Parâmetros da pesquisa
            params = {
                'termo': query,
                'tipo': 'jurisprudencia',
                'ordenacao': 'relevancia'
            }
            
            if date_from:
                params['dataInicio'] = date_from.strftime('%d/%m/%Y')
            if date_to:
                params['dataFim'] = date_to.strftime('%d/%m/%Y')
            
            # Mock de dados do STF (em produção, usar API real)
            mock_results = [
                {
                    'id': f'stf_{hashlib.md5(query.encode()).hexdigest()[:8]}',
                    'titulo': f'Acórdão STF sobre {query}',
                    'ementa': f'Ementa do acórdão relacionado a {query}...',
                    'texto': f'Texto completo do acórdão que trata de {query}...',
                    'data': datetime.now() - timedelta(days=30),
                    'url': f'https://jurisprudencia.stf.jus.br/pages/search/acordao/{query}',
                    'relator': 'Min. Marco Aurélio'
                }
            ]
            
            documents = []
            for result in mock_results:
                doc = LegalDocument(
                    id=result['id'],
                    title=result['titulo'],
                    summary=result['ementa'][:200],
                    content=result['texto'],
                    source='STF',
                    court='STF',
                    date=result['data'],
                    relevance_score=0.9,
                    document_type='Acórdão',
                    url=result['url'],
                    citations=[],
                    keywords=query.split(),
                    legal_area='Constitucional'
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            return []
    
    async def _search_stj(self, query: str, date_from: Optional[datetime], date_to: Optional[datetime]) -> List[LegalDocument]:
        """Pesquisa no STJ"""
        try:
            # Mock de dados do STJ
            mock_results = [
                {
                    'id': f'stj_{hashlib.md5(query.encode()).hexdigest()[:8]}',
                    'titulo': f'Recurso Especial STJ - {query}',
                    'ementa': f'Ementa do recurso especial sobre {query}...',
                    'texto': f'Acórdão que discute questões relacionadas a {query}...',
                    'data': datetime.now() - timedelta(days=45),
                    'url': f'https://www.stj.jus.br/websecstj/cgi/revista/REJ.cgi/ATC?seq={query}',
                    'relator': 'Min. Luiz Felipe Salomão'
                }
            ]
            
            documents = []
            for result in mock_results:
                doc = LegalDocument(
                    id=result['id'],
                    title=result['titulo'],
                    summary=result['ementa'][:200],
                    content=result['texto'],
                    source='STJ',
                    court='STJ',
                    date=result['data'],
                    relevance_score=0.85,
                    document_type='Recurso Especial',
                    url=result['url'],
                    citations=[],
                    keywords=query.split(),
                    legal_area='Infraconstitucional'
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            return []
    
    async def _search_legislation(self, query: str, date_from: Optional[datetime], date_to: Optional[datetime]) -> List[LegalDocument]:
        """Pesquisa na legislação"""
        try:
            # Mock de dados de legislação
            mock_results = [
                {
                    'id': f'lei_{hashlib.md5(query.encode()).hexdigest()[:8]}',
                    'titulo': f'Lei relacionada a {query}',
                    'ementa': f'Lei que regulamenta aspectos de {query}',
                    'texto': f'Texto da lei que trata de {query}...',
                    'data': datetime.now() - timedelta(days=365),
                    'url': f'http://www.planalto.gov.br/ccivil_03/_ato/{query}.htm',
                    'tipo': 'Lei Ordinária'
                }
            ]
            
            documents = []
            for result in mock_results:
                doc = LegalDocument(
                    id=result['id'],
                    title=result['titulo'],
                    summary=result['ementa'][:200],
                    content=result['texto'],
                    source='Planalto',
                    court=None,
                    date=result['data'],
                    relevance_score=0.8,
                    document_type=result['tipo'],
                    url=result['url'],
                    citations=[],
                    keywords=query.split(),
                    legal_area='Legislação'
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            return []
    
    async def _search_doctrine(self, query: str) -> List[LegalDocument]:
        """Pesquisa na doutrina"""
        try:
            # Mock de dados doutrinários
            mock_results = [
                {
                    'id': f'doutrina_{hashlib.md5(query.encode()).hexdigest()[:8]}',
                    'titulo': f'Artigo Doutrinário sobre {query}',
                    'resumo': f'Análise doutrinária aprofundada sobre {query}',
                    'texto': f'Artigo que analisa teoricamente {query}...',
                    'data': datetime.now() - timedelta(days=60),
                    'url': f'https://revista-juridica.com/artigo/{query.replace(" ", "-")}',
                    'autor': 'Prof. Dr. Jurista Silva'
                }
            ]
            
            documents = []
            for result in mock_results:
                doc = LegalDocument(
                    id=result['id'],
                    title=result['titulo'],
                    summary=result['resumo'][:200],
                    content=result['texto'],
                    source='Doutrina',
                    court=None,
                    date=result['data'],
                    relevance_score=0.7,
                    document_type='Artigo Doutrinário',
                    url=result['url'],
                    citations=[],
                    keywords=query.split(),
                    legal_area='Doutrina'
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            return []
    
    async def _search_legal_news(self, query: str) -> List[LegalDocument]:
        """Pesquisa em notícias jurídicas"""
        try:
            # Mock de notícias jurídicas
            mock_results = [
                {
                    'id': f'news_{hashlib.md5(query.encode()).hexdigest()[:8]}',
                    'titulo': f'STF decide caso importante sobre {query}',
                    'resumo': f'Supremo Tribunal Federal toma decisão relevante sobre {query}',
                    'texto': f'O STF decidiu questão importante relacionada a {query}...',
                    'data': datetime.now() - timedelta(days=5),
                    'url': f'https://conjur.com.br/noticia/{query.replace(" ", "-")}',
                    'fonte': 'ConJur'
                }
            ]
            
            documents = []
            for result in mock_results:
                doc = LegalDocument(
                    id=result['id'],
                    title=result['titulo'],
                    summary=result['resumo'][:200],
                    content=result['texto'],
                    source='ConJur',
                    court=None,
                    date=result['data'],
                    relevance_score=0.6,
                    document_type='Notícia',
                    url=result['url'],
                    citations=[],
                    keywords=query.split(),
                    legal_area='Atualidades'
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            return []
    
    def _remove_duplicates(self, documents: List[LegalDocument]) -> List[LegalDocument]:
        """Remove documentos duplicados baseado no conteúdo"""
        seen_hashes = set()
        unique_docs = []
        
        for doc in documents:
            content_hash = hashlib.md5(doc.content.encode()).hexdigest()
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_docs.append(doc)
        
        return unique_docs
    
    async def _generate_search_suggestions(self, query: str, documents: List[LegalDocument]) -> List[str]:
        """Gera sugestões de pesquisa baseadas nos resultados"""
        try:
            # Análise com IA das palavras-chave mais relevantes
            all_keywords = []
            for doc in documents:
                all_keywords.extend(doc.keywords)
            
            # Conta frequência e gera sugestões
            keyword_freq = {}
            for keyword in all_keywords:
                keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
            
            # Top palavras-chave diferentes da consulta original
            suggestions = []
            for keyword, freq in sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True):
                if keyword.lower() not in query.lower() and len(suggestions) < 5:
                    suggestions.append(f'{query} AND {keyword}')
            
            return suggestions
            
        except Exception:
            return [
                f'{query} jurisprudência',
                f'{query} doutrina',
                f'{query} legislação',
                f'{query} STF',
                f'{query} STJ'
            ]
    
    async def _extract_related_topics(self, documents: List[LegalDocument]) -> List[str]:
        """Extrai tópicos relacionados dos documentos"""
        try:
            # Análise simples de tópicos relacionados
            topics = set()
            
            for doc in documents:
                # Extrai termos jurídicos comuns do conteúdo
                legal_terms = [
                    'constitucional', 'civil', 'penal', 'administrativo',
                    'tributário', 'trabalhista', 'processual', 'comercial',
                    'ambiental', 'consumidor', 'família', 'sucessões'
                ]
                
                content_lower = doc.content.lower()
                for term in legal_terms:
                    if term in content_lower:
                        topics.add(term.title())
            
            return list(topics)[:8]
            
        except Exception:
            return ['Direito Constitucional', 'Direito Civil', 'Direito Penal']
    
    async def _generate_ai_summary(self, query: str, documents: List[LegalDocument]) -> str:
        """Gera resumo com IA dos resultados da pesquisa"""
        try:
            if not documents:
                return f"Não foram encontrados resultados relevantes para '{query}'."
            
            # Resumo baseado nos documentos encontrados
            sources = list(set(doc.source for doc in documents))
            doc_types = list(set(doc.document_type for doc in documents))
            
            summary = f"Foram encontrados {len(documents)} documentos relevantes para '{query}' "
            summary += f"nas seguintes fontes: {', '.join(sources)}. "
            summary += f"Os tipos de documentos incluem: {', '.join(doc_types)}. "
            
            # Análise das datas
            if documents:
                latest_doc = max(documents, key=lambda x: x.date)
                summary += f"O documento mais recente é de {latest_doc.date.strftime('%d/%m/%Y')} "
                summary += f"({latest_doc.source}). "
            
            # Análise de relevância
            high_relevance = [d for d in documents if d.relevance_score > 0.8]
            if high_relevance:
                summary += f"{len(high_relevance)} documentos apresentam alta relevância para sua pesquisa."
            
            return summary
            
        except Exception:
            return f"Análise dos resultados para '{query}' está temporariamente indisponível."
    
    def _generate_cache_key(self, query: str, search_type: SearchType, courts: List[Court], 
                           date_from: Optional[datetime], date_to: Optional[datetime], limit: int) -> str:
        """Gera chave de cache única para a pesquisa"""
        key_parts = [
            query,
            search_type.value,
            ','.join([c.value for c in courts]) if courts else 'all',
            date_from.isoformat() if date_from else 'none',
            date_to.isoformat() if date_to else 'none',
            str(limit)
        ]
        
        key_string = '|'.join(key_parts)
        return f"legal_search:{hashlib.md5(key_string.encode()).hexdigest()}"

class CaseLawAnalyzer:
    """Analisador avançado de jurisprudência"""
    
    def __init__(self):
        self.research_api = LegalResearchAPI()
    
    async def analyze_precedents(self, case_topic: str, court: Court = Court.ALL) -> Dict[str, Any]:
        """Analisa precedentes sobre um tópico específico"""
        
        # Busca jurisprudência relevante
        search_result = await self.research_api.search(
            query=case_topic,
            search_type=SearchType.JURISPRUDENCE,
            courts=[court] if court != Court.ALL else None,
            limit=100
        )
        
        if not search_result.documents:
            return {
                'topic': case_topic,
                'precedents_found': 0,
                'analysis': 'Nenhum precedente encontrado para análise'
            }
        
        # Análise dos precedentes
        precedents_by_court = {}
        precedents_by_year = {}
        favorable_vs_contrary = {'favorable': 0, 'contrary': 0, 'neutral': 0}
        
        for doc in search_result.documents:
            # Agrupa por tribunal
            court_name = doc.court or 'Não especificado'
            if court_name not in precedents_by_court:
                precedents_by_court[court_name] = []
            precedents_by_court[court_name].append(doc)
            
            # Agrupa por ano
            year = doc.date.year
            if year not in precedents_by_year:
                precedents_by_year[year] = 0
            precedents_by_year[year] += 1
            
            # Análise de sentimento (simplificada)
            content_lower = doc.content.lower()
            if any(word in content_lower for word in ['procedente', 'deferido', 'acolhido']):
                favorable_vs_contrary['favorable'] += 1
            elif any(word in content_lower for word in ['improcedente', 'indeferido', 'rejeitado']):
                favorable_vs_contrary['contrary'] += 1
            else:
                favorable_vs_contrary['neutral'] += 1
        
        # Identifica precedentes mais importantes (maior relevância)
        key_precedents = sorted(search_result.documents, key=lambda x: x.relevance_score, reverse=True)[:5]
        
        # Tendência temporal
        years_sorted = sorted(precedents_by_year.keys())
        if len(years_sorted) > 1:
            recent_count = sum(precedents_by_year[year] for year in years_sorted[-2:])
            older_count = sum(precedents_by_year[year] for year in years_sorted[:-2])
            trend = "crescente" if recent_count > older_count else "decrescente" if recent_count < older_count else "estável"
        else:
            trend = "insuficiente para análise"
        
        return {
            'topic': case_topic,
            'precedents_found': len(search_result.documents),
            'analysis_summary': f"Análise de {len(search_result.documents)} precedentes sobre {case_topic}",
            'precedents_by_court': {k: len(v) for k, v in precedents_by_court.items()},
            'precedents_by_year': precedents_by_year,
            'decision_pattern': favorable_vs_contrary,
            'temporal_trend': trend,
            'key_precedents': [
                {
                    'title': p.title,
                    'court': p.court,
                    'date': p.date.isoformat(),
                    'relevance': p.relevance_score,
                    'url': p.url
                }
                for p in key_precedents
            ],
            'legal_principles': await self._extract_legal_principles(search_result.documents),
            'recommendations': await self._generate_legal_recommendations(case_topic, search_result.documents)
        }
    
    async def _extract_legal_principles(self, documents: List[LegalDocument]) -> List[str]:
        """Extrai princípios jurídicos dos documentos"""
        principles = set()
        
        # Princípios jurídicos comuns
        legal_principles = [
            'devido processo legal', 'contraditório', 'ampla defesa',
            'igualdade', 'proporcionalidade', 'razoabilidade',
            'dignidade da pessoa humana', 'legalidade', 'moralidade',
            'publicidade', 'eficiência', 'supremacia do interesse público',
            'presunção de inocência', 'non bis in idem', 'coisa julgada'
        ]
        
        for doc in documents:
            content_lower = doc.content.lower()
            for principle in legal_principles:
                if principle in content_lower:
                    principles.add(principle.title())
        
        return list(principles)[:10]
    
    async def _generate_legal_recommendations(self, topic: str, documents: List[LegalDocument]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        if not documents:
            return ["Buscar precedentes em tribunais inferiores", "Consultar doutrina especializada"]
        
        # Análise de tendências
        recent_docs = [d for d in documents if d.date > datetime.now() - timedelta(days=365)]
        if len(recent_docs) < len(documents) * 0.3:
            recommendations.append("Atenção: poucos precedentes recentes encontrados. Verificar mudanças legislativas.")
        
        # Análise de tribunais
        stf_docs = [d for d in documents if d.court == 'STF']
        if stf_docs:
            recommendations.append(f"Considerar {len(stf_docs)} precedente(s) do STF para fundamentação constitucional.")
        
        stj_docs = [d for d in documents if d.court == 'STJ']
        if stj_docs:
            recommendations.append(f"Analisar {len(stj_docs)} precedente(s) do STJ para questões infraconstitucionais.")
        
        # Análise de relevância
        high_relevance = [d for d in documents if d.relevance_score > 0.8]
        if high_relevance:
            recommendations.append(f"Focar nos {len(high_relevance)} precedentes de maior relevância.")
        
        return recommendations[:5]

# Instância global da API de pesquisa
legal_research_api = LegalResearchAPI()
case_law_analyzer = CaseLawAnalyzer()

# Funções de utilidade
async def quick_legal_search(query: str, limit: int = 10) -> SearchResult:
    """Busca jurídica rápida"""
    return await legal_research_api.search(query, limit=limit)

async def analyze_case_law(topic: str, court: str = 'all') -> Dict[str, Any]:
    """Análise rápida de jurisprudência"""
    court_enum = Court.ALL
    try:
        court_enum = Court(court.lower())
    except ValueError:
        pass
    
    return await case_law_analyzer.analyze_precedents(topic, court_enum) 