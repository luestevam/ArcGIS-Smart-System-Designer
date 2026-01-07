# Deploy da aplicação Streamlit

Resumo rápido: esta aplicação é um app Streamlit (`app.py`). Plataformas como Vercel/GitHub Pages não são adequadas para apps Streamlit (aplicações long‑running). Recomenda-se usar Streamlit Community Cloud, Heroku, Render ou Railway.

Passos recomendados

- Streamlit Community Cloud (recomendado)
  1. Crie uma conta em https://share.streamlit.io
  2. Conecte o repositório GitHub e selecione o repositório
  3. Aponte o campo `Main file` para `app.py` e verifique que `requirements.txt` existe
  4. Deploy — o Streamlit cuidará do ambiente

- Heroku / Render / Railway
  - Certifique-se que `requirements.txt`, `Procfile` e `runtime.txt` estejam no repo (já incluídos).
  - Exemplo rápido com Git (Heroku):

```bash
git add requirements.txt Procfile runtime.txt README.md
git commit -m "Add deployment files"
git push origin main

# (Heroku CLI) ou conectar GitHub no painel Heroku/Render e implantar
heroku create my-app-name
git push heroku main
```

Observações
- Vercel e GitHub Pages servem sites estáticos ou serverless functions; Streamlit requer um processo web permanente (sempre online), por isso causam erros 404/NOT_FOUND ao tentar usar Vercel para esse tipo de app.
- Se quiser, posso ajudar a configurar o deploy no Streamlit Cloud passo a passo ou preparar o repositório para Heroku/Render e orientá-lo a criar a aplicação na plataforma.
