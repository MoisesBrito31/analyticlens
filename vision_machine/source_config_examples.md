# Configurações de Source de Imagem - Vision Machine

## 📁 Modo: Pasta (folder)

Para processar imagens de uma pasta local em fila cíclica:

```json
{
  "type": "pasta",
  "folder_path": "./images",
  "resolution": [640, 480],
  "fps": 1
}
```

**Características:**
- Lê imagens da pasta especificada
- Suporta: JPG, JPEG, PNG, BMP, TIFF
- Fila cíclica automática
- Útil para testes e processamento de lotes

## 📷 Modo: Câmera Local (camera)

Para câmeras USB ou integradas:

```json
{
  "type": "camera",
  "camera_id": 0,
  "resolution": [1280, 720],
  "fps": 30
}
```

**Características:**
- ID da câmera (0, 1, 2...)
- Resolução configurável
- FPS configurável
- Fallback automático se falhar

## 🌐 Modo: Câmera IP (camera_IP)

Para câmeras de rede via RTSP:

```json
{
  "type": "camera_IP",
  "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
  "resolution": [1920, 1080],
  "fps": 25
}
```

**Características:**
- URL RTSP completa
- Suporte a autenticação
- Buffer otimizado para rede
- Timeout configurável

## 🔄 Atualização via API

Para mudar o tipo de source em tempo real:

```bash
# Mudar para pasta
curl -X PUT http://localhost:5000/api/source_config \
  -H "Content-Type: application/json" \
  -d '{"type": "pasta", "folder_path": "./test_images"}'

# Mudar para câmera
curl -X PUT http://localhost:5000/api/source_config \
  -H "Content-Type: application/json" \
  -d '{"type": "camera", "camera_id": 1, "resolution": [640, 480]}'

# Mudar para RTSP
curl -X PUT http://localhost:5000/api/source_config \
  -H "Content-Type: application/json" \
  -d '{"type": "camera_IP", "rtsp_url": "rtsp://192.168.1.100/stream"}'
```

## ⚠️ Observações

1. **Pasta**: Cria automaticamente se não existir
2. **Câmera**: Fallback para câmera 0 se falhar
3. **RTSP**: Verifica conectividade antes de usar
4. **Transição**: Libera recursos antigos automaticamente
5. **Persistência**: Configurações são salvas automaticamente
