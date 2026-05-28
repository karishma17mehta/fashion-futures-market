"""
Manual seed data from WGSN reports, Instagram @databutmakeitfashion, and curated sources.
Run from backend/ directory: python -m data.seeds.manual_seed
"""
import sys, uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from db.session import SessionLocal
from db.models import Trend, Market, TrendStatus, MarketStatus

TRENDS = [
    # ── WGSN Top Trends 2026 ──────────────────────────────────────────────
    {
        "name": "Guardian Design",
        "description": "Anti-theft features becoming must-have in accessories and apparel. Button shoulder straps on coats, RFID-blocking pockets, carabiner clips, tunnel-locked zippers.",
        "ai_score": 8.5,
        "ai_thesis": "WGSN flagged this as a top 2026 fashion trend. Rising urban anxiety + commuter culture + smart design convergence. Anti-slash pockets and branded security hardware are crossing from travel gear into everyday wear. Brands adding 'designed-in deterrents' as signature value. Strong functional + aesthetic case.",
        "source": "wgsn",
        "signal_velocity": 4.2,
        "resolution_question": "Will anti-theft design features (RFID pockets, carabiner clips, tunnel zippers) appear in 3+ major high-street brand collections by end of 2026?",
    },
    {
        "name": "Going for Gold",
        "description": "Gold renaissance driven by economic uncertainty and status dressing. Bold gold jewellery, lamé scarves, gold bags and footwear layered into casual looks.",
        "ai_score": 8.2,
        "ai_thesis": "Gold is at its highest market pricing run as a status metal. WGSN ties this to #80s status dressing revival + vintage styling influence. The casualisation of gold (layering lamé into everyday outfits) signals this isn't just red-carpet — it's a mass-market shift. Uncertainty economics drive safe-haven aesthetics.",
        "source": "wgsn",
        "signal_velocity": 5.5,
        "resolution_question": "Will gold jewellery and lamé accents appear in the top 5 fast-fashion homepage features (Zara, H&M, ASOS, Mango, Topshop) by Sept 2026?",
    },
    {
        "name": "Rugged Luxury",
        "description": "Outdoor gear infused with high-performance durability and elevated design. Premium aesthetics in camping/hiking gear, democratised luxury for nature experiences.",
        "ai_score": 7.8,
        "ai_thesis": "WGSN's top sports & outdoor trend for 2026. Consumer fatigue driving demand for multi-sensorial rest products. Glamping and sophisticated escapism rising fast. Brands must combine tactile hedonism + sustainable materials. The gorpcore aesthetic matures into something more refined — performance meets provenance.",
        "source": "wgsn",
        "signal_velocity": 3.8,
        "resolution_question": "Will 3+ luxury fashion houses (e.g. Loro Piana, Brunello Cucinelli, Arc'teryx Veilance) launch dedicated outdoor-elevated collections by end of 2026?",
    },
    {
        "name": "Digital Privilege / Offline Luxury",
        "description": "Logging off is the new luxury logo. Ability to disconnect without sacrificing career or social standing becomes a status symbol. Brands creating digital detox experiences and offline sanctuaries.",
        "ai_score": 8.8,
        "ai_thesis": "WGSN macro insight: nearly half of young adults say online life harms wellbeing. The Restorers consumer persona (WGSN FC28) is built around this. Fashion implication: clothing and experiences designed to signal intentional offline presence. Expect 'no-phone' aesthetic brands, analogue accessories, retreat wear. Extremely timely cultural moment.",
        "source": "wgsn",
        "signal_velocity": 6.0,
        "resolution_question": "Will 'offline luxury' or 'digital detox' appear as a named trend category on 2+ major trend forecasting platforms (WGSN, Vogue Business, BoF) by mid-2026?",
    },
    {
        "name": "Gatekeeping Aesthetics",
        "description": "Exclusivity comeback — consumers guarding the products and spaces that define them. Closed communities, locked Reels, invite-only groups. Protecting cultural capital.",
        "ai_score": 7.5,
        "ai_thesis": "WGSN 2026 insight trend. Viral trends burning out faster than ever, driving a counter-movement of intentional obscurity. Fashion implication: underground brands gaining cachet precisely because they resist mainstream visibility. Invite-only drops, private community commerce, brand mystique as strategy. Aligns with anti-algorithm sentiment.",
        "source": "wgsn",
        "signal_velocity": 4.0,
        "resolution_question": "Will invite-only or members-only brand drops become a documented strategy for 3+ mid-tier fashion brands by end of 2026?",
    },

    # ── @databutmakeitfashion / Instagram data ────────────────────────────
    {
        "name": "Seasonal Florals Resurgence",
        "description": "Spring 2026 floral resurgence stronger than usual. Searches 36% higher vs last year. Dior Fall 2026 featured florals in 51% of looks. Demna's Gucci debut: 61% floral patterns.",
        "ai_score": 7.2,
        "ai_thesis": "Data-backed: Google + Pinterest floral searches up 36% YoY for Spring 2026. Runway confirmation from Dior (51% of looks), Gucci Demna debut (61% patterns). This is a move away from 2025 minimalism dominance. Florals are crossing from expected seasonal into a maximalism statement. Broad market signal.",
        "source": "instagram_databutmakeitfashion",
        "signal_velocity": 3.6,
        "resolution_question": "Will florals be featured in 40%+ of major SS26 runway collections as documented by Vogue Runway by June 2026?",
    },
    {
        "name": "Romanticism Wave 2026",
        "description": "Google searches for 'romance' at 5-year high, up 27% in 2026 vs 5-year avg, growing 8% annually since 2021. Driven by Bridgerton S4, Broadway record ($1.89B season), cultural shift to intentional artistic experiences.",
        "ai_score": 8.0,
        "ai_thesis": "Multi-signal trend: Google data, Netflix rankings, record Broadway revenue all pointing the same direction. Fashion implication: romantic silhouettes, corsetry, soft draping, lace, ballet references. 2026 is the year romanticism goes from niche aesthetic to mainstream category. Corset searches, ballet flat data, and Bridgerton cosplay all feeding this.",
        "source": "instagram_databutmakeitfashion",
        "signal_velocity": 8.0,
        "resolution_question": "Will 'Romanticism' or 'Romantic dressing' be named a top-5 trend by Vogue, Harper's Bazaar, or BoF for AW26?",
    },
    {
        "name": "White / Cloud Dancer Dominance",
        "description": "Pantone Color of 2026: Cloud Dancer (white). Follows pink (2023), green (2024), orange (2025). Fashion implications: white-on-white dressing, white tanks (+160% popularity YoY), clean minimalism.",
        "ai_score": 7.8,
        "ai_thesis": "Pantone 2026 = Cloud Dancer (white). Historical pattern: each Pantone color creates a 12-18 month halo effect on fashion purchasing. White tank tops already 160% more popular YoY per Instagram data. Luxury collections showing white monochromatic looks (Gucci: 71% monochromatic in Demna debut). Clean, blank-slate aesthetic fitting post-maximalism correction.",
        "source": "instagram_databutmakeitfashion",
        "signal_velocity": 5.0,
        "resolution_question": "Will white/off-white be the dominant color in 3+ major fast-fashion seasonal campaigns by Summer 2026?",
    },
    {
        "name": "Lip Liner Index",
        "description": "Lip liner is the most popular lip product — 172% more popular than lip gloss and lipstick on average. Online searches growing 69% monthly. Lip filler searches declining 3% monthly, signalling shift from injectable to cosmetic.",
        "ai_score": 6.8,
        "ai_thesis": "Data signal from @databutmakeitfashion: lip liner searches growing 69% monthly in 2026 while lip filler interest declining 3% monthly. Modern lipstick index equivalent — affordable luxury indicator. Fashion implication: bold, defined lip as key styling accessory. Brands selling colour cosmetics as statement accessories rather than beauty afterthoughts.",
        "source": "instagram_databutmakeitfashion",
        "signal_velocity": 6.9,
        "resolution_question": "Will lip liner overtake lipstick as the #1 purchased lip product in at least one major UK/US beauty retailer's sales data by end of 2026?",
    },
    {
        "name": "The Restorers Consumer Shift",
        "description": "WGSN FC28 persona: calm, sensory-aware consumers reclaiming balance. Buy less but better. Tactile fabrics, natural fibres, artisanal finishes. 40% of US Gen Z report almost always stressed (McKinsey). 47% of young people would prefer to grow up without internet.",
        "ai_score": 9.0,
        "ai_thesis": "WGSN's #1 Future Consumer 2028 persona. Macro-level shift not a micro-trend. Fashion brands that survive the next cycle will design for emotional restoration not stimulation. Tactile luxury, repairability, provenance, slow fashion signals. The Restorers buy less but better — this fundamentally restructures the volume-based fast fashion model. Highest confidence, longest runway.",
        "source": "wgsn",
        "signal_velocity": 7.0,
        "resolution_question": "Will 'slow fashion' or 'restorative design' be named a macro trend by 3+ industry analysts or forecasting houses by end of 2026?",
    },
    {
        "name": "Unserious Everything",
        "description": "WGSN macro trend 2026: anything serious is out, anything unserious is in. Subversive, irreverent, laugh-out-loud consumer energy. Evolution of Glimmers trend. Applies across fashion, beauty, tech, food.",
        "ai_score": 8.3,
        "ai_thesis": "WGSN's overarching macro for 2026 — emotional release and self-care driving irreverence. Fashion implication: novelty prints, absurdist accessories, anti-serious styling, meme-able garments. Post-serious luxury: brands that can be playful without losing premium positioning will win Gen Z. Kawaii crossover to Western markets fits here.",
        "source": "wgsn",
        "signal_velocity": 5.5,
        "resolution_question": "Will novelty/humour-forward fashion collections (non-costume) feature in 5+ major brand lookbooks for AW26?",
    },
    {
        "name": "Neurocosmetics in Fashion Beauty",
        "description": "Beauty used to regulate nervous systems. Haptic-led packaging, sensorial formulations, deliberate routines as mindful practices. Anti-noisy beauty and wellness tech. WGSN Restorers persona.",
        "ai_score": 7.5,
        "ai_thesis": "WGSN FC28: The Restorers use beauty to regulate nervous systems. Fashion-adjacent: textures, tactility and scent becoming core design criteria for wearables and accessories. Fragrance as fashion statement growing (personal fragrance wardrobe concept). Sensorial dressing — fabric texture, skin-feel — becoming a purchase driver over visual aesthetics alone.",
        "source": "wgsn",
        "signal_velocity": 4.5,
        "resolution_question": "Will 'sensorial dressing' or 'neuroaesthetics in fashion' be cited in 3+ major fashion editorial pieces by end of 2026?",
    },
    {
        "name": "Loewe Effect — Small Brand Sentiment Premium",
        "description": "Loewe's creative director debut received highest overall positive sentiment — 30% more positive than other brands. Has 7M IG followers vs Chanel's 60M. Smaller brands can dominate quality of discourse over quantity.",
        "ai_score": 7.0,
        "ai_thesis": "Data insight: sentiment quality matters more than follower volume in 2026. Loewe outperforming Chanel on positivity with 1/8th the audience. Fashion market implication: niche brands with high-quality communities are undervalued in traditional metrics. Prediction market angle — can identify which small brands will break through before follower counts signal it.",
        "source": "instagram_databutmakeitfashion",
        "signal_velocity": 3.5,
        "resolution_question": "Will Loewe achieve a 20% increase in brand search volume (per Google Trends) by end of 2026 without a major campaign or celebrity endorsement?",
    },
    {
        "name": "Divisive Trend Signal — High Volume Low Sentiment",
        "description": "Divisive trends (high conversation, mixed/negative sentiment) often have lasting impact. Labubu accessory: search traffic grew 2% daily while sentiment dropped 15%. Bieber Skylrk boxers: 300% web traffic spike but 36% less positive sentiment.",
        "ai_score": 6.5,
        "ai_thesis": "Key pattern identified by @databutmakeitfashion: divisive trends — lots of conversation but mixed sentiment — are actually longer-lasting than purely positive trends. Controversy = cultural stickiness. Fashion market implication: don't bet against viral-but-polarising trends too early. High volume + low sentiment = durable trend, not a fad.",
        "source": "instagram_databutmakeitfashion",
        "signal_velocity": 2.0,
        "resolution_question": "Will Labubu accessories still be commercially available and actively sold at major streetwear retailers 12 months after their viral peak?",
    },
    {
        "name": "Ralph Lauren Calendar Return — Heritage Brand Revival",
        "description": "Ralph Lauren returned to official men's calendar in Jan 2026 for first time in 20 years. 73-look runway. Calvin Klein had 190% popularity spike on NYFW return. Off-calendar absence followed by dramatic comeback = proven playbook.",
        "ai_score": 6.8,
        "ai_thesis": "Data pattern: brand withdrawal + strategic return creates massive attention spike. Ralph Lauren's return mirrors Calvin Klein's 190% popularity surge. Fashion market signal: heritage American brands in revival cycle (fits Romanticism wave + nostalgia tailwinds). Market question: which other absent heritage brands return in 2026-27?",
        "source": "instagram_databutmakeitfashion",
        "signal_velocity": 3.0,
        "resolution_question": "Will Ralph Lauren's brand popularity (per Google Trends) increase 50%+ in the 30 days following their NYFW January 2026 return?",
    },
]


def run():
    db = SessionLocal()
    written = 0
    skipped = 0

    for t in TRENDS:
        exists = db.query(Trend).filter(Trend.name == t["name"]).first()
        if exists:
            skipped += 1
            continue

        trend = Trend(
            id=str(uuid.uuid4()),
            name=t["name"],
            description=t["description"],
            ai_score=t["ai_score"],
            ai_thesis=t["ai_thesis"],
            source=t["source"],
            signal_velocity=t["signal_velocity"],
            status=TrendStatus.emerging,
        )
        db.add(trend)
        db.flush()

        resolution_date = datetime.utcnow() + timedelta(days=180)
        market = Market(
            id=str(uuid.uuid4()),
            trend_id=trend.id,
            question=t["resolution_question"],
            resolution_date=resolution_date,
            resolution_criteria=t["resolution_question"],
            yes_price=0.5,
            no_price=0.5,
            liquidity_param=100.0,
            status=MarketStatus.open,
        )
        db.add(market)
        written += 1

    db.commit()
    db.close()
    print(f"\n✓ {written} trends + markets written to DB ({skipped} skipped as duplicates)")


if __name__ == "__main__":
    run()
