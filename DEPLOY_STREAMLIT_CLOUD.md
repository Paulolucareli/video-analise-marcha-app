# Deploy no Streamlit Cloud

## Pasta do projeto

`/Users/paulolucareli/Library/CloudStorage/OneDrive-Personal/NAPAM/Ícaro/Importar GCD/video_analise_marcha_app`

## Antes de publicar

Confirme que estes arquivos estão no repositório:

- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `analysis_schema.py`
- `temporal_parameters.py`
- `infographic.py`
- `frame_export.py`
- `calibration.py`
- `linear_parameters.py`
- `narrative.py`

## Passo a passo

1. Crie um repositório no GitHub.
2. Envie a pasta do app para esse repositório.
3. Acesse [Streamlit Community Cloud](https://share.streamlit.io/).
4. Clique em `Create app`.
5. Escolha o repositório.
6. Defina:
   - `Main file path`: `app.py`
   - `Python version`: deixe a padrão do serviço, se não houver exigência específica
7. Clique em `Deploy`.

## Configuração atual

- upload de vídeo até `500 MB`
- tema claro
- dependência de OpenCV compatível com deploy em nuvem usando `opencv-python-headless`

## Recomendações para aula

- usar vídeos curtos, preferencialmente abaixo de `100 MB`
- deixar vídeos de exemplo já separados
- testar no navegador exatamente como os alunos usarão
- manter uma cópia local do projeto como backup

## Limitações esperadas na nuvem

- vídeos muito grandes podem ficar lentos
- extração de frames e recortes pode demorar mais do que no computador local
- a experiência depende da qualidade da internet da sala
