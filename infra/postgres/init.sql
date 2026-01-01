-- PostgreSQL Schema for Yad2 Semantic Search Engine
-- This schema stores structured listing data (ground truth)

-- Create listings table
CREATE TABLE IF NOT EXISTS listings (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE NOT NULL,  -- ID from Yad2 or other source
    title TEXT,
    description TEXT NOT NULL,  -- Full listing description (Hebrew text)
    price INTEGER,  -- Price in NIS (can be NULL for "price on request")
    rooms DECIMAL(3, 1),  -- Number of rooms (e.g., 2.5, 3, 4.5)
    size_sqm INTEGER,  -- Apartment size in square meters
    location TEXT,  -- Neighborhood or area name
    city VARCHAR(100),  -- City name (e.g., תל אביב, ירושלים)
    neighborhood VARCHAR(100),  -- Specific neighborhood
    floor INTEGER,  -- Floor number (can be negative for basement)
    total_floors INTEGER,  -- Total floors in building
    has_parking BOOLEAN DEFAULT FALSE,
    has_elevator BOOLEAN DEFAULT FALSE,
    has_balcony BOOLEAN DEFAULT FALSE,
    has_storage BOOLEAN DEFAULT FALSE,
    furnished BOOLEAN DEFAULT FALSE,  -- מרוהט
    pets_allowed BOOLEAN DEFAULT NULL,  -- NULL = not specified
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_listings_external_id ON listings(external_id);
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price) WHERE price IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_listings_rooms ON listings(rooms) WHERE rooms IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_listings_city ON listings(city);
CREATE INDEX IF NOT EXISTS idx_listings_location ON listings(location);
CREATE INDEX IF NOT EXISTS idx_listings_scraped_at ON listings(scraped_at);
CREATE INDEX IF NOT EXISTS idx_listings_updated_at ON listings(updated_at);

-- Composite index for common filter combinations
CREATE INDEX IF NOT EXISTS idx_listings_city_price_rooms ON listings(city, price, rooms) 
    WHERE price IS NOT NULL AND rooms IS NOT NULL;

-- Full-text search index on description (for future keyword search)
CREATE INDEX IF NOT EXISTS idx_listings_description_fts ON listings USING gin(to_tsvector('hebrew', description));

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
