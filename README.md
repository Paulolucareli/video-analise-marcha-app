# Análise de Vídeo da Marcha

App em Streamlit para análise observacional da marcha com vídeo, criado a partir da lógica da planilha antiga `Análise de Vídeo LabMarch 5.xls`.

## O que o app faz

- importa vídeos do paciente
- permite navegar frame a frame
- marca eventos do ciclo de marcha
- registra eventos bilaterais para variáveis temporais
- gera texto clínico automaticamente
- monta um infográfico comparando direito, esquerdo e referência clínica
- exporta o laudo em Word com texto e imagens

## Estrutura principal

- `app.py`: interface principal
- `analysis_schema.py`: opções clínicas e eventos
- `temporal_parameters.py`: cálculos temporais
- `infographic.py`: painel visual comparativo
- `frame_export.py`: captura e montagem de frames
- `calibration.py`: calibração da plataforma
- `narrative.py`: geração do `.docx`

## Rodando localmente

```bash
cd "/Users/paulolucareli/Library/CloudStorage/OneDrive-Personal/NAPAM/Ícaro/Importar GCD/video_analise_marcha_app"
streamlit run app.py
```

## Publicação online

Este projeto já está preparado para publicação no Streamlit Community Cloud:

- `requirements.txt` com dependências do app
- `.streamlit/config.toml` com tema e upload maior para vídeos

Passo a passo resumido:

1. subir esta pasta para um repositório no GitHub
2. acessar o Streamlit Community Cloud
3. criar um novo app apontando para o repositório
4. escolher:
   - branch: a principal do repositório
   - main file path: `app.py`
5. publicar

## Observações para aula

- o upload máximo foi configurado para `500 MB`
- o desempenho online depende do tamanho do vídeo e da internet
- para aula, vale ter vídeos curtos de exemplo e uma versão local como backup
