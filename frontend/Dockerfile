# ── Stage 1: Build ──
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

# ── Stage 2: Serve ──
FROM node:20-alpine
RUN npm install -g serve
WORKDIR /app
COPY --from=build /app/dist ./dist
EXPOSE 8074
# --single: modo SPA, todas las rutas a index.html (react-router)
CMD ["serve", "-s", "dist", "-l", "8074", "--single"]
