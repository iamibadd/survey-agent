# Build stage
FROM node:24-alpine AS build

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY package*.json ./

# Install dependencies (for build)
RUN npm ci

# Copy source files
COPY . .

# Build production files
RUN npm run build

# Expose Vite preview port
EXPOSE 5173

# Start the server
CMD ["npm", "run", "dev"]
