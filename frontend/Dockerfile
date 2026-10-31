# Dockerfile para Frontend Vite.js
FROM node:20-alpine

WORKDIR /app

# Copiar manifiestos de dependencias
COPY package.json ./

# Instalar dependencias
RUN npm install

# Copiar el código de la aplicación
COPY . .

EXPOSE 5173

# Ejecutar el servidor de desarrollo Vite expuesto en 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

