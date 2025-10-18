#!/usr/bin/env python3
"""
Script para testar as correções nas regras problemáticas
"""

from app_space_version import predict_hate_speech

def test_corrections():
    """Testa as correções nas regras problemáticas"""
    
    # Casos de teste
    test_cases = [
        # Casos que NÃO devem ser HATE
        ("Que legal!!!!!", "NÃO devem ser HATE - Pontuação excessiva positiva"),
        ("Parabéns!!!!!", "NÃO devem ser HATE - Pontuação excessiva positiva"),
        ("Meu amor, seja o que você quiser serrrrrr! Seja feliz sempre!!!!!!!!", "NÃO devem ser HATE - Pontuação excessiva positiva"),
        ("Hahah", "NÃO devem ser HATE - Risada simples"),
        ("hahaha", "NÃO devem ser HATE - Risada simples"),
        ("Todes", "NÃO devem ser HATE - Linguagem neutra sozinha"),
        ("Meu bar sapatão favorito em SP", "NÃO devem ser HATE - Contexto positivo"),
        ("Amo a comunidade LGBTQIA+", "NÃO devem ser HATE - Contexto positivo"),
        
        # Casos que DEVEM ser HATE
        ("Viado do caralho!!!!!", "DEVEM ser HATE - Hate com pontuação excessiva"),
        ("Que porra de todes!!!!!", "DEVEM ser HATE - Hate à linguagem neutra"),
        ("Viado doente 😂😂😂", "DEVEM ser HATE - Hate com risada"),
        ("Que modinha todes", "DEVEM ser HATE - Hate à linguagem neutra"),
        ("Sapatão nojenta!!!!!", "DEVEM ser HATE - Hate com pontuação excessiva")
    ]
    
    print("🧪 Testando correções nas regras problemáticas...")
    print("=" * 60)
    
    for text, description in test_cases:
        result = predict_hate_speech(text)
        is_hate = result['is_hate']
        method = result['method']
        
        # Lógica de validação corrigida
        if "NÃO devem" in description:
            status = "✅ CORRETO" if not is_hate else "❌ INCORRETO"
        elif "DEVEM" in description:
            status = "✅ CORRETO" if is_hate else "❌ INCORRETO"
        else:
            status = "❓ INDEFINIDO"
        
        print(f"\n📝 Texto: {text}")
        print(f"📋 Descrição: {description}")
        print(f"🎯 Resultado: {'HATE' if is_hate else 'NÃO-HATE'}")
        print(f"🔧 Método: {method}")
        print(f"📊 Status: {status}")
        print("-" * 40)

if __name__ == "__main__":
    test_corrections()
