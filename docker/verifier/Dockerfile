FROM mcr.microsoft.com/playwright:v1.48.0-jammy

WORKDIR /work

# Playwright config is copied in; tests are mounted at runtime
COPY playwright.config.ts /work/playwright.config.ts

# Ensure browsers are present (base image already has them)
RUN npx playwright install --with-deps chromium || true

CMD ["npx", "playwright", "test", "--config=/work/playwright.config.ts"]
