-- Portfolio tablosunda 'asset_id' bulunamadı (PGRST204) hatası için
-- Supabase Dashboard → SQL Editor → New query → Bu scripti yapıştırıp Run.

-- Eksik sütunları ekle (tablo zaten varsa hiçbir şeyi silmez)
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS asset_id TEXT;
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS purchase_date DATE;
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS price NUMERIC(20, 8);
ALTER TABLE portfolio ADD COLUMN IF NOT EXISTS quantity NUMERIC(20, 8);

-- Eski 'symbol' sütunu varsa asset_id'ye kopyala
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'portfolio' AND column_name = 'symbol'
  ) THEN
    UPDATE portfolio SET asset_id = COALESCE(asset_id, symbol);
  END IF;
END $$;
