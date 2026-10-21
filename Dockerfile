# W5 部署到 Render（Docker）時使用
FROM python:3.12-slim

# 以非 root 使用者執行（uid 1000）
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# 先裝套件、再複製程式：只改程式時，不用重裝套件
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .

# Render 的 Environment Variables 必須設定 PORT=7860
EXPOSE 7860
CMD ["solara", "run", "app.py", "--host=0.0.0.0", "--port=7860", "--production"]
