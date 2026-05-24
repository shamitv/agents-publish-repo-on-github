FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 8020
CMD ["npm", "start"]
