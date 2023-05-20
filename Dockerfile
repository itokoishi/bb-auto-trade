FROM nikolaik/python-nodejs:python3.9-nodejs16

RUN apt-get update && apt-get install -y curl unzip
RUN apt-get install -y less jq

RUN mkdir /app

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip && ./aws/install

RUN npm install -g aws-cdk@2.20

# 下記のコマンドを追加します。
# COPY requirements.txt .
# RUN pip3 install -r requirements.txt