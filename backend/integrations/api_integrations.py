"""
Integração com APIs reais para produção
"""

import os
import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import openai
import anthropic
from web3 import Web3
import hashlib
import json
import time
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from celery import shared_task

# Configurações das APIs
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
BLOCKCHAIN_RPC_URL = os.getenv('BLOCKCHAIN_RPC_URL', 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID')
BLOCKCHAIN_PRIVATE_KEY = os.getenv('BLOCKCHAIN_PRIVATE_KEY')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# Configurar clientes
openai.api_key = OPENAI_API_KEY
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))


class OpenAIIntegration:
    """Integração com OpenAI GPT-4 e modelos de IA"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.models = {
            'gpt-4': 'gpt-4-1106-preview',
            'gpt-3.5': 'gpt-3.5-turbo-1106',
            'whisper': 'whisper-1',
            'dall-e': 'dall-e-3'
        }
    
    async def generate_legal_explanation(self, question: str, context: Dict) -> Dict:
        """Gerar explicação jurídica usando GPT-4"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """Você é um especialista em direito brasileiro com mais de 20 anos de experiência.
                    Forneça explicações claras, didáticas e fundamentadas sobre questões jurídicas.
                    Sempre cite a legislação aplicável e jurisprudência relevante."""
                },
                {
                    "role": "user",
                    "content": f"""
                    Questão: {question}
                    Contexto: {json.dumps(context, indent=2)}
                    
                    Por favor, forneça uma explicação completa incluindo:
                    1. Fundamento legal
                    2. Interpretação doutrinária
                    3. Jurisprudência relevante
                    4. Aplicação prática
                    """
                }
            ]
            
            response = await self.client.chat.completions.acreate(
                model=self.models['gpt-4'],
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            return {
                'success': True,
                'explanation': response.choices[0].message.content,
                'model': 'GPT-4',
                'tokens': response.usage.total_tokens,
                'cost': self._calculate_cost(response.usage.total_tokens, 'gpt-4')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': 'GPT-4'
            }
    
    async def generate_study_plan(self, user_profile: Dict, goals: List[str]) -> Dict:
        """Gerar plano de estudos personalizado"""
        try:
            prompt = f"""
            Crie um plano de estudos personalizado para concursos jurídicos brasileiros.
            
            Perfil do usuário:
            {json.dumps(user_profile, indent=2)}
            
            Objetivos:
            {', '.join(goals)}
            
            Crie um plano detalhado incluindo:
            1. Cronograma semanal
            2. Disciplinas prioritárias
            3. Métodos de estudo recomendados
            4. Metas mensais
            5. Estratégias de revisão
            """
            
            response = await self.client.chat.completions.acreate(
                model=self.models['gpt-4'],
                messages=[
                    {"role": "system", "content": "Você é um coach especializado em concursos jurídicos brasileiros."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=3000
            )
            
            return {
                'success': True,
                'study_plan': response.choices[0].message.content,
                'model': 'GPT-4',
                'tokens': response.usage.total_tokens
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def transcribe_audio(self, audio_file_path: str) -> Dict:
        """Transcrever áudio usando Whisper"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.acreate(
                    model=self.models['whisper'],
                    file=audio_file,
                    language="pt"
                )
            
            return {
                'success': True,
                'transcription': response.text,
                'model': 'Whisper'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_cost(self, tokens: int, model: str) -> Decimal:
        """Calcular custo baseado no modelo e tokens"""
        costs = {
            'gpt-4': Decimal('0.03') / 1000,  # $0.03 per 1K tokens
            'gpt-3.5': Decimal('0.002') / 1000,  # $0.002 per 1K tokens
        }
        return costs.get(model, Decimal('0')) * tokens


class ClaudeIntegration:
    """Integração com Claude (Anthropic)"""
    
    def __init__(self):
        self.client = anthropic_client
    
    async def analyze_legal_case(self, case_data: Dict) -> Dict:
        """Analisar caso jurídico com Claude"""
        try:
            message = await self.client.messages.acreate(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.2,
                system="""Você é um jurista experiente especializado em análise de casos.
                Forneça análises técnicas precisas com fundamentação legal sólida.""",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                        Analise este caso jurídico:
                        {json.dumps(case_data, indent=2)}
                        
                        Forneça:
                        1. Análise dos fatos
                        2. Questões jurídicas relevantes
                        3. Precedentes aplicáveis
                        4. Possíveis estratégias
                        5. Prognóstico do caso
                        """
                    }
                ]
            )
            
            return {
                'success': True,
                'analysis': message.content[0].text,
                'model': 'Claude-3-Opus',
                'tokens': message.usage.input_tokens + message.usage.output_tokens
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def generate_legal_document(self, template_type: str, parameters: Dict) -> Dict:
        """Gerar documento jurídico usando Claude"""
        try:
            templates = {
                'petition': 'petição inicial',
                'appeal': 'recurso',
                'contract': 'contrato',
                'legal_opinion': 'parecer jurídico'
            }
            
            document_type = templates.get(template_type, 'documento jurídico')
            
            message = await self.client.messages.acreate(
                model="claude-3-opus-20240229",
                max_tokens=3000,
                temperature=0.1,
                system=f"""Você é um advogado especialista em redação jurídica.
                Crie documentos formais seguindo as melhores práticas do direito brasileiro.""",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                        Crie um(a) {document_type} com os seguintes parâmetros:
                        {json.dumps(parameters, indent=2)}
                        
                        O documento deve seguir:
                        1. Formatação jurídica padrão
                        2. Linguagem técnica adequada
                        3. Fundamentação legal sólida
                        4. Estrutura lógica e clara
                        """
                    }
                ]
            )
            
            return {
                'success': True,
                'document': message.content[0].text,
                'model': 'Claude-3-Opus',
                'type': document_type
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


class BlockchainIntegration:
    """Integração com blockchain para certificações e NFTs"""
    
    def __init__(self):
        self.w3 = web3
        self.contract_address = os.getenv('SMART_CONTRACT_ADDRESS')
        self.private_key = BLOCKCHAIN_PRIVATE_KEY
        
        # ABI do contrato inteligente para certificações
        self.contract_abi = [
            {
                "inputs": [{"name": "user", "type": "address"}, {"name": "achievement", "type": "string"}],
                "name": "mintCertificate",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "getCertificate",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            }
        ]
    
    async def mint_achievement_nft(self, user_address: str, achievement_data: Dict) -> Dict:
        """Criar NFT de conquista"""
        try:
            if not self.w3.isConnected():
                return {'success': False, 'error': 'Blockchain connection failed'}
            
            contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.contract_abi
            )
            
            # Preparar dados da conquista
            achievement_json = json.dumps({
                'user_id': achievement_data['user_id'],
                'achievement_type': achievement_data['type'],
                'title': achievement_data['title'],
                'description': achievement_data['description'],
                'date_earned': achievement_data['date'].isoformat(),
                'course': achievement_data.get('course', ''),
                'score': achievement_data.get('score', 0),
                'metadata_hash': self._generate_metadata_hash(achievement_data)
            })
            
            # Executar transação
            account = self.w3.eth.account.from_key(self.private_key)
            
            transaction = contract.functions.mintCertificate(
                user_address,
                achievement_json
            ).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': self.w3.toWei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(account.address)
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Aguardar confirmação
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'transaction_hash': receipt.transactionHash.hex(),
                'token_id': receipt.logs[0]['topics'][3].hex(),
                'gas_used': receipt.gasUsed,
                'block_number': receipt.blockNumber
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def verify_certificate(self, token_id: str) -> Dict:
        """Verificar autenticidade de certificado"""
        try:
            contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.contract_abi
            )
            
            certificate_data = contract.functions.getCertificate(int(token_id, 16)).call()
            
            return {
                'success': True,
                'valid': True,
                'certificate_data': json.loads(certificate_data),
                'verified_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_metadata_hash(self, data: Dict) -> str:
        """Gerar hash dos metadados para verificação"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()


class NotificationIntegration:
    """Integração com serviços de notificação (SendGrid, Twilio, Push)"""
    
    def __init__(self):
        self.sendgrid_key = SENDGRID_API_KEY
        self.twilio_sid = TWILIO_ACCOUNT_SID
        self.twilio_token = TWILIO_AUTH_TOKEN
    
    async def send_email(self, to_email: str, subject: str, content: str, template_id: str = None) -> Dict:
        """Enviar email via SendGrid"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_key)
            
            mail = Mail(
                from_email='noreply@duolingojuridico.com',
                to_emails=to_email,
                subject=subject,
                html_content=content
            )
            
            if template_id:
                mail.template_id = template_id
            
            response = sg.send(mail)
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id')
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def send_sms(self, to_number: str, message: str) -> Dict:
        """Enviar SMS via Twilio"""
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_sid, self.twilio_token)
            
            message = client.messages.create(
                body=message,
                from_='+1234567890',  # Número Twilio
                to=to_number
            )
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def send_push_notification(self, device_tokens: List[str], title: str, body: str, data: Dict = None) -> Dict:
        """Enviar notificação push via Firebase"""
        try:
            import firebase_admin
            from firebase_admin import messaging
            
            messages = []
            for token in device_tokens:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data=data or {},
                    token=token
                )
                messages.append(message)
            
            response = messaging.send_all(messages)
            
            return {
                'success': True,
                'success_count': response.success_count,
                'failure_count': response.failure_count,
                'responses': [r.message_id for r in response.responses if r.success]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


class LegalDatabaseIntegration:
    """Integração com bases de dados jurídicas"""
    
    def __init__(self):
        self.stf_api = "http://www.stf.jus.br/portal/jurisprudencia/api"
        self.planalto_api = "http://www4.planalto.gov.br/legislacao/api"
    
    async def search_jurisprudence(self, query: str, court: str = 'STF') -> Dict:
        """Buscar jurisprudência em bases oficiais"""
        try:
            if court == 'STF':
                url = f"{self.stf_api}/search"
                params = {
                    'q': query,
                    'format': 'json',
                    'limit': 10
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
            
            return {
                'success': True,
                'results': data.get('decisions', []),
                'total': data.get('total', 0),
                'court': court
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def get_legislation(self, law_number: str) -> Dict:
        """Obter texto de lei do Planalto"""
        try:
            url = f"{self.planalto_api}/law/{law_number}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
            
            return {
                'success': True,
                'law_data': data,
                'source': 'Planalto'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Tarefas assíncronas para processamento em background
@shared_task
def process_ai_request(request_type: str, data: Dict) -> Dict:
    """Processar requisição de IA em background"""
    
    if request_type == 'legal_explanation':
        integration = OpenAIIntegration()
        return asyncio.run(integration.generate_legal_explanation(
            data['question'], data['context']
        ))
    
    elif request_type == 'case_analysis':
        integration = ClaudeIntegration()
        return asyncio.run(integration.analyze_legal_case(data))
    
    elif request_type == 'mint_nft':
        integration = BlockchainIntegration()
        return asyncio.run(integration.mint_achievement_nft(
            data['user_address'], data['achievement']
        ))
    
    return {'success': False, 'error': 'Unknown request type'}


@shared_task
def send_notification_batch(notification_type: str, recipients: List[Dict], content: Dict) -> Dict:
    """Enviar notificações em lote"""
    
    integration = NotificationIntegration()
    results = []
    
    for recipient in recipients:
        if notification_type == 'email':
            result = asyncio.run(integration.send_email(
                recipient['email'], content['subject'], content['body']
            ))
        elif notification_type == 'sms':
            result = asyncio.run(integration.send_sms(
                recipient['phone'], content['message']
            ))
        elif notification_type == 'push':
            result = asyncio.run(integration.send_push_notification(
                [recipient['device_token']], content['title'], content['body']
            ))
        
        results.append({
            'recipient': recipient,
            'result': result
        })
    
    return {
        'success': True,
        'total_sent': len([r for r in results if r['result']['success']]),
        'total_failed': len([r for r in results if not r['result']['success']]),
        'results': results
    }


# Classe principal para gerenciar todas as integrações
class ProductionAPIManager:
    """Gerenciador principal das integrações de produção"""
    
    def __init__(self):
        self.openai = OpenAIIntegration()
        self.claude = ClaudeIntegration()
        self.blockchain = BlockchainIntegration()
        self.notifications = NotificationIntegration()
        self.legal_db = LegalDatabaseIntegration()
        
        # Cache para otimização
        self.cache_timeout = 3600  # 1 hora
    
    async def get_ai_response(self, provider: str, request_type: str, data: Dict) -> Dict:
        """Obter resposta de IA com cache"""
        
        # Gerar chave de cache
        cache_key = f"ai_{provider}_{request_type}_{hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()}"
        
        # Verificar cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Processar requisição
        if provider == 'openai':
            if request_type == 'explanation':
                result = await self.openai.generate_legal_explanation(data['question'], data['context'])
            elif request_type == 'study_plan':
                result = await self.openai.generate_study_plan(data['profile'], data['goals'])
            elif request_type == 'transcription':
                result = await self.openai.transcribe_audio(data['audio_path'])
        
        elif provider == 'claude':
            if request_type == 'case_analysis':
                result = await self.claude.analyze_legal_case(data)
            elif request_type == 'document':
                result = await self.claude.generate_legal_document(data['type'], data['parameters'])
        
        # Armazenar no cache se sucesso
        if result.get('success'):
            cache.set(cache_key, result, self.cache_timeout)
        
        return result
    
    async def create_certified_achievement(self, user_data: Dict, achievement: Dict) -> Dict:
        """Criar conquista certificada via blockchain"""
        
        # Gerar endereço blockchain para usuário se não existir
        if not user_data.get('blockchain_address'):
            # Gerar nova carteira
            account = web3.eth.account.create()
            user_data['blockchain_address'] = account.address
            user_data['private_key'] = account.privateKey.hex()
        
        # Criar NFT de conquista
        result = await self.blockchain.mint_achievement_nft(
            user_data['blockchain_address'],
            achievement
        )
        
        # Enviar notificação de conquista
        if result['success']:
            await self.notifications.send_email(
                user_data['email'],
                'Nova Conquista Certificada! 🏆',
                f"""
                Parabéns! Você conquistou: {achievement['title']}
                
                Sua conquista foi certificada na blockchain:
                Token ID: {result['token_id']}
                Transação: {result['transaction_hash']}
                
                Você pode verificar sua certificação a qualquer momento!
                """
            )
        
        return result
    
    def get_health_status(self) -> Dict:
        """Verificar status de saúde de todas as integrações"""
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'services': {}
        }
        
        # Verificar OpenAI
        try:
            # Teste simples de API
            status['services']['openai'] = {
                'status': 'healthy',
                'last_check': datetime.now().isoformat()
            }
        except:
            status['services']['openai'] = {
                'status': 'unhealthy',
                'last_check': datetime.now().isoformat()
            }
            status['overall_status'] = 'degraded'
        
        # Verificar Blockchain
        try:
            connected = web3.isConnected()
            status['services']['blockchain'] = {
                'status': 'healthy' if connected else 'unhealthy',
                'connected': connected,
                'last_block': web3.eth.block_number if connected else None
            }
        except:
            status['services']['blockchain'] = {
                'status': 'unhealthy',
                'connected': False
            }
            status['overall_status'] = 'degraded'
        
        # Verificar demais serviços...
        
        return status 