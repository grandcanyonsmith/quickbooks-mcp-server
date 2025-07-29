# Vendor Name Normalization Rules

## Overview
This document defines rules to normalize vendor names from financial transaction data. These rules clean up messy credit card processor descriptions and bank transaction descriptions to create consistent, readable vendor names.

## Rule Categories

### 1. **Pattern-Based Rules**
Rules that match specific patterns in transaction descriptions and extract/normalize vendor names.

### 2. **Keyword Mapping Rules**
Direct keyword matches that map to specific vendor names.

### 3. **Cleanup Rules**
General text cleanup rules applied after pattern and keyword matching.

---

## 1. Pattern-Based Rules

### ACH/Wire Transfer Patterns
```javascript
// BUSINESS TO BUSINESS ACH [Company] [Reference] → Company
"BUSINESS TO BUSINESS ACH Wise Inc WISE 240517..." → "Wise"
"BUSINESS TO BUSINESS ACH" → Extract company name after "ACH "

// Payoneer patterns
"Payoneer Inc. [ID] XXXXX[DIGITS] Payoneer ID: [ID] Pay To: [Name]" → "Payoneer"
```

### Recurring Payment Patterns
```javascript
// RECURRING PAYMENT AUTHORIZED ON [DATE] [VENDOR] [DOMAIN/LOCATION] [STATE] [CARD#]
"RECURRING PAYMENT * ON * [VENDOR_NAME] [DOMAIN] [STATE] *" → Extract VENDOR_NAME

Examples:
"RECURRING PAYMENT ... HIGHLEVEL INC. GOHIGHLEVEL.C TX ..." → "GoHighLevel"
"RECURRING PAYMENT ... OPENAI OPENAI.COM CA ..." → "OpenAI"
"RECURRING PAYMENT ... ADOBE *PREMIERE P 408-536-6000 CA ..." → "Adobe"
```

### Purchase Patterns
```javascript
// PURCHASE AUTHORIZED ON [DATE] [VENDOR] [LOCATION] [CARD#]
"PURCHASE * ON * [VENDOR_NAME] [LOCATION] *" → Extract VENDOR_NAME

Examples:
"PURCHASE ... GOOGLE *ADS5139240 cc@google.com CA ..." → "Google Ads"
"PURCHASE ... CHARGEFLOW.IO CHARGEFLOW.IO DE ..." → "Chargeflow"
```

### PayPal Patterns
```javascript
// PAYPAL *[VENDOR_NAME] [DETAILS]
"PAYPAL *REMOVAL AI XXXXXX7733 SGP ..." → "Removal.ai"
"PAYPAL *INFINITEWE XXXXXX7733 CA ..." → "Infinite"
"PAYPAL *NICHOLASKI XXXXXX7733 WI ..." → "Nicholas (PayPal)"
```

---

## 2. Keyword Mapping Rules

### Software & SaaS Companies
```javascript
const softwareVendorMap = {
    // CRM & Marketing
    "HIGHLEVEL": "GoHighLevel",
    "GOHIGHLEVEL": "GoHighLevel",
    "EXTENDLY": "Extendly",
    "HYROS": "Hyros",
    "MARKETHERO": "Hyros",
    
    // AI & Development
    "OPENAI": "OpenAI",
    "ANTHROPIC": "Anthropic (Claude)",
    "CLAUDE.AI": "Anthropic (Claude)",
    "CURSOR": "Cursor",
    "GITHUB": "GitHub",
    
    // Cloud & Infrastructure
    "CLOUDFLARE": "Cloudflare",
    "VERCEL": "Vercel",
    "GOOGLE": "Google",
    "ZOOM": "Zoom",
    "ZAPIER": "Zapier",
    
    // Design & Media
    "ADOBE": "Adobe",
    "TRINT": "Trint",
    "SCREENSHOT API": "Screenshot API",
    "SCREENSHOTAPI": "Screenshot API",
    
    // Business Tools
    "INTUIT": "Intuit QuickBooks",
    "QBOOKS": "Intuit QuickBooks",
    "QUICKBOOKS": "Intuit QuickBooks",
    "MAKE.COM": "Make",
    "WWW.MAKE.COM": "Make",
    "RAPIDAPI": "RapidAPI",
    "SEGMENT": "Twilio Segment",
    "TWILIO": "Twilio Segment",
    
    // Social & Communication
    "FACEBK": "Meta/Facebook",
    "META": "Meta/Facebook",
    "X CORP": "X (Twitter)",
    "LINKTW": "LinkedIn",
    "LINKEDIN": "LinkedIn",
    
    // Domain & Hosting
    "GODADDY": "GoDaddy",
    "DNH*GODADDY": "GoDaddy",
    "IPINFO": "IPInfo",
    
    // Payment & Finance
    "CHARGEFLOW": "Chargeflow",
    "CURATEDCONNECTOR": "Curated",
    "CURATEDAPPS": "Curated"
};
```

### Payment Processors & Financial
```javascript
const financialVendorMap = {
    "WISE INC": "Wise",
    "WISE": "Wise",
    "PAYONEER": "Payoneer",
    "PAYPAL": "PayPal", // Keep as PayPal unless specific vendor extracted
};
```

