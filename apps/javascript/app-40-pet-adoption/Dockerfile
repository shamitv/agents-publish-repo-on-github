FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 8040
CMD ["npm", "start"]
