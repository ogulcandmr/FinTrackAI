-- Fix missing 'asset_id' on portfolio (PGRST204)
-- Supabase Dashboard → SQL Editor → New query → paste this script → Run.

-- Add missing columns (does not delete anything if the table already exists)
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS asset_id TEXT;
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS purchase_date DATE;
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS price NUMERIC(20, 8);
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS quantity NUMERIC(20, 8);

-- If legacy 'symbol' column exists, copy into asset_id
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'portfolio' AND column_name = 'symbol'
  ) THEN
    UPDATE portfolio SET asset_id = COALESCE(asset_id, symbol);
  END IF;
END $$;
