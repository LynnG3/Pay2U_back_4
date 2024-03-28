FROM node:18 as build
# WORKDIR /app
#
# COPY package.json package.json
# COPY package-lock.json package-lock.json
#
# RUN npm install
#
# COPY . .
# RUN npm run tsc
# RUN npm install --global http-server
#
# CMD ["npx", "-y", "http-server", "-p", "8000", "/app/build"]

WORKDIR /app
COPY package*.json ./
RUN npm install tsx
COPY . ./
RUN npm run build
CMD cp -r build result_build
