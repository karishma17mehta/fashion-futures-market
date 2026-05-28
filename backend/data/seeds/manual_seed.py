"""
Manual seed data for fashion trend intelligence pipeline.
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
    {
        "name": "Guardian Design",
        "description": "Security-forward design is moving from niche travel gear into mainstream fashion, with anti-theft hardware — tunnel zippers, carabiner clips, RFID-blocking pockets — becoming viable aesthetic differentiators for urban commuter collections.",
        "ai_score": 8.5,
        "ai_thesis": "Guardian Design sits at the intersection of rising urban anxiety and consumer demand for functional streetwear that doesn't sacrifice style. As commuter culture evolves, brands that embed visible security features into their silhouettes gain a dual signal: practical credibility and a design language that reads as intentional and modern. The crossover from travel accessories into everyday apparel suggests this is a durable category shift rather than a seasonal novelty. Collections that brand their security hardware distinctively — rather than hiding it — will capture the strongest market premium.",
        "source": "trend_intelligence",
        "signal_velocity": 4.2,
        "resolution_question": "Will anti-theft design features (RFID pockets, carabiner clips, tunnel zippers) appear in 3+ major high-street brand collections by end of 2026?",
    },
    {
        "name": "Going for Gold",
        "description": "Gold is undergoing a mainstream rehabilitation — escaping its red-carpet confinement and re-entering everyday wardrobes through lamé layering, bold chain jewellery, and metallic footwear paired with casual separates.",
        "ai_score": 8.2,
        "ai_thesis": "Gold's resurgence tracks closely with macroeconomic uncertainty cycles, where consumers historically gravitate toward status-coded materials as a form of psychological anchoring. What distinguishes this wave is the casualisation vector: gold is being democratised through accessible layering rather than reserved for occasion dressing, which dramatically broadens its addressable market. The parallel with 1980s status dressing revival gives brands a nostalgic reference point that resonates across Gen X and millennial demographics simultaneously. Fast-fashion adoption of lamé and gold-tone hardware will be the clearest indicator that this has moved beyond runway aspiration.",
        "source": "trend_intelligence",
        "signal_velocity": 5.5,
        "resolution_question": "Will gold jewellery and lamé accents appear in the top 5 fast-fashion homepage features (Zara, H&M, ASOS, Mango, Topshop) by Sept 2026?",
    },
    {
        "name": "Rugged Luxury",
        "description": "The gorpcore aesthetic is maturing into a more considered proposition: premium outdoor apparel and gear designed for consumers who want both trail-ready performance and the visual language of considered luxury.",
        "ai_score": 7.8,
        "ai_thesis": "Rugged Luxury reflects a consumer base exhausted by purely aspirational fashion and increasingly drawn to products that justify their price through functional excellence rather than brand mythology alone. The glamping economy and the rise of sophisticated escapism have created a new consumer archetype that refuses to choose between comfort and aesthetics in outdoor contexts. Brands that can credibly combine certified performance materials with refined construction details — and communicate the provenance of both — will own this space as it moves from outdoor specialist labels into the broader luxury market. The sustainability angle (durable goods, natural fibres, repairability) further extends the value proposition.",
        "source": "trend_intelligence",
        "signal_velocity": 3.8,
        "resolution_question": "Will 3+ luxury fashion houses (e.g. Loro Piana, Brunello Cucinelli, Arc'teryx Veilance) launch dedicated outdoor-elevated collections by end of 2026?",
    },
    {
        "name": "Digital Privilege / Offline Luxury",
        "description": "Intentional disconnection is becoming a legible status signal — the capacity to step away from digital obligation without professional or social penalty is positioning itself as the new luxury flex.",
        "ai_score": 8.8,
        "ai_thesis": "Digital Privilege is the logical endpoint of a decade of wellness marketing: when everyone can access a smoothie and a meditation app, the true luxury becomes structural freedom from the attention economy itself. Fashion's role in this shift is significant — clothing and accessories that signal analogue intentionality (no logo-lock, no QR-code integration, no smart functionality) function as counter-cultural luxury objects. The Restorers consumer archetype, increasingly documented across multiple demographic cohorts, is shaping purchasing logic around restoration and presence rather than stimulation and display. Brands that design physical sanctuaries, produce analogue-first accessories, or build anti-notification aesthetics into their identity will capture outsized loyalty from this high-value segment.",
        "source": "trend_intelligence",
        "signal_velocity": 6.0,
        "resolution_question": "Will 'offline luxury' or 'digital detox' appear as a named trend category on 2+ major trend forecasting platforms (WGSN, Vogue Business, BoF) by mid-2026?",
    },
    {
        "name": "Gatekeeping Aesthetics",
        "description": "As viral trend cycles accelerate and compress, a counter-movement of deliberate scarcity and cultural exclusivity is gaining traction — consumers and brands alike are pulling back from mass visibility as a form of value protection.",
        "ai_score": 7.5,
        "ai_thesis": "Gatekeeping Aesthetics is a direct market response to algorithmic flattening: when every trend reaches saturation within weeks, the act of withholding becomes its own brand strategy. Underground labels and closed-community commerce are not simply niche quirks — they represent a tested mechanism for preserving brand mystique in an era when overexposure destroys premium positioning faster than any competitor can. The fashion market implication is structural: discovery channels are bifurcating between mass algorithmic distribution and high-trust private networks, and the brands investing in the latter now will hold durable pricing power. Invite-only drops and locked-access content are the aesthetic expressions of this economic logic.",
        "source": "trend_intelligence",
        "signal_velocity": 4.0,
        "resolution_question": "Will invite-only or members-only brand drops become a documented strategy for 3+ mid-tier fashion brands by end of 2026?",
    },

    {
        "name": "Seasonal Florals Resurgence",
        "description": "Spring 2026 floral adoption is running materially ahead of prior cycles, with search data showing a 36% year-over-year increase and runway confirmation across multiple major houses — including Dior and Gucci's Demna debut — signalling a pattern rather than a coincidence.",
        "ai_score": 7.2,
        "ai_thesis": "When runway adoption, search volume growth, and social engagement all converge on the same motif simultaneously, the result is a trend with real commercial velocity rather than editorial hype. The 2026 floral resurgence is notable precisely because it follows a sustained minimalism cycle — consumers returning to pattern after deliberate restraint tend to overcorrect, driving stronger-than-baseline market penetration. Dior's 51% floral proportion and Gucci's 61% in a debut collection are not coincidental: they reflect creative directors reading the same underlying consumer mood. The commercial window for florals in 2026 is wider than a typical seasonal lift.",
        "source": "social_data",
        "signal_velocity": 3.6,
        "resolution_question": "Will florals be featured in 40%+ of major SS26 runway collections as documented by Vogue Runway by June 2026?",
    },
    {
        "name": "Romanticism Wave 2026",
        "description": "Romantic aesthetics are consolidating across entertainment, search behaviour, and live cultural spending in 2026 — corsetry, soft draping, lace, and ballet references are intersecting with broader cultural appetite for intentional, artistically rich experiences.",
        "ai_score": 8.0,
        "ai_thesis": "Romanticism Wave 2026 has an unusually robust multi-signal foundation: search volume, streaming performance, and record live entertainment revenue are pointing in the same direction simultaneously, which sharply reduces false-positive risk for this trend call. The fashion implication is that romantic silhouettes are not being driven by a single cultural moment but by a sustained consumer mood shift toward aesthetic richness after years of functional minimalism. Ballet flat search data and corset popularity metrics are both running ahead of prior comparable trend cycles, suggesting this has already moved from aspirational to commercial. Brands that build romantic capsule collections rather than one-off pieces will capture the longer tail of this shift.",
        "source": "social_data",
        "signal_velocity": 8.0,
        "resolution_question": "Will 'Romanticism' or 'Romantic dressing' be named a top-5 trend by Vogue, Harper's Bazaar, or BoF for AW26?",
    },
    {
        "name": "White / Cloud Dancer Dominance",
        "description": "Cloud Dancer — Pantone's 2026 colour of the year — is translating into measurable commercial movement, with white tank tops already tracking 160% above prior-year popularity and monochromatic white looks appearing at outsized frequency across major runway collections.",
        "ai_score": 7.8,
        "ai_thesis": "Pantone colour-of-year designations have a documented 12-18 month halo effect on fashion purchasing across both mass and premium market tiers, making Cloud Dancer a reliable near-term commercial signal rather than speculative trend noise. The white monochromatic direction also fits neatly into the broader post-maximalism correction: after two seasons of high-saturation colour, the market appetite for clean, blank-slate dressing is commercially logical. Gucci's 71% monochromatic showing in a high-profile debut collection adds designer-level confirmation to what the data is already indicating. The risk is commoditisation speed — white basics are easy to reproduce, so margin advantage will concentrate in brands that execute texture and construction at a premium level.",
        "source": "social_data",
        "signal_velocity": 5.0,
        "resolution_question": "Will white/off-white be the dominant color in 3+ major fast-fashion seasonal campaigns by Summer 2026?",
    },
    {
        "name": "Lip Liner Index",
        "description": "Lip liner has displaced lip gloss and lipstick as the dominant lip product by search volume, with monthly query growth running at 69% while injectable lip filler interest declines — a shift from clinical enhancement toward expressive cosmetic definition.",
        "ai_score": 6.8,
        "ai_thesis": "Lip Liner Index functions as a modern iteration of the classic lipstick index: a cost-accessible beauty product surging during a period of economic uncertainty, offering consumers a visible style update without significant financial commitment. The simultaneous decline in lip filler search interest is analytically significant — it suggests the market is moving from structural body modification back toward surface-level styling, which historically correlates with broader shifts toward creative expression over perfection culture. For fashion brands with beauty adjacency, this signals renewed appetite for bold, defined lip looks as a styling statement that can anchor an entire outfit narrative. The monthly growth rate is steep enough to suggest this is still in its acceleration phase.",
        "source": "social_data",
        "signal_velocity": 6.9,
        "resolution_question": "Will lip liner overtake lipstick as the #1 purchased lip product in at least one major UK/US beauty retailer's sales data by end of 2026?",
    },
    {
        "name": "The Restorers Consumer Shift",
        "description": "A structurally distinct consumer segment is coalescing around restoration-oriented purchasing logic — buying fewer, better-made pieces, prioritising tactile quality and natural materials, and treating the act of dressing as a form of sensory self-regulation rather than social performance.",
        "ai_score": 9.0,
        "ai_thesis": "The Restorers represent a macro-level consumer reorientation, not a product trend — and that distinction matters enormously for forecasting. When purchasing logic itself changes, every product category is affected: volume-based fast fashion loses structural relevance, artisanal and repairability credentials gain pricing power, and the emotional register of marketing must shift from aspiration to restoration. McKinsey stress data and generational internet ambivalence both point to the same underlying driver: consumers who feel chronically overstimulated are actively seeking material environments that calm rather than excite. Fashion brands that design for this sensory register — tactile luxury, muted palettes, transparent provenance — will build the kind of loyalty that survives trend cycles.",
        "source": "trend_intelligence",
        "signal_velocity": 7.0,
        "resolution_question": "Will 'slow fashion' or 'restorative design' be named a macro trend by 3+ industry analysts or forecasting houses by end of 2026?",
    },
    {
        "name": "Unserious Everything",
        "description": "Consumer appetite for irreverence and emotional lightness is becoming a dominant purchasing signal in 2026 — novelty prints, absurdist accessories, and anti-serious styling are crossing from subculture into mainstream commercial collections.",
        "ai_score": 8.3,
        "ai_thesis": "Unserious Everything is the aesthetic counterweight to prolonged cultural heaviness — after several years of earnest, values-forward brand communication, the market is visibly fatiguing on sincerity and reaching for levity. The commercial opportunity is real but technically demanding: brands that can execute playfulness without sacrificing premium positioning will capture Gen Z's loyalty, while those that treat irreverence as a bolt-on campaign tone will miss the underlying shift. Kawaii-influenced Western product design, meme-literate collections, and humour-forward brand voice are all expressions of the same consumer demand. The risk is that novelty has a short shelf life — winning brands will need a consistent irreverent identity rather than isolated playful moments.",
        "source": "trend_intelligence",
        "signal_velocity": 5.5,
        "resolution_question": "Will novelty/humour-forward fashion collections (non-costume) feature in 5+ major brand lookbooks for AW26?",
    },
    {
        "name": "Neurocosmetics in Fashion Beauty",
        "description": "Beauty and fashion are converging around a shared brief: products designed not just to look good but to actively modulate the wearer's sensory and emotional state, with haptic packaging, skin-feel fabric selection, and scent becoming first-order design criteria.",
        "ai_score": 7.5,
        "ai_thesis": "Neurocosmetics in Fashion Beauty reflects a broader collapse of the boundary between wellness and style — consumers who approach beauty routines as nervous-system regulation are applying the same logic to clothing and accessories, selecting for texture, weight, and scent as much as silhouette. This has direct product development implications: fabric tactility is becoming a purchase driver that rivals visual aesthetics, and brands that can communicate the sensory experience of their materials — through sampling, storytelling, or in-store touch — hold a meaningful conversion advantage. The personal fragrance wardrobe concept, in which consumers layer and rotate scents as they would accessories, is the clearest commercially mature expression of this trend. Brands that treat sensory design as a core competency rather than a marketing layer will compound advantage over time.",
        "source": "trend_intelligence",
        "signal_velocity": 4.5,
        "resolution_question": "Will 'sensorial dressing' or 'neuroaesthetics in fashion' be cited in 3+ major fashion editorial pieces by end of 2026?",
    },
    {
        "name": "Loewe Effect — Small Brand Sentiment Premium",
        "description": "Sentiment quality is outperforming reach as a brand health metric — Loewe's creative director debut generated 30% higher positive sentiment than peer brands despite operating with roughly one-eighth of their social audience size.",
        "ai_score": 7.0,
        "ai_thesis": "The Loewe Effect exposes a measurement gap in how fashion market share is typically assessed: follower count and impression volume capture noise, not conviction, and conviction is what drives full-price purchasing. A brand with a smaller, highly aligned community can dominate the quality of commercial discourse in ways that standard reach metrics systematically undervalue. For prediction market purposes, this pattern is actionable: high-sentiment, lower-reach brands are structurally underpriced in forecasts that weight volume over quality of attention. Identifying the next Loewe — a brand generating disproportionate sentiment positivity before its follower base catches up — is a repeatable alpha signal in fashion market analysis.",
        "source": "social_data",
        "signal_velocity": 3.5,
        "resolution_question": "Will Loewe achieve a 20% increase in brand search volume (per Google Trends) by end of 2026 without a major campaign or celebrity endorsement?",
    },
    {
        "name": "Divisive Trend Signal — High Volume Low Sentiment",
        "description": "Trends generating high conversation volume alongside mixed or negative sentiment show measurably longer commercial lifespans than purely positive trends — the controversy itself functions as a durability mechanism by sustaining ongoing cultural engagement.",
        "ai_score": 6.5,
        "ai_thesis": "The High Volume Low Sentiment pattern inverts a common forecasting instinct: analysts tend to discount polarising trends as fragile, when in practice the controversy sustains attention cycles that purely positive trends exhaust more quickly. Labubu accessories and similarly divisive products maintain search traffic precisely because people keep forming and sharing opinions about them — the debate is the marketing. For fashion prediction markets, this means that calls to short divisive trends on the basis of negative sentiment alone will systematically underperform. The more reliable counter-indicator is when controversy fades to indifference — that is the genuine trend mortality signal, not the presence of mixed sentiment.",
        "source": "social_data",
        "signal_velocity": 2.0,
        "resolution_question": "Will Labubu accessories still be commercially available and actively sold at major streetwear retailers 12 months after their viral peak?",
    },
    {
        "name": "Ralph Lauren Calendar Return — Heritage Brand Revival",
        "description": "Ralph Lauren's return to the official men's fashion calendar in January 2026 — its first scheduled runway in two decades — follows a documented playbook in which strategic absence amplifies re-entry impact, as demonstrated by Calvin Klein's 190% popularity spike on its own NYFW return.",
        "ai_score": 6.8,
        "ai_thesis": "The absence-and-return mechanic is one of the most reliable attention-generation strategies in fashion, and the data pattern holds consistently: controlled withdrawal followed by a high-production re-entry creates a novelty premium that paid media rarely replicates at comparable cost. Ralph Lauren's return arrives with strong tailwinds — American heritage aesthetics are resonating within both the Romanticism Wave and the broader nostalgia cycle — which compounds the structural re-entry effect with genuine trend alignment. The commercial question worth tracking is not whether Ralph Lauren spikes on return (it will) but whether the spike converts into sustained search growth and wholesale expansion, which would signal a durable revival rather than a nostalgia moment. Other heritage brands observing this outcome will accelerate their own return timelines.",
        "source": "social_data",
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


def update_descriptions():
    """Patch description, ai_thesis, and source for existing DB records by trend name."""
    db = SessionLocal()
    updated = 0
    not_found = 0

    for t in TRENDS:
        trend = db.query(Trend).filter(Trend.name == t["name"]).first()
        if not trend:
            not_found += 1
            continue

        trend.description = t["description"]
        trend.ai_thesis = t["ai_thesis"]
        trend.source = t["source"]
        updated += 1

    db.commit()
    db.close()
    print(f"\n✓ {updated} trends updated in DB ({not_found} not found — run run() to seed them)")


if __name__ == "__main__":
    run()
    update_descriptions()
