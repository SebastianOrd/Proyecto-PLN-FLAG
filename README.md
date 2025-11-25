# Generación automática de resúmenes en lenguaje sencillo en salud

Este repositorio contiene el código, datos y documentación del artículo de tesis de maestría "Generación automática de resúmenes en lenguaje sencillo en salud".

El objetivo central es cerrar la brecha de comprensión en salud mediante la automatización eficiente de la generación de textos accesibles, validando la viabilidad de modelos de bajo costo computacional.

Resumen del Proyecto
La alfabetización en salud (\textit{Health Literacy}) es un desafío global, impactando negativamente la comprensión de tratamientos y la toma de decisiones informadas. La producción manual de Resúmenes en Lenguaje Sencillo (PLS) es costosa e inescalable.

Este proyecto aborda el problema mediante un pipeline integral de dos etapas:

Clasificación: Discriminación automática entre textos científicos y PLS.

Generación de PLS: Ajuste fino (\textit{fine-tuning}) de Modelos de Lenguaje Grandes (LLMs) de código abierto y tamaño reducido (<3B) utilizando QLoRA y estrategias de razonamiento (\textit{Chain-of-Thought}), enfocándose en la eficiencia y la portabilidad en entornos de hardware limitado.

La evaluación se realiza mediante un Criterio de Puntuación Compuesta (CPSC) que combina Factualidad (AlignScore), Legibilidad (Flesch y afines) y Relevancia (BERTScore). Los resultados demuestran que los modelos pequeños son competitivos en factualidad, pero la legibilidad sigue siendo el principal desafío.

## Objetivo General

Desarrollar y evaluar un pipeline eficiente y reproducible para la clasificación y generación de resúmenes biomédicos en lenguaje sencillo, demostrando su viabilidad técnica en entornos de recursos computacionales limitados.

### Objetivos Específicos

Implementar y evaluar un clasificador binario (disperso vs. contextual) que alcance alta precisión en la discriminación de textos científicos/PLS.

Ajustar modelos LLM ligeros (<3B) con QLoRA para generar PLS, comparando el rendimiento entre entornos locales (NVIDIA 4050) y en la nube (NVIDIA L4).

Cuantificar el impacto de estrategias de \textit{prompting} y razonamiento (CoT) en la factualidad y la legibilidad de los textos generados.

Definir y aplicar un Criterio de Puntuación Compuesta (CPSC) que priorice la utilidad clínica (factualidad y legibilidad) para la evaluacion todos los modelos.

## Estructura del Repositorio
La estructura del repositorio se diseñó para la trazabilidad y reproducibilidad del pipeline de PNL.

```
PROYECTO-PLN-FLAG/
├── datos/
│   ├── raw/                     # Corpus original (e.g., Cochrane, BioLaySumm)
│   └── pre-processed/           # Conjuntos limpios, tokenizados o particionados
├── docs/                        # Documentación y artículo final de tesis
├── modelos/                     # Checkpoints de LLMs ajustados (QLoRA) y clasificadores
├── notebooks/                   # Entorno de experimentación y desarrollo (Jupyter)
│   ├── clasificacion/           # Notebooks para el clasificador TF-IDF y ELECTRA
│   ├── finetuning/              # Notebooks para el ajuste QLoRA de cada modelo (Gemma, Llama, Qwen)
│   └── evaluacion/              # Notebooks para cálculo de métricas (BERTScore, AlignScore, CPSC)
├── resultados/                  # Resultados tabulares y cualitativos finales
│   ├── metricas/                # Tablas finales para el artículo (Tablas 5 y 6)
│   ├── resumenes/               # Resúmenes generados por los modelos (análisis cualitativo)
│   └── logs/                    # Logs de pérdida (loss logs) del entrenamiento
├── src/                         # Código modular y scripts de despliegue
└── requirements.txt             # Dependencias del proyecto
```

## Requisitos e Instalación
Proyecto probado con Python 3.12 y GPU NVIDIA.

### 1. Clonar e Instalar

Bash
#### 1. Clonar el repositorio
```
git clone https://[repositorio]
cd PROYECTO-PLN-FLAG
```
#### 2. Crear y activar entorno virtual (Recomendamos Mamba/Conda o venv)
```
python3 -m venv venv
source venv/bin/activate
```
#### 3. Instalar dependencias

es necesario recalcar que hay varios requirements.txt debido a que se necesitaron entornos diferentes, por ejemplo alignscore exige que sea un entorno python 3.10, y el entrenamiento de los modelos se realizo en python 3.12
```
pip install -r requirements.txt
```
### 2. Uso y Reproducción

Para ejecutar el pipeline y reproducir los resultados:

Exploración y Preprocesamiento: Ejecutar los notebooks en notebooks/data_prep/.

Clasificación: Entrenar los clasificadores dispersos y contextuales usando notebooks/clasificacion/.

Generación de PLS (QLoRA): Ejecutar los notebooks en notebooks/finetuning/ para entrenar los LLMs y luego los de notebooks/inferencia/ para generar los resúmenes con diferentes estrategias de prompting (CoT/OPT).

Evaluación: Ejecutar notebooks/evaluacion/ para calcular todas las métricas y el CPSC.

## Equipo de Trabajo

- Brayan Sthefen Gomez Salamanca
- Juan Sebastian Ordoñez Acuña 
- Maria Alejandra Rojas Garzon  
- Hainer Jair Torrenegra Jimenez