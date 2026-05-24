FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 8014
CMD ["npm", "start"]
