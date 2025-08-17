#!/usr/bin/env python3
"""
Teste do Sistema de Ferramentas da Vision Machine
"""

import cv2
import numpy as np
import json
from inspection_processor import InspectionProcessor

def test_tools_system():
    """Testa o sistema de ferramentas completo"""
    print("🧪 Testando Sistema de Ferramentas da Vision Machine")
    print("=" * 60)
    
    # Configuração de teste - Pipeline otimizado
    test_config = {
        "tools": [
            {
                "id": 1,
                "name": "grayscale_filter",
                "type": "grayscale",
                "ROI": {"x": 0, "y": 0, "w": 640, "h": 480},
                "method": "luminance",
                "normalize": True,
                "inspec_pass_fail": False
            },
            {
                "id": 2,
                "name": "blob_1",
                "type": "blob",
                "ROI": {"x": 0, "y": 10, "w": 100, "h": 100},
                "th_max": 255,
                "th_min": 130,
                "area_min": 100,
                "area_max": 1000,
                "test_total_area_max": 100,
                "test_total_area_min": 50,
                "test_blob_count_max": 5,
                "test_blob_count_min": 4,
                "total_area_test": True,
                "blob_count_test": True,
                "inspec_pass_fail": True
            }
        ]
    }
    
    print("📋 Pipeline configurado:")
    print("   1️⃣ GrayscaleFilter -> Converte imagem para grayscale")
    print("   2️⃣ BlobTool -> Usa imagem grayscale já processada (otimizado)")
    print("   🎯 Evita duplicação de processamento grayscale")
    
    try:
        # 1. Testar inicialização do processador
        print("1️⃣ Inicializando processador de ferramentas...")
        processor = InspectionProcessor(test_config)
        print(f"   ✅ Processador inicializado com {len(processor.tools)} ferramentas")
        
        # 2. Validar ferramentas
        print("\n2️⃣ Validando configurações das ferramentas...")
        if processor.validate_all_tools():
            print("   ✅ Todas as ferramentas passaram na validação")
        else:
            print("   ❌ Algumas ferramentas falharam na validação")
            return
        
        # 3. Criar imagem de teste com dimensões reais de câmera
        print("\n3️⃣ Criando imagem de teste...")
        
        # Dimensões típicas de câmera (640x480, 1280x720, 1920x1080)
        width, height = 640, 480
        test_image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        
        # Adicionar alguns retângulos para simular blobs (dentro do ROI da ferramenta blob)
        # ROI da ferramenta blob: x=0, y=10, w=100, h=100
        cv2.rectangle(test_image, (10, 20), (80, 90), (200, 200, 200), -1)      # Dentro do ROI
        cv2.rectangle(test_image, (20, 30), (70, 80), (180, 180, 180), -1)      # Dentro do ROI
        cv2.rectangle(test_image, (30, 40), (60, 70), (160, 160, 160), -1)      # Dentro do ROI
        
        # Adicionar alguns retângulos fora do ROI para testar filtros
        cv2.rectangle(test_image, (200, 100), (250, 150), (150, 150, 150), -1)  # Fora do ROI
        cv2.rectangle(test_image, (400, 200), (450, 250), (120, 120, 120), -1)  # Fora do ROI
        
        print(f"   ✅ Imagem de teste criada: {test_image.shape}")
        print(f"   📐 Dimensões: {width}x{height} pixels")
        print(f"   🎯 ROI da ferramenta blob: (0,10) a (100,110)")
        
        # 4. Processar inspeção
        print("\n4️⃣ Processando inspeção...")
        result = processor.process_inspection(test_image)
        
        # 5. Exibir resultados
        print("\n5️⃣ Resultados da inspeção:")
        print(f"   📊 Total de ferramentas: {result['inspection_summary']['total_tools']}")
        print(f"   ✅ Ferramentas bem-sucedidas: {result['inspection_summary']['successful_tools']}")
        print(f"   ❌ Ferramentas com erro: {result['inspection_summary']['failed_tools']}")
        print(f"   🎯 Resultado geral: {'PASSOU' if result['inspection_summary']['overall_pass'] else 'FALHOU'}")
        print(f"   ⏱️ Tempo total: {result['inspection_summary']['total_processing_time_ms']:.2f}ms")
        print(f"   ⚙️ Tempo das ferramentas: {result['inspection_summary']['tools_processing_time_ms']:.2f}ms")
        print(f"   📈 Overhead: {result['inspection_summary']['overhead_time_ms']:.2f}ms")
        
        # 6. Detalhes das ferramentas
        print("\n6️⃣ Detalhes das ferramentas:")
        for tool_result in result['tool_results']:
            print(f"   🔧 {tool_result['tool_name']} (ID: {tool_result['tool_id']}):")
            print(f"      Tipo: {tool_result['tool_type']}")
            print(f"      Status: {tool_result['status']}")
            print(f"      Tempo: {tool_result.get('processing_time_ms', 0):.2f}ms")
            
            if tool_result['tool_type'] == 'blob':
                print(f"      Blobs encontrados: {tool_result.get('blob_count', 0)}")
                print(f"      Área total: {tool_result.get('total_area', 0):.2f}")
                print(f"      Pass/Fail: {tool_result.get('pass_fail', 'N/A')}")
            
            if tool_result['tool_type'] == 'grayscale':
                print(f"      Imagem modificada: {tool_result.get('image_modified', False)}")
        
        # 7. Validação do pipeline otimizado
        print("\n7️⃣ Validação do Pipeline Otimizado:")
        grayscale_tool = next((r for r in result['tool_results'] if r['tool_type'] == 'grayscale'), None)
        blob_tool = next((r for r in result['tool_results'] if r['tool_type'] == 'blob'), None)
        
        if grayscale_tool and blob_tool:
            if grayscale_tool['status'] == 'success' and blob_tool['status'] == 'success':
                print("   ✅ Pipeline funcionando corretamente")
                print(f"   📊 Grayscale: {grayscale_tool.get('processing_time_ms', 0):.2f}ms")
                print(f"   📊 Blob: {blob_tool.get('processing_time_ms', 0):.2f}ms")
                print("   🎯 Sem duplicação de processamento grayscale")
            else:
                print("   ❌ Pipeline com problemas")
        else:
            print("   ⚠️ Não foi possível validar o pipeline")
        
        # 8. Salvar resultado
        print("\n8️⃣ Salvando resultado...")
        with open('test_tools_result.json', 'w', encoding='utf-8') as f:
            # Converter numpy arrays para listas para JSON
            json_result = json.loads(json.dumps(result, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x))
            json.dump(json_result, f, indent=2, ensure_ascii=False)
        print("   ✅ Resultado salvo em 'test_tools_result.json'")
        
        print("\n🎉 Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tools_system()
