FROM node:20-alpine
RUN npm install -g serve
WORKDIR /app
COPY index.html ./public/index.html
EXPOSE 8074
CMD ["serve", "-s", "public", "-l", "8074", "--single"]