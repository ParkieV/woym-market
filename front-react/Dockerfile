FROM node:alpine AS builder_with_req

RUN npm install -g serve

WORKDIR /usr/src/app
COPY ../front/package.json .

RUN npm install

FROM builder_with_req AS frontend_app

COPY ../front .
RUN npm run build

CMD ["serve", "/usr/src/app/build", "--listen", "3000"]