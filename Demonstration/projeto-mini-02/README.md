# Projeto Mini 02 — Pré-processamento de Imagens para Inspeção de Peças Fundidas

Projeto de estudo em **Visão Computacional** que implementa um pipeline de pré-processamento de imagens para inspeção de qualidade de peças fundidas (*casting*), classificando-as em **defeituosas** (`def_front`) e **ok** (`ok_front`).

O pipeline aplica uma sequência clássica de técnicas de processamento de imagem com **OpenCV** — escala de cinza, desfoque, limiarização, morfologia e detecção de bordas — preparando as imagens para uma futura etapa de treinamento de um modelo de Machine Learning.

## 📂 Estrutura do projeto

```
projeto-mini-02/
├── raw_images/
│   ├── def_front/           # imagens de peças com defeito
│   └── ok_front/            # imagens de peças ok
├── src/
│   ├── prepocess.ipynb      # notebook com o pipeline de pré-processamento
│   └── processed_img/
│       ├── def_front_processed/
│       └── ok_front_processed/
└── .gitignore
```

## ⚙️ Pipeline de pré-processamento

A classe `Processor` (definida em `src/prepocess.ipynb`) executa, para cada imagem, as seguintes etapas:

1. **Leitura** da imagem original (`cv2.imread`)
2. **Conversão para escala de cinza**
3. **Desfoque Gaussiano** (`GaussianBlur`) para redução de ruído
4. **Limiarização** com Otsu (`THRESH_BINARY + THRESH_OTSU`), convertendo a imagem em preto e branco
5. **Operações morfológicas** (abertura + fechamento) para limpar pequenos ruídos e falhas
6. **Detecção de bordas** com o algoritmo **Canny**
7. **Redimensionamento** final para `256x256`, padronizando o tamanho de todas as imagens

Ao final, o notebook monta um **painel horizontal** com todas as etapas lado a lado (original → cinza → desfoque → binarização → morfologia → bordas → resultado final), facilitando a comparação visual do efeito de cada técnica, e salva o resultado em `processed_img/`.

O processamento em lote (`process_batch`) percorre uma pasta inteira de imagens, exibindo uma barra de progresso (`tqdm`) e reportando o tempo total e a quantidade de imagens processadas com sucesso.

## 🧰 Tecnologias utilizadas

- Python
- OpenCV (`opencv-python`)
- NumPy
- tqdm
- Jupyter Notebook

## 📊 Sobre os dados

As imagens estão organizadas em duas classes, seguindo a convenção comum de datasets de inspeção de peças fundidas:
- `def_front`: peças com defeito
- `ok_front`: peças aprovadas (sem defeito)

## ✍️ Autor

Projeto desenvolvido por **Delmar** ([@delmar-dev-one](https://github.com/delmar-dev-one)), como parte de seus estudos em Machine Learning e Computer Vision.
