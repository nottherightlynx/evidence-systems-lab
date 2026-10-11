# Source inventory — Pages 2–3

All internal-looking sources are **fictional**. Never add real CFLeads, ACLU, voter, donor, or constituent records.

| Source ID | Domain | File or URL | Coverage | Provenance / authority | Allowed for public portfolio? | Expected refresh |
|---|---|---|---|---|---|---|
| LEGACY_CRM | Constituent identities | data/synthetic/raw_constituents.csv | Fictional US sample | Synthetic, created in bootstrap script | Yes | Manual demo |
| NEW_CRM | Constituent identities | data/synthetic/raw_constituents.csv | Fictional US sample | Synthetic, created in bootstrap script | Yes | Manual demo |
| ENGAGEMENT_APP | Registrations and attendance | data/synthetic/raw_engagements.csv | Synthetic DC/MD/VA | Synthetic, created in bootstrap script | Yes | Manual demo |
| DONATION_PROCESSOR | Contributions and refunds | data/synthetic/raw_contributions.csv | Synthetic DC/MD | Synthetic, created in bootstrap script | Yes | Manual demo |
| FEDERAL_REGISTER | Public-document metadata | https://www.federalregister.gov/developers/documentation/api/v1 | US federal | Federal Register API documentation | Metadata and citation only | Daily, for later project |

**Current phase:** Only synthetic CSVs are loaded. Federal Register is a registered future source, not yet ingested.
