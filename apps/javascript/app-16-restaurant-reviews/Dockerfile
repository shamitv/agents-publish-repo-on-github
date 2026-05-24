FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 8016
CMD ["npm", "start"]
