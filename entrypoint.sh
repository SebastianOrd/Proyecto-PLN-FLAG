#!/bin/bash
# Autenticación
ngrok config add-authtoken $NGROK_AUTHTOKEN

# Exponer el puerto 8501
ngrok http 8501 > /tmp/ngrok.log &

# Arrancar streamlit
streamlit run /app/src/ui/app_streamlit.py --server.port=8501 --server.address=0.0.0.0