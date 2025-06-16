"""
Sistema Blockchain para Certificados NFT - Duolingo Jurídico
Criação, validação e gestão de certificados e conquistas como NFTs
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import secrets
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class CertificateType(Enum):
    COURSE_COMPLETION = "course_completion"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    SKILL_MASTERY = "skill_mastery"
    COMPETITION_WIN = "competition_win"
    PROFESSIONAL_CERT = "professional_cert"

class ContractStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

@dataclass
class BlockchainTransaction:
    """Transação na blockchain"""
    id: str
    from_address: str
    to_address: str
    data: Dict[str, Any]
    timestamp: datetime
    signature: str
    hash: str
    block_number: int
    gas_used: int
    transaction_fee: float

@dataclass
class NFTMetadata:
    """Metadados do NFT"""
    name: str
    description: str
    image: str
    attributes: List[Dict[str, Any]]
    external_url: str
    animation_url: Optional[str]
    properties: Dict[str, Any]

@dataclass
class LegalCertificate:
    """Certificado jurídico digital"""
    id: str
    user_id: str
    certificate_type: CertificateType
    title: str
    description: str
    issuer: str
    issue_date: datetime
    expiry_date: Optional[datetime]
    metadata: NFTMetadata
    blockchain_hash: str
    smart_contract_address: str
    token_id: str
    verification_code: str
    is_transferable: bool
    is_revocable: bool

class CryptographyManager:
    """Gerenciador de criptografia avançada"""
    
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
    
    def generate_key_pair(self) -> Tuple[str, str]:
        """Gera par de chaves pública/privada"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode(), public_pem.decode()
    
    def sign_data(self, data: str, private_key_pem: str) -> str:
        """Assina dados com chave privada"""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        
        signature = private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode()
    
    def verify_signature(self, data: str, signature: str, public_key_pem: str) -> bool:
        """Verifica assinatura com chave pública"""
        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode())
            signature_bytes = base64.b64decode(signature.encode())
            
            public_key.verify(
                signature_bytes,
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def encrypt_data(self, data: str, public_key_pem: str) -> str:
        """Criptografa dados com chave pública"""
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        
        encrypted = public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str, private_key_pem: str) -> str:
        """Descriptografa dados com chave privada"""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted.decode()
    
    def generate_symmetric_key(self) -> str:
        """Gera chave simétrica para criptografia AES"""
        return base64.b64encode(secrets.token_bytes(32)).decode()
    
    def encrypt_symmetric(self, data: str, key: str) -> str:
        """Criptografia simétrica AES"""
        key_bytes = base64.b64decode(key.encode())
        iv = secrets.token_bytes(16)
        
        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Padding PKCS7
        data_bytes = data.encode()
        padding_length = 16 - (len(data_bytes) % 16)
        padded_data = data_bytes + bytes([padding_length] * padding_length)
        
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        return base64.b64encode(iv + encrypted).decode()
    
    def decrypt_symmetric(self, encrypted_data: str, key: str) -> str:
        """Descriptografia simétrica AES"""
        key_bytes = base64.b64decode(key.encode())
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        
        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        padding_length = decrypted_padded[-1]
        decrypted = decrypted_padded[:-padding_length]
        
        return decrypted.decode()

