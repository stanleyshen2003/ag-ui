# Multi-stage build for minimal Next.js frontend (CopilotKit + AG-UI).
# Build stage: install deps and run next build with standalone output.
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies (use ci for reproducible builds).
COPY package.json package-lock.json ./
RUN npm ci

# Copy app and build (standalone output in .next/standalone).
COPY . .
RUN mkdir -p public
RUN npm run build

# Runtime stage: only standalone output + static assets.
FROM node:20-alpine AS runtime

WORKDIR /app

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone server and static files (public may be empty).
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Next.js standalone server.
CMD ["node", "server.js"]
