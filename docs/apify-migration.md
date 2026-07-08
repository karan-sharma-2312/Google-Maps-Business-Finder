# Apify Migration Plan

## Goal
Migrate localhost services into an Apify Actor by replacing only input/output layers.

## Service Reuse Strategy
- Keep discovery, website analyzer, SEO analyzer, repositories, and schemas unchanged.
- Wrap workflows in Actor input parser and dataset writer.

## Actor Mapping
- Input: Apify actor input JSON -> existing request schemas.
- Output: write result payloads to Apify Dataset.
- State: use Apify Key-Value Store for checkpoints and scheduler metadata.

## Implementation Steps
1. Create Actor entry module under scripts or a dedicated apify package.
2. Load actor input and validate with existing Pydantic models.
3. Call existing services.
4. Push result items to dataset.
5. Store summary metrics to key-value store.

## Publication Checklist
- Add README tailored for store listing.
- Add usage examples and expected output schema.
- Configure pricing and usage limits.
- Add actor test run and sample dataset export.
