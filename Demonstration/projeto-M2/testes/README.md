# Testes complementares — AgroVisionAI

Este diretório contém `testes.ipynb`, um notebook complementar ao `AgroVisionAI_Modulo2_Final.ipynb`.

## O que ele executa
1. Gera/verifica `api.py` e inicializa a API com Uvicorn.
2. Consulta `/health` e testa `/classificar-folha` e `/detectar-fruto` com v8, v9 e v11.
3. Gera uma Collection Postman v2.1 com scripts de teste.
4. Compara bounding boxes previstas com as anotações YOLO reais, calculando TP, FP, FN, precisão, recall, F1 e IoU médio.
5. Executa validação Ultralytics para obter mAP50 e mAP50-95.

## Como usar
- Coloque a pasta `testes/` na raiz do projeto AgroVisionAI.
- Garanta que `models/` contenha `modelo_folhas.keras`, `classes.json`, `yolov8_best.pt`, `yolov9_best.pt` e `yolo11_best.pt`.
- Garanta que o dataset de frutos esteja disponível e que seu `data.yaml` esteja dentro da pasta do projeto.
- Abra `testes.ipynb` no Jupyter/VS Code e execute as células em ordem.
- Se necessário, ajuste `PROJECT_DIR`, `LEAF_IMAGE`, `FRUIT_IMAGE` e `DATA_YAML`.
- Importe `AgroVisionAI_Testes_Postman.json` no Postman e selecione os arquivos de imagem nos campos `file`.

## Evidências
Os relatórios são salvos em `results/` na raiz do projeto. Salve capturas reais do Swagger/Postman em `testes/evidencias/` após executar os testes.

**Nota:** este pacote não contém pesos treinados nem imagens do dataset. Ele não inventa resultados: as métricas e os status de teste serão produzidos no ambiente em que o projeto e seus artefatos estiverem instalados.
