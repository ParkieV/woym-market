FROM node:18-alpine as builder

WORKDIR /front
COPY package.json .
COPY package-lock.json .
RUN npm ci
COPY . .
RUN npm run build


FROM node:18-alpine as production

WORKDIR /front
COPY --from=builder /front/build ./build
COPY --from=builder /front/node_modules ./node_modules
COPY package.json .
CMD ["node", "./build"]