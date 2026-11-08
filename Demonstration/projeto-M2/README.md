# AgroVisionAI — Módulo 2

Entrega corrigida baseada no notebook `modelo_m2_final`.

## Estrutura

- `model(1)(1).ipynb`: notebook com CNN, EDA, divisão estratificada, avaliação e pipeline de treino/validação dos três YOLO.
- `api.py`: API REST com `/classificar-folha`, `/detectar-fruto?modelo=v8|v9|v11` e `/health`.
- `AgroVisionAI_Postman_Collection.json`: coleção importável no Postman.
- `requirements.txt`: dependências.
- `models/`: diretório para artefatos treinados.
- `results/`: diretório para métricas e gráficos.

## Execução no Google Colab

1. Abra o notebook no Colab e execute as células iniciais para montar/baixar PlantVillage.
2. Execute a seção **Correções finais e avaliação independente** para criar os conjuntos treino/validação/teste e treinar/avaliar a CNN final.
3. Configure a chave do Roboflow em `os.environ["ROBOFLOW_API_KEY"]` ou nos Secrets do Colab. Não coloque a chave diretamente no notebook.
4. Baixe a versão do dataset de frutos em formato **YOLOv8 (detecção axis-aligned)**, não `yolov8-obb`.
5. Execute o treinamento dos três modelos na seção **YOLO de frutos**. O notebook salva `best.pt` em `models/` e métricas em `results/`.
6. Baixe `models/` e coloque-a ao lado de `api.py`.

## Execução local da API

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000
```

Abra `http://127.0.0.1:8000/docs` para conferir o Swagger.

## Testes no Postman

Importe `AgroVisionAI_Postman_Collection.json`, selecione arquivos de imagem nos campos `file` e execute:
- `GET /health`
- `POST /classificar-folha`
- `POST /detectar-fruto?modelo=v8` (repita para `v9` e `v11`)

Um endpoint de detecção retorna HTTP 503 se o peso daquela versão ainda não estiver treinado/salvo. Isso é intencional: a API não usa pesos genéricos como se fossem modelos ajustados no dataset de frutos.

## Notas metodológicas

- A CNN original do notebook foi avaliada no conjunto chamado validação. A seção final cria uma divisão estratificada independente de treino/validação/teste para que as métricas finais de teste não sejam confundidas com validação.
- O notebook anterior gerava bounding boxes de lesões com threshold/contornos. Isso não constitui ground truth confiável para detecção de frutos e foi substituído pelo dataset de frutos anotado.
- Treinamento YOLO depende de GPU/tempo de execução e acesso ao dataset Roboflow. Os resultados só devem ser reportados depois de executar as células e conferir os arquivos/métricas gerados.
- A chave Roboflow anteriormente embutida no notebook deve ser revogada e substituída por uma nova, armazenada como segredo/variável de ambiente.


## Trello / Kanban

https://trello.com/invite/b/6ae4db736f31182afd15c6ea/ATTI18ddd5b76ad744fe50fcefd4282f62b0992F5156/projeto-final

https://trello.com/invite/b/6ae4db736f31182afd15c6ea/ATTI18ddd5b76ad744fe50fcefd4282f62b0992F5156/projeto-final