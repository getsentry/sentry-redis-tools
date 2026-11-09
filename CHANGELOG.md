# Changelog and versioning

## 0.5.3

### Bug Fixes 🐛

- Restore wheel publishing by @sentry-junior in [#31](https://github.com/getsentry/sentry-redis-tools/pull/31)
- Publish repaired sdist only Co-Authored-By: Kyle Consalus <kyle.consalus@sentry.io> by @sentry-junior in [89adac60](https://github.com/getsentry/sentry-redis-tools/commit/89adac60c0a1d1f852a861a1f80eac60184bd3be)
- Build normalized Python distributions Co-Authored-By: Kyle Consalus <kyle.consalus@sentry.io> by @sentry-junior in [a883ca2e](https://github.com/getsentry/sentry-redis-tools/commit/a883ca2e9958c03570b68bced3c04e5585e2c49b)

### Internal Changes 🔧

- Test against a Valkey cluster on Python 3.12 by @Starrao123 in [#32](https://github.com/getsentry/sentry-redis-tools/pull/32)

## 0.5.2

### Bug Fixes 🐛

- Disable FailoverRedis pipeline retries by @kcons in [#29](https://github.com/getsentry/sentry-redis-tools/pull/29)

### Internal Changes 🔧

- Pin GitHub Actions to full-length commit SHAs by @joshuarli in [#28](https://github.com/getsentry/sentry-redis-tools/pull/28)

## 0.5.1

### Various fixes & improvements

- fix: add context manager to unsafe redis connection (#26) by @kylemumma

## 0.5.0

### Various fixes & improvements

- feat: Revert remove `rediscluster` (#21) by @shruthilayaj

## 0.4.0

### Retry `TimeoutError`

- feat: support retries for `TimeoutError` (#18) by @mwarkentin @kneeyo1

## 0.3.0

### Various fixes & improvements

- feat: remove `rediscluster` (#12) by @anonrig

## 0.2.0

### Various fixes & improvements

- fix: move `redis-py-cluster` to optional deps (#10) by @anonrig
- build: update github actions (#11) by @anonrig

## 0.1.7

### Various fixes & improvements

- fix: Also failover for pipelines (#8) by @untitaker

## 0.1.6

### Various fixes & improvements

- feat: Add retrying redis cluster (#7) by @untitaker
- fix: Make license Apache (#6) by @untitaker

## 0.1.5

### Various fixes & improvements

- feat: Add sliding window rate limiter (#5) by @untitaker
- feat: Add cardinality limiter (#4) by @untitaker

## 0.1.4

### Various fixes & improvements

- fix: Support redis 3 (#3) by @untitaker

## 0.1.3

### Various fixes & improvements

- fix: Add py.typed marker (#2) by @untitaker

## 0.1.2

### Various fixes & improvements

- fix: Do not depend on redis-py-cluster (#1) by @untitaker

## 0.1.1

- First release 🎉

