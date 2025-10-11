#!/usr/bin/env python3
"""
API REST para detecção de discurso de ódio em produção
Usa Flask para criar endpoint de inferência
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
import re
from datetime import datetime
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Classe do detector (mesma do script de inferência)
class HateSpeechDetector:
    """Classe para detecção de discurso de ódio"""
    
    def __init__(self, model_path=None, threshold_path=None):
        """Inicializa o detector com modelo e threshold"""
        self.model = None
        self.threshold = 0.5
        self.model_path = model_path
        self.threshold_path = threshold_path
        
        # Carregar modelo e threshold se especificados
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        
        if threshold_path and os.path.exists(threshold_path):
            self.load_threshold(threshold_path)
    
    def load_model(self, model_path):
        """Carrega modelo treinado"""
        try:
            self.model = joblib.load(model_path)
            self.model_path = model_path
            logger.info(f"Modelo carregado: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False
    
    def load_threshold(self, threshold_path):
        """Carrega informações de threshold"""
        try:
            with open(threshold_path, 'r', encoding='utf-8') as f:
                threshold_info = json.load(f)
            self.threshold = threshold_info.get('threshold', 0.5)
            logger.info(f"Threshold carregado: {self.threshold:.2f}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar threshold: {e}")
            return False
    
    def normalize_text(self, text):
        """Normaliza texto para análise"""
        if pd.isna(text) or text == "":
            return ""
        
        # Converter para string e limpar
        text = str(text).strip()
        
        # Remover URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remover menções e hashtags
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Remover caracteres especiais excessivos
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def predict_single(self, text):
        """Prediz se um texto é discurso de ódio"""
        if not self.model:
            raise ValueError("Modelo não carregado")
        
        # Normalizar texto
        normalized_text = self.normalize_text(text)
        
        if len(normalized_text) < 3:
            return {
                'text': text,
                'normalized_text': normalized_text,
                'is_hate': 0,
                'hate_probability': 0.0,
                'confidence': 'low',
                'warning': 'Texto muito curto'
            }
        
        # Obter probabilidades
        probabilities = self.model.predict_proba([normalized_text])
        hate_probability = probabilities[0][1]
        
        # Aplicar threshold
        is_hate = 1 if hate_probability >= self.threshold else 0
        
        # Determinar confiança
        if hate_probability < 0.3:
            confidence = 'low'
        elif hate_probability > 0.7:
            confidence = 'high'
        else:
            confidence = 'medium'
        
        return {
            'text': text,
            'normalized_text': normalized_text,
            'is_hate': is_hate,
            'hate_probability': float(hate_probability),
            'confidence': confidence,
            'threshold_used': self.threshold
        }

# Inicializar detector global
detector = HateSpeechDetector(
    model_path='out/modelo_otimizado_20251010_150123.pkl',
    threshold_path='out/threshold_info_20251010_150123.json'
)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector.model is not None,
        'threshold': detector.threshold,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint para predição de discurso de ódio"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON não fornecidos'}), 400
        
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Campo "text" não fornecido'}), 400
        
        # Fazer predição
        result = detector.predict_single(text)
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    """Endpoint para predição em lote"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON não fornecidos'}), 400
        
        texts = data.get('texts')
        if not texts or not isinstance(texts, list):
            return jsonify({'error': 'Campo "texts" deve ser uma lista'}), 400
        
        if len(texts) > 100:  # Limite de segurança
            return jsonify({'error': 'Máximo de 100 textos por lote'}), 400
        
        # Fazer predições
        results = []
        for text in texts:
            try:
                result = detector.predict_single(text)
                results.append(result)
            except Exception as e:
                results.append({
                    'text': text,
                    'error': str(e),
                    'is_hate': 0,
                    'hate_probability': 0.0
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na predição em lote: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Endpoint para estatísticas do modelo"""
    try:
        return jsonify({
            'success': True,
            'stats': {
                'model_loaded': detector.model is not None,
                'threshold': detector.threshold,
                'model_path': detector.model_path,
                'threshold_path': detector.threshold_path,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Endpoint raiz com informações da API"""
    return jsonify({
        'name': 'Hate Speech Detection API',
        'version': '1.0.0',
        'description': 'API para detecção de discurso de ódio em português',
        'endpoints': {
            'GET /': 'Informações da API',
            'GET /health': 'Health check',
            'POST /predict': 'Predição de texto único',
            'POST /predict_batch': 'Predição em lote',
            'GET /stats': 'Estatísticas do modelo'
        },
        'example_usage': {
            'single_prediction': {
                'method': 'POST',
                'endpoint': '/predict',
                'body': {'text': 'Você é um idiota'}
            },
            'batch_prediction': {
                'method': 'POST',
                'endpoint': '/predict_batch',
                'body': {'texts': ['Olá mundo', 'Vai se foder']}
            }
        }
    })

if __name__ == '__main__':
    # Verificar se modelo foi carregado
    if not detector.model:
        logger.error("Modelo não pôde ser carregado. Encerrando...")
        exit(1)
    
    logger.info("🚀 Iniciando API de detecção de discurso de ódio...")
    logger.info(f"📊 Modelo: {detector.model_path}")
    logger.info(f"🎯 Threshold: {detector.threshold:.2f}")
    
    # Executar Flask
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        threaded=True
    )
