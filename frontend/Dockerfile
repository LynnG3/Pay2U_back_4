FROM node:21-slim as build

WORKDIR /app
COPY package*.json ./
RUN npm i
COPY . ./
RUN npm run build
CMD cp -r build result_build
