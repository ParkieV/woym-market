FROM node:alpine AS builder
WORKDIR /front
COPY package.json .
RUN npm install
COPY . .
RUN npm run build