class SmartContractManager:
    """Gerenciador de contratos inteligentes"""
    
    def __init__(self):
        self.crypto_manager = CryptographyManager()
        self.contracts: Dict[str, Dict] = {}
    
    def create_certificate_contract(self, 
                                  certificate: LegalCertificate,
                                  terms: Dict[str, Any]) -> str:
        """Cria contrato inteligente para certificado"""
        
        contract_id = f"cert_contract_{secrets.token_hex(16)}"
        
        contract_code = {
            'version': '1.0',
            'type': 'certificate_issuance',
            'certificate_id': certificate.id,
            'user_id': certificate.user_id,
            'issuer': certificate.issuer,
            'terms': terms,
            'conditions': {
                'transferable': certificate.is_transferable,
                'revocable': certificate.is_revocable,
                'expiry_date': certificate.expiry_date.isoformat() if certificate.expiry_date else None,
                'minimum_score': terms.get('minimum_score', 0),
                'required_achievements': terms.get('required_achievements', []),
                'validity_period_days': terms.get('validity_period_days', 365)
            },
            'functions': {
                'verify_ownership': self._generate_ownership_verification_code(),
                'transfer_certificate': self._generate_transfer_code(),
                'revoke_certificate': self._generate_revocation_code(),
                'validate_certificate': self._generate_validation_code()
            },
            'events': [],
            'created_at': datetime.now().isoformat(),
            'status': ContractStatus.PENDING.value
        }
        
        # Assina o contrato
        contract_json = json.dumps(contract_code, sort_keys=True)
        private_key, _ = self.crypto_manager.generate_key_pair()
        signature = self.crypto_manager.sign_data(contract_json, private_key)
        
        contract_code['signature'] = signature
        contract_code['hash'] = hashlib.sha256(contract_json.encode()).hexdigest()
        
        self.contracts[contract_id] = contract_code
        
        return contract_id
    
    def execute_contract_function(self, 
                                 contract_id: str, 
                                 function_name: str, 
                                 parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Executa função do contrato inteligente"""
        
        if contract_id not in self.contracts:
            return {'success': False, 'error': 'Contract not found'}
        
        contract = self.contracts[contract_id]
        
        if function_name not in contract['functions']:
            return {'success': False, 'error': 'Function not found'}
        
        # Executa função baseada no nome
        if function_name == 'verify_ownership':
            return self._verify_ownership(contract, parameters)
        elif function_name == 'transfer_certificate':
            return self._transfer_certificate(contract, parameters)
        elif function_name == 'revoke_certificate':
            return self._revoke_certificate(contract, parameters)
        elif function_name == 'validate_certificate':
            return self._validate_certificate(contract, parameters)
        
        return {'success': False, 'error': 'Unknown function'}
    
    def _generate_ownership_verification_code(self) -> str:
        """Gera código para verificação de propriedade"""
        return f"""
        function verify_ownership(certificate_id, user_signature) {{
            const certificate = getCertificate(certificate_id);
            const user_public_key = getUserPublicKey(certificate.user_id);
            
            if (verifySignature(certificate_id, user_signature, user_public_key)) {{
                return {{
                    valid: true,
                    owner: certificate.user_id,
                    verified_at: getCurrentTimestamp()
                }};
            }}
            
            return {{ valid: false, error: 'Invalid signature' }};
        }}
        """
    
    def _generate_transfer_code(self) -> str:
        """Gera código para transferência"""
        return f"""
        function transfer_certificate(certificate_id, from_user, to_user, authorization) {{
            const certificate = getCertificate(certificate_id);
            
            if (!certificate.conditions.transferable) {{
                return {{ success: false, error: 'Certificate not transferable' }};
            }}
            
            if (certificate.user_id !== from_user) {{
                return {{ success: false, error: 'Unauthorized transfer' }};
            }}
            
            if (verifyTransferAuthorization(authorization, from_user)) {{
                certificate.user_id = to_user;
                certificate.transfer_history.push({{
                    from: from_user,
                    to: to_user,
                    timestamp: getCurrentTimestamp(),
                    authorization: authorization
                }});
                
                return {{ success: true, new_owner: to_user }};
            }}
            
            return {{ success: false, error: 'Invalid authorization' }};
        }}
        """
    
    def _generate_revocation_code(self) -> str:
        """Gera código para revogação"""
        return f"""
        function revoke_certificate(certificate_id, issuer_signature) {{
            const certificate = getCertificate(certificate_id);
            
            if (!certificate.conditions.revocable) {{
                return {{ success: false, error: 'Certificate not revocable' }};
            }}
            
            const issuer_public_key = getIssuerPublicKey(certificate.issuer);
            
            if (verifySignature(certificate_id + 'REVOKE', issuer_signature, issuer_public_key)) {{
                certificate.status = 'REVOKED';
                certificate.revoked_at = getCurrentTimestamp();
                certificate.revoked_by = certificate.issuer;
                
                return {{ success: true, revoked_at: certificate.revoked_at }};
            }}
            
            return {{ success: false, error: 'Unauthorized revocation' }};
        }}
        """
    
    def _generate_validation_code(self) -> str:
        """Gera código para validação"""
        return f"""
        function validate_certificate(certificate_id, validation_time) {{
            const certificate = getCertificate(certificate_id);
            const current_time = validation_time || getCurrentTimestamp();
            
            if (certificate.status === 'REVOKED') {{
                return {{ valid: false, reason: 'Certificate revoked' }};
            }}
            
            if (certificate.conditions.expiry_date && 
                current_time > certificate.conditions.expiry_date) {{
                return {{ valid: false, reason: 'Certificate expired' }};
            }}
            
            const signature_valid = verifyContractSignature(certificate);
            
            return {{
                valid: signature_valid,
                certificate_id: certificate_id,
                owner: certificate.user_id,
                issuer: certificate.issuer,
                issue_date: certificate.created_at,
                expiry_date: certificate.conditions.expiry_date,
                validated_at: current_time
            }};
        }}
        """
    
    def _verify_ownership(self, contract: Dict, parameters: Dict) -> Dict[str, Any]:
        """Implementa verificação de propriedade"""
        certificate_id = parameters.get('certificate_id')
        user_signature = parameters.get('user_signature')
        
        if not certificate_id or not user_signature:
            return {'success': False, 'error': 'Missing parameters'}
        
        # Simula verificação (em produção, usar blockchain real)
        return {
            'success': True,
            'valid': True,
            'owner': contract['user_id'],
            'verified_at': datetime.now().isoformat()
        }
    
    def _transfer_certificate(self, contract: Dict, parameters: Dict) -> Dict[str, Any]:
        """Implementa transferência de certificado"""
        if not contract['conditions']['transferable']:
            return {'success': False, 'error': 'Certificate not transferable'}
        
        from_user = parameters.get('from_user')
        to_user = parameters.get('to_user')
        authorization = parameters.get('authorization')
        
        if not all([from_user, to_user, authorization]):
            return {'success': False, 'error': 'Missing parameters'}
        
        # Atualiza contrato
        contract['user_id'] = to_user
        contract['events'].append({
            'type': 'transfer',
            'from': from_user,
            'to': to_user,
            'timestamp': datetime.now().isoformat()
        })
        
        return {'success': True, 'new_owner': to_user}
    
    def _revoke_certificate(self, contract: Dict, parameters: Dict) -> Dict[str, Any]:
        """Implementa revogação de certificado"""
        if not contract['conditions']['revocable']:
            return {'success': False, 'error': 'Certificate not revocable'}
        
        issuer_signature = parameters.get('issuer_signature')
        
        if not issuer_signature:
            return {'success': False, 'error': 'Missing issuer signature'}
        
        # Revoga certificado
        contract['status'] = ContractStatus.CANCELLED.value
        contract['events'].append({
            'type': 'revocation',
            'issuer': contract['issuer'],
            'timestamp': datetime.now().isoformat()
        })
        
        return {'success': True, 'revoked_at': datetime.now().isoformat()}
    
    def _validate_certificate(self, contract: Dict, parameters: Dict) -> Dict[str, Any]:
        """Implementa validação de certificado"""
        validation_time = parameters.get('validation_time', datetime.now())
        
        if isinstance(validation_time, str):
            validation_time = datetime.fromisoformat(validation_time)
        
        # Verifica status
        if contract['status'] == ContractStatus.CANCELLED.value:
            return {'valid': False, 'reason': 'Certificate revoked'}
        
        # Verifica expiração
        expiry_date = contract['conditions'].get('expiry_date')
        if expiry_date:
            expiry_date = datetime.fromisoformat(expiry_date)
            if validation_time > expiry_date:
                return {'valid': False, 'reason': 'Certificate expired'}
        
        return {
            'valid': True,
            'certificate_id': contract['certificate_id'],
            'owner': contract['user_id'],
            'issuer': contract['issuer'],
            'validated_at': validation_time.isoformat()
        }

class NFTCertificateManager:
    """Gerenciador de certificados NFT"""
    
    def __init__(self):
        self.crypto_manager = CryptographyManager()
        self.contract_manager = SmartContractManager()
        self.certificates: Dict[str, LegalCertificate] = {}
    
    def create_certificate(self,
                          user_id: str,
                          certificate_type: CertificateType,
                          title: str,
                          description: str,
                          achievement_data: Dict[str, Any],
                          validity_days: int = 365) -> LegalCertificate:
        """Cria novo certificado NFT"""
        
        certificate_id = f"cert_{secrets.token_hex(16)}"
        issue_date = datetime.now()
        expiry_date = issue_date + timedelta(days=validity_days) if validity_days > 0 else None
        
        # Cria metadados NFT
        metadata = NFTMetadata(
            name=f"{title} - Duolingo Jurídico",
            description=description,
            image=f"https://certificates.duolingojuridico.com/{certificate_id}.png",
            attributes=[
                {"trait_type": "Certificate Type", "value": certificate_type.value},
                {"trait_type": "Issuer", "value": "Duolingo Jurídico"},
                {"trait_type": "Issue Date", "value": issue_date.strftime("%Y-%m-%d")},
                {"trait_type": "User Level", "value": achievement_data.get("user_level", "Iniciante")},
                {"trait_type": "Score", "value": achievement_data.get("score", 0)},
                {"trait_type": "Rarity", "value": self._calculate_rarity(achievement_data)}
            ],
            external_url=f"https://duolingojuridico.com/certificate/{certificate_id}",
            animation_url=f"https://certificates.duolingojuridico.com/{certificate_id}.mp4",
            properties={
                "certificate_id": certificate_id,
                "blockchain_network": "Polygon",
                "smart_contract_version": "1.0",
                "achievement_data": achievement_data
            }
        )
        
        # Gera código de verificação
        verification_code = self._generate_verification_code(certificate_id, user_id)
        
        # Calcula hash da blockchain (simulado)
        blockchain_hash = self._calculate_blockchain_hash(certificate_id, metadata, verification_code)
        
        certificate = LegalCertificate(
            id=certificate_id,
            user_id=user_id,
            certificate_type=certificate_type,
            title=title,
            description=description,
            issuer="Duolingo Jurídico",
            issue_date=issue_date,
            expiry_date=expiry_date,
            metadata=metadata,
            blockchain_hash=blockchain_hash,
            smart_contract_address=f"0x{secrets.token_hex(20)}",
            token_id=str(int(time.time() * 1000)),  # Unix timestamp em ms
            verification_code=verification_code,
            is_transferable=certificate_type in [CertificateType.PROFESSIONAL_CERT, CertificateType.COMPETITION_WIN],
            is_revocable=True
        )
        
        # Cria contrato inteligente
        contract_terms = {
            'minimum_score': achievement_data.get('minimum_score', 70),
            'required_achievements': achievement_data.get('required_achievements', []),
            'validity_period_days': validity_days
        }
        
        contract_id = self.contract_manager.create_certificate_contract(certificate, contract_terms)
        
        # Armazena certificado
        self.certificates[certificate_id] = certificate
        
        # Cache por 24 horas
        cache.set(f"certificate:{certificate_id}", asdict(certificate), 86400)
        
        return certificate
    
    def verify_certificate(self, certificate_id: str, verification_code: str = None) -> Dict[str, Any]:
        """Verifica autenticidade do certificado"""
        
        certificate = self.certificates.get(certificate_id)
        if not certificate:
            # Tenta buscar no cache
            cached_cert = cache.get(f"certificate:{certificate_id}")
            if cached_cert:
                certificate = LegalCertificate(**cached_cert)
            else:
                return {'valid': False, 'error': 'Certificate not found'}
        
        # Verificação básica
        if verification_code and certificate.verification_code != verification_code:
            return {'valid': False, 'error': 'Invalid verification code'}
        
        # Verifica expiração
        if certificate.expiry_date and datetime.now() > certificate.expiry_date:
            return {'valid': False, 'error': 'Certificate expired'}
        
        # Verifica hash da blockchain
        expected_hash = self._calculate_blockchain_hash(
            certificate.id, 
            certificate.metadata, 
            certificate.verification_code
        )
        
        if certificate.blockchain_hash != expected_hash:
            return {'valid': False, 'error': 'Blockchain verification failed'}
        
        return {
            'valid': True,
            'certificate': asdict(certificate),
            'verified_at': datetime.now().isoformat(),
            'blockchain_confirmed': True
        }
    
    def get_user_certificates(self, user_id: str) -> List[LegalCertificate]:
        """Obtém todos os certificados de um usuário"""
        user_certs = []
        
        for cert in self.certificates.values():
            if cert.user_id == user_id:
                user_certs.append(cert)
        
        # Ordena por data de emissão (mais recente primeiro)
        return sorted(user_certs, key=lambda x: x.issue_date, reverse=True)
    
    def generate_certificate_image(self, certificate: LegalCertificate) -> str:
        """Gera imagem do certificado (retorna URL simulada)"""
        # Em produção, usar biblioteca de geração de imagens
        return f"https://certificates.duolingojuridico.com/{certificate.id}.png"
    
    def generate_certificate_metadata_json(self, certificate: LegalCertificate) -> str:
        """Gera JSON de metadados para NFT"""
        return json.dumps(asdict(certificate.metadata), indent=2, ensure_ascii=False)
    
    def _calculate_rarity(self, achievement_data: Dict[str, Any]) -> str:
        """Calcula raridade do certificado baseado nos dados de conquista"""
        score = achievement_data.get('score', 0)
        completion_time = achievement_data.get('completion_time_days', 0)
        perfect_streak = achievement_data.get('perfect_streak', 0)
        
        rarity_score = score + (perfect_streak * 10)
        
        if completion_time > 0:
            rarity_score += max(0, 100 - completion_time)  # Bonus por completar rapidamente
        
        if rarity_score >= 300:
            return "Legendary"
        elif rarity_score >= 200:
            return "Epic"
        elif rarity_score >= 100:
            return "Rare"
        elif rarity_score >= 50:
            return "Uncommon"
        else:
            return "Common"
    
    def _generate_verification_code(self, certificate_id: str, user_id: str) -> str:
        """Gera código de verificação único"""
        data = f"{certificate_id}:{user_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    
    def _calculate_blockchain_hash(self, certificate_id: str, metadata: NFTMetadata, verification_code: str) -> str:
        """Calcula hash para verificação na blockchain"""
        data = f"{certificate_id}:{asdict(metadata)}:{verification_code}"
        return hashlib.sha256(data.encode()).hexdigest()

class DocumentVerificationSystem:
    """Sistema de verificação de documentos legais"""
    
    def __init__(self):
        self.crypto_manager = CryptographyManager()
        self.verified_documents: Dict[str, Dict] = {}
    
    def verify_legal_document(self, 
                            document_content: str,
                            document_type: str,
                            digital_signature: str = None) -> Dict[str, Any]:
        """Verifica autenticidade de documento legal"""
        
        document_id = hashlib.sha256(document_content.encode()).hexdigest()
        
        verification_result = {
            'document_id': document_id,
            'document_type': document_type,
            'content_hash': document_id,
            'verified_at': datetime.now().isoformat(),
            'integrity_check': True,
            'signature_valid': False,
            'authenticity_score': 0.0,
            'issues_found': [],
            'recommendations': []
        }
        
        # Verifica integridade do conteúdo
        if not document_content.strip():
            verification_result['integrity_check'] = False
            verification_result['issues_found'].append("Document content is empty")
        
        # Verifica assinatura digital se fornecida
        if digital_signature:
            # Simulação de verificação de assinatura
            verification_result['signature_valid'] = len(digital_signature) > 50
        
        # Análise de autenticidade baseada no conteúdo
        authenticity_score = self._analyze_document_authenticity(document_content, document_type)
        verification_result['authenticity_score'] = authenticity_score
        
        # Gera recomendações
        if authenticity_score < 70:
            verification_result['recommendations'].append("Consider additional verification steps")
        
        if not digital_signature:
            verification_result['recommendations'].append("Add digital signature for enhanced security")
        
        # Armazena resultado
        self.verified_documents[document_id] = verification_result
        
        return verification_result
    
    def _analyze_document_authenticity(self, content: str, doc_type: str) -> float:
        """Analisa autenticidade do documento baseado no conteúdo"""
        score = 50.0  # Score base
        
        # Verifica elementos esperados por tipo de documento
        if doc_type == 'contract':
            if 'contrato' in content.lower():
                score += 10
            if 'cláusula' in content.lower():
                score += 10
            if 'parte' in content.lower():
                score += 5
        elif doc_type == 'legal_opinion':
            if 'parecer' in content.lower():
                score += 10
            if 'fundamento' in content.lower():
                score += 10
            if 'jurisprudência' in content.lower():
                score += 5
        elif doc_type == 'sentence':
            if 'sentença' in content.lower():
                score += 10
            if 'decide' in content.lower():
                score += 10
            if 'processo' in content.lower():
                score += 5
        
        # Verifica formatação legal típica
        if 'art.' in content.lower() or 'artigo' in content.lower():
            score += 5
        
        if 'lei' in content.lower():
            score += 5
        
        # Verifica estrutura formal
        if len(content) > 100:
            score += 10
        
        if content.count('.') > 5:  # Múltiplas sentenças
            score += 5
        
        return min(100.0, score)

# Instâncias globais
crypto_manager = CryptographyManager()
smart_contract_manager = SmartContractManager()
nft_certificate_manager = NFTCertificateManager()
document_verification_system = DocumentVerificationSystem()

# Funções de utilidade
def create_course_completion_certificate(user_id: str, course_name: str, score: int) -> LegalCertificate:
    """Cria certificado de conclusão de curso"""
    return nft_certificate_manager.create_certificate(
        user_id=user_id,
        certificate_type=CertificateType.COURSE_COMPLETION,
        title=f"Certificado de Conclusão - {course_name}",
        description=f"Certificado de conclusão do curso {course_name} com aproveitamento de {score}%",
        achievement_data={
            'course_name': course_name,
            'score': score,
            'completion_date': datetime.now().isoformat()
        }
    )

def verify_certificate_by_code(certificate_id: str, verification_code: str) -> Dict[str, Any]:
    """Verificação rápida de certificado por código"""
    return nft_certificate_manager.verify_certificate(certificate_id, verification_code)

def get_user_certificate_collection(user_id: str) -> List[Dict[str, Any]]:
    """Obtém coleção completa de certificados do usuário"""
    certificates = nft_certificate_manager.get_user_certificates(user_id)
    return [asdict(cert) for cert in certificates] 