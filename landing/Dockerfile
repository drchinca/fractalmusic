FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY . .
RUN node --check server.js && node --check integrations.js && node --check email.js
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD wget -qO- http://127.0.0.1:3000/api/health >/dev/null || exit 1
CMD ["node", "server.js"]
