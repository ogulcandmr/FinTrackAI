-- FinTrackAI - Portfolio table schema
-- Data layer and wallet management (Part 2)
-- Run in Supabase SQL Editor or apply as a migration.

-- Portfolio rows: each row = one buy (position)
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

-- Users should only see their own rows
CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON portfolio(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_asset_id ON portfolio(asset_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_purchase_date ON portfolio(purchase_date);

-- RLS: Row Level Security
ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can read own portfolio"
    ON portfolio FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own portfolio rows"
    ON portfolio FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own portfolio rows"
    ON portfolio FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own portfolio rows"
    ON portfolio FOR DELETE
    USING (auth.uid() = user_id);

-- updated_at trigger (optional)
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

COMMENT ON TABLE portfolio IS 'FinTrackAI - User portfolio positions (asset id, purchase date, price, quantity)';
