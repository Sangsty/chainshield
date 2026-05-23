function toNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function getLevelFromScore(score) {
  if (score >= 80) return "Critical";
  if (score >= 50) return "High";
  if (score >= 20) return "Medium";
  return "Low";
}

function ensureArray(value) {
  if (Array.isArray(value)) return value;
  if (typeof value === "string" && value.trim()) return [value];
  return [];
}

export function getRiskTheme(levelOrScore) {
  const level =
    typeof levelOrScore === "number"
      ? getLevelFromScore(levelOrScore)
      : String(levelOrScore || "Low");

  const normalized = level.toLowerCase();

  if (normalized.includes("critical")) {
    return {
      label: "Critical",
      hex: "#ef4444",
      text: "text-red-300",
      strongText: "text-red-400",
      badge: "border-red-400/30 bg-red-500/15 text-red-200",
      soft: "bg-red-500/10",
      border: "border-red-400/25",
      progress: "bg-red-500",
    };
  }

  if (normalized.includes("high")) {
    return {
      label: "High",
      hex: "#fb923c",
      text: "text-orange-300",
      strongText: "text-orange-400",
      badge: "border-orange-400/30 bg-orange-500/15 text-orange-200",
      soft: "bg-orange-500/10",
      border: "border-orange-400/25",
      progress: "bg-orange-500",
    };
  }

  if (normalized.includes("medium")) {
    return {
      label: "Medium",
      hex: "#facc15",
      text: "text-yellow-200",
      strongText: "text-yellow-300",
      badge: "border-yellow-400/30 bg-yellow-500/15 text-yellow-100",
      soft: "bg-yellow-500/10",
      border: "border-yellow-400/25",
      progress: "bg-yellow-400",
    };
  }

  return {
    label: "Low",
    hex: "#22c55e",
    text: "text-emerald-300",
    strongText: "text-emerald-400",
    badge: "border-emerald-400/30 bg-emerald-500/15 text-emerald-200",
    soft: "bg-emerald-500/10",
    border: "border-emerald-400/25",
    progress: "bg-emerald-400",
  };
}

function extractCategoryBreakdown(raw) {
  const risk = raw?.risk || {};

  const source =
    risk.category_breakdown ||
    raw.category_breakdown ||
    risk.score_breakdown ||
    raw.score_breakdown ||
    {};

  return {
    contract_risk: toNumber(source.contract_risk),
    liquidity_risk: toNumber(source.liquidity_risk),
    holder_risk: toNumber(source.holder_risk),
    honeypot_risk: toNumber(source.honeypot_risk),
    creator_risk: toNumber(source.creator_risk),
    event_risk: toNumber(source.event_risk),
    safety_adjustments: toNumber(source.safety_adjustments),
  };
}

export function normalizeReport(rawReport) {
  const raw = rawReport || {};

  const token = raw.token || {};
  const contract = raw.contract || {};
  const creator = raw.creator || {};
  const holder = raw.holder_analysis || {};
  const liquidity = raw.liquidity_analysis || {};
  const events = raw.event_analysis || raw.event_log_analysis || {};
  const honeypot = raw.honeypot_analysis || {};
  const risk = raw.risk || {};

  const categoryBreakdown = extractCategoryBreakdown(raw);

  const riskScore = toNumber(
    risk.score ??
      raw.risk_score ??
      raw.score ??
      raw.final_score ??
      raw.total_score,
    0
  );

  const riskLevel =
    risk.level || raw.risk_level || raw.level || getLevelFromScore(riskScore);

  return {
    raw,
    riskScore,
    riskLevel,

    token: {
      address: token.address || raw.token_address || "",
      name: token.name || "Unknown Token",
      symbol: token.symbol || "N/A",
      decimals: token.decimals ?? "N/A",
      totalSupply: token.total_supply ?? token.totalSupply ?? null,
    },

    contract: {
      verified: Boolean(contract.verified),
      compilerVersion: contract.compiler_version || "N/A",
      isProxy: Boolean(contract.is_proxy),
      implementationAddress: contract.implementation_address || null,
      dangerousFunctions: contract.dangerous_functions_found || [],
    },

    creator: {
      address:
        creator.creator_address ||
        creator.address ||
        creator.deployer_address ||
        "Not available",
      creationTxHash:
        creator.creation_tx_hash || creator.tx_hash || "Not available",
    },

    holder: {
      top10Percentage: holder.top_10_percentage ?? 0,
      holderCount: holder.holder_count ?? 0,
      whaleRisk: holder.whale_risk || "Unknown",
    },

    liquidity: {
      found: Boolean(liquidity.liquidity_found),
      locked: Boolean(liquidity.liquidity_locked),
      risk: liquidity.liquidity_risk || "Low",
      pairAddress: liquidity.pair_address || "Not available",
    },

    events: {
      mintEvents: events.mint_count ?? 0,
      burnEvents: events.burn_count ?? 0,
      transferCount: events.transfer_count ?? 0,
      suspiciousEvents: events.suspicious_events || [],
    },

    honeypot: {
      risk: honeypot.honeypot_risk || "Unknown",
      transferRestrictions: Boolean(honeypot.transfer_restrictions_detected),
      signalsFound: honeypot.signals_found || [],
      notes: honeypot.notes || [],
    },

    explanations: ensureArray(
      risk.reasons || raw.explanations || raw.red_flags || raw.warnings
    ),

    categoryBreakdown,
  };
}

export const demoReport = normalizeReport({
  token: {
    address: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    name: "Tether USD",
    symbol: "USDT",
    decimals: 6,
    total_supply: 97071875962.55351,
  },
  contract: {
    verified: true,
    compiler_version: "v0.4.18+commit.9cf6e910",
    is_proxy: false,
    implementation_address: null,
    dangerous_functions_found: [
      "issue",
      "blacklist",
      "pause",
      "transferownership",
    ],
  },
  creator: {
    creator_address: "0x36928500bc1dcd7af6a2b4008875cc336b927d57",
    creation_tx_hash:
      "0x2f1c5c2b44f771e942a8506148e256f94f1a464babc938ae0690c6e34ca79190",
  },
  holder_analysis: {
    top_10_percentage: 0,
    holder_count: 0,
  },
  liquidity_analysis: {
    liquidity_found: true,
    liquidity_locked: false,
    liquidity_risk: "Low",
  },
  event_analysis: {
    mint_count: 0,
    burn_count: 0,
    transfer_count: 0,
    suspicious_events: [],
  },
  honeypot_analysis: {
    honeypot_risk: "Medium",
    transfer_restrictions_detected: true,
    signals_found: ["blacklist", "isBlacklisted"],
  },
  risk: {
    score: 65,
    level: "High",
    reasons: [
      "Blacklist-related function detected.",
      "Pause functionality detected.",
      "Minting capability detected.",
      "Ownership transfer capability detected.",
      "Creator wallet identified for deployer tracking.",
      "Moderate honeypot-style transfer restriction risk detected.",
    ],
    category_breakdown: {
      contract_risk: 53,
      holder_risk: 0,
      liquidity_risk: 0,
      event_risk: 0,
      honeypot_risk: 12,
      creator_risk: 0,
      safety_adjustments: 0,
    },
  },
});