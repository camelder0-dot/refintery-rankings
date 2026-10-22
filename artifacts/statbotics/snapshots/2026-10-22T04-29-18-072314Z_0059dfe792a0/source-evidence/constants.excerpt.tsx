// Excerpts from https://raw.githubusercontent.com/avgupta456/statbotics/169330ecef38a4f614356ac0b0caa156f2180021/frontend/src/constants.tsx
// Original lines 3-10
// undici bug requires 127.0.0.1 instead of localhost
export const BACKEND_URL = PROD
  ? "https://api.statbotics.io/v3/site"
  : "http://127.0.0.1:8000/v3/site";

export const BUCKET_URL = PROD
  ? "https://storage.googleapis.com/site_v1"
  : "https://storage.googleapis.com/site_dev_v1";
// Original lines 14-15
export const CURR_YEAR = 2026;
export const DISABLE_GCS = true; // TODO: Re-enable for 2027 season
