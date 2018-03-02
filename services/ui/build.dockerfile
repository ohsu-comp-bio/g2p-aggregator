FROM node:carbon
ENV NODE_ENV=dev
# build dependecies
WORKDIR /node
COPY package*.json .
RUN npm install babel-core@6.3.26
RUN npm install babel-eslint@5.0.0-beta6
RUN npm install babel-loader@6.2.0
RUN npm install babel-preset-es2015@6.3.13
RUN npm install babel-preset-react@6.3.13
RUN npm install json-loader@0.5.7
RUN npm install webpack@3.10.0
RUN npm install webpack-dev-server@2.9.6
RUN npm install -g
COPY . . 
RUN npm run build
RUN ls -l index.js
