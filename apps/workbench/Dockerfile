# syntax=docker/dockerfile:1
FROM oven/bun:1 AS deps
WORKDIR /app/apps/workbench
COPY apps/workbench/package.json apps/workbench/bun.lock ./
RUN bun install --frozen-lockfile

FROM oven/bun:1 AS builder
WORKDIR /app
ARG NEXT_PUBLIC_AI_SERVICE_URL=
ENV NEXT_PUBLIC_AI_SERVICE_URL=${NEXT_PUBLIC_AI_SERVICE_URL}
COPY --from=deps /app/apps/workbench/node_modules ./apps/workbench/node_modules
COPY apps/workbench ./apps/workbench
COPY data ./data
WORKDIR /app/apps/workbench
ENV NEXT_TELEMETRY_DISABLED=1
RUN bun run build

FROM node:20-alpine AS runner
WORKDIR /app/apps/workbench
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=5900
ENV HOSTNAME=0.0.0.0

RUN addgroup -S -g 1001 nodejs && adduser -S -u 1001 -G nodejs nextjs

COPY --from=builder --chown=nextjs:nodejs /app/apps/workbench/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/workbench/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/apps/workbench/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/data /app/data

USER nextjs
EXPOSE 5900
CMD ["node", "server.js"]