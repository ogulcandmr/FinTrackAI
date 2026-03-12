-- FinTrackAI - Portföy Tablosu Şeması
-- Veri Katmanı ve Cüzdan Yönetimi (2. Kısım)
-- Supabase SQL Editor'da çalıştırın veya migration ile uygulayın.

-- Portföy kayıtları: her satır = bir alım (pozisyon)
CREATE TABLE IF NOT EXISTS portfolio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    asset_id TEXT NOT NULL,
    purchase_date DATE NOT NULL,
    price NUMERIC(20, 8) NOT NULL CHECK (price > 0),
    quantity NUMERIC(20, 8) NOT NULL CHECK (quantity > 0),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Kullanıcı sadece kendi kayıtlarını görebilsin
CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON portfolio(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_asset_id ON portfolio(asset_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_purchase_date ON portfolio(purchase_date);

-- RLS: Row Level Security
ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;

-- Politikalar
CREATE POLICY "Kullanıcı kendi portföyünü görebilir"
    ON portfolio FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Kullanıcı kendi portföyüne ekleme yapabilir"
    ON portfolio FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Kullanıcı kendi portföy kaydını güncelleyebilir"
    ON portfolio FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Kullanıcı kendi portföy kaydını silebilir"
    ON portfolio FOR DELETE
    USING (auth.uid() = user_id);

-- updated_at tetikleyicisi (opsiyonel)
CREATE OR REPLACE FUNCTION update_portfolio_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS portfolio_updated_at ON portfolio;
CREATE TRIGGER portfolio_updated_at
    BEFORE UPDATE ON portfolio
    FOR EACH ROW
    EXECUTE PROCEDURE update_portfolio_updated_at();

COMMENT ON TABLE portfolio IS 'FinTrackAI - Kullanıcı portföy pozisyonları (Asset ID, Alış Tarihi, Fiyat, Adet)';