### Marketing & Advertising
```javascript
const marketingVendorMap = {
    "DADGUMMARKETING": "DadGum Marketing",
    "FACEBOOK.COM": "Meta/Facebook Ads",
    "GOOGLE ADS": "Google Ads",
    "META ADS": "Meta Ads"
};
```

### Company-Specific Names
```javascript
const companyVendorMap = {
    "COURSE CREATOR 360": "Course Creator 360",
    "COURSECREATOR": "Course Creator 360"
};
```

---

## 3. Cleanup Rules

### Text Normalization
```javascript
// Remove common prefixes
const prefixesToRemove = [
    "RECURRING PAYMENT",
    "AUTHORIZED ON",
    "PURCHASE",
    "BUSINESS TO BUSINESS ACH",
    "DNH*",
    "*"
];

// Remove common suffixes
const suffixesToRemove = [
    "INC.",
    "INC",
    "LLC",
    "CORP.",
    "CORP",
    ".COM",
    ".IO",
    ".AI"
];

// Remove location codes (state abbreviations)
const stateCodesRegex = /\b[A-Z]{2}\s+S[X]+\d+/g;

// Remove card numbers and reference IDs
const cardNumberRegex = /S[X]+\d+/g;
const referenceIdRegex = /\d{6,}/g;

// Remove phone numbers
const phoneRegex = /\d{3}-\d{3}-\d{4}/g;

// Remove URLs
const urlRegex = /(https?:\/\/[^\s]+|[a-z]+\.[a-z]{2,})/gi;
```

### Case Normalization
```javascript
// Convert to proper case
function toProperCase(str) {
    return str.toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
}

// Handle special cases
const specialCaseMap = {
    "ai": "AI",
    "api": "API",
    "crm": "CRM",
    "sms": "SMS",
    "io": "IO",
    "github": "GitHub",
    "paypal": "PayPal",
    "godaddy": "GoDaddy"
};
```

---

## 4. Application Order

The rules should be applied in this specific order:

1. **Pattern-Based Rules** - Extract vendor from structured patterns
2. **Keyword Mapping Rules** - Map known keywords to vendor names
3. **Cleanup Rules** - Remove prefixes, suffixes, and normalize text
4. **Case Normalization** - Apply proper casing
5. **Special Cases** - Handle any remaining edge cases

---

## 5. Implementation Example

```javascript
function normalizeVendorName(description, existingVendor = null) {
    if (!description) return existingVendor || "Unknown Vendor";
    
    let normalized = description.toUpperCase();
    
    // Step 1: Apply pattern-based rules
    normalized = applyPatternRules(normalized);
    
    // Step 2: Apply keyword mapping
    normalized = applyKeywordMapping(normalized);
    
    // Step 3: Apply cleanup rules
    normalized = applyCleanupRules(normalized);
    
    // Step 4: Apply case normalization
    normalized = applyCaseNormalization(normalized);
    
    // Step 5: Handle fallbacks
    return normalized || existingVendor || "Unknown Vendor";
}

// Example usage:
normalizeVendorName("RECURRING PAYMENT AUTHORIZED ON 06/29 HIGHLEVEL INC. GOHIGHLEVEL.C TX SXXXXXXXX0522146 CARD 1933")
// Returns: "GoHighLevel"

normalizeVendorName("BUSINESS TO BUSINESS ACH Wise Inc WISE 240517 First half paym Course Creator Pro Inc")
// Returns: "Wise"

normalizeVendorName("Payoneer Inc. 153956 XXXXX8171 Payoneer ID: 852168171 Pay To: Sayyid Ali Sajjad")
// Returns: "Payoneer"
```

---

## 6. Testing Examples

| Original Description | Expected Result |
|---------------------|----------------|
| `Highlevel Httpsgohighle Tx` | `GoHighLevel` |
| `BUSINESS TO BUSINESS ACH Wise Inc WISE 240517...` | `Wise` |
| `RECURRING PAYMENT ... OPENAI OPENAI.COM CA ...` | `OpenAI` |
| `RECURRING PAYMENT ... ADOBE *PREMIERE P ...` | `Adobe` |
| `RECURRING PAYMENT ... CLOUDFLARE CLOUDFLARE.CO CA ...` | `Cloudflare` |
| `PAYPAL *REMOVAL AI XXXXXX7733 SGP ...` | `Removal.ai` |
| `RECURRING PAYMENT ... COURSE CREATOR 360 COURSECREATOR UT ...` | `Course Creator 360` |
| `RECURRING PAYMENT ... DNH*GODADDY#379312 https://www.g AZ ...` | `GoDaddy` |
| `Payoneer Inc. 153956 XXXXX8171 Payoneer ID: 852168171...` | `Payoneer` |
| `RECURRING PAYMENT ... FACEBK *Meta Verif fb.me/cc CA ...` | `Meta/Facebook` |

This rule set provides a systematic approach to cleaning and normalizing vendor names from financial transaction data.