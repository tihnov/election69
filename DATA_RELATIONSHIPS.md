# Election 69 Data Relationships Report

## Overview

This document describes the structure and relationships between the 7 JSON data files in the Election 69 dataset. This is a Thai election results database using a mixed electoral system (constituency MPs + party list proportional representation).

---

## Data Architecture

### Hierarchical Structure

```
National Level
    ├── Provinces (77 provinces)
    │   └── Constituencies (400+ electoral districts)
    │       └── Candidates (competing for MP seats)
    │
    └── Political Parties (50+ parties)
        ├── Party List Candidates (proportional representation)
        ├── PM Candidates (prime minister nominees)
        └── Constituency Candidates (district-level MPs)
```

---

## File Descriptions & Relationships

### 1. **info_province.json** - Province Master Data

**Purpose**: Master list of all 77 Thai provinces with electoral statistics

**Key Fields**:
- `province_id`: Numeric province identifier
- `prov_id`: Short province code (e.g., "BKK", "SPK", "NBI")
- `province`: Thai province name
- `eng`: English abbreviation
- `total_registered_vote`: Total eligible voters in province
- `total_vote_stations`: Number of polling stations

**Relationships**:
- **Primary Key**: `prov_id`
- **Links to**:
  - `info_constituency.json` via `prov_id`
  - `stats_cons.json` → `result_province[].prov_id`
  - `info_mp_candidate.json` via `mp_app_id` prefix

**Example**:
```json
{
  "province_id": "10",
  "prov_id": "BKK",
  "province": "กรุงเทพมหานคร",
  "eng": "BKK",
  "total_registered_vote": 4502458,
  "total_vote_stations": 6757
}
```

---

### 2. **info_constituency.json** - Constituency Master Data

**Purpose**: Electoral districts (constituencies) within each province

**Key Fields**:
- `cons_id`: Constituency identifier (format: `{prov_id}_{cons_no}`)
- `cons_no`: Constituency number within province
- `prov_id`: Parent province code
- `zone`: Array of district/area names within constituency
- `registered_vote`: Eligible voters in constituency
- `total_vote_stations`: Polling stations in constituency

**Relationships**:
- **Primary Key**: `cons_id`
- **Foreign Key**: `prov_id` → `info_province.json`
- **Links to**:
  - `info_mp_candidate.json` via `cons_id` portion of `mp_app_id`
  - `stats_cons.json` → `result_province[].constituencies[].cons_id`

**Example**:
```json
{
  "cons_id": "BKK_1",
  "cons_no": 1,
  "prov_id": "BKK",
  "zone": ["เขตพระนคร", "เขตดุสิต", "เขตบางรัก"],
  "registered_vote": 130423,
  "total_vote_stations": 239
}
```

---

### 3. **info_party_overview.json** - Political Party Master Data

**Purpose**: Complete list of all registered political parties

**Key Fields**:
- `id`: Party identifier (string number, e.g., "34", "254")
- `party_no`: Party ballot number (string)
- `name`: Party name in Thai
- `abbr`: Party abbreviation
- `color`: Party branding color (hex code)
- `logo_url`: URL to party logo image

**Relationships**:
- **Primary Key**: `id` (referred to as `party_id` in other files)
- **Alternate Key**: `party_no`
- **Links to**:
  - `info_mp_candidate.json` via `mp_app_party_id`
  - `info_party_candidate.json` via `party_no`
  - `stats_cons.json` via `party_id`
  - `stats_party.json` via `party_id`

**Example**:
```json
{
  "id": "34",
  "party_no": "9",
  "name": "เพื่อไทย",
  "abbr": "พท.",
  "color": "#e41e26",
  "logo_url": "https://static-ectreport69.ect.go.th/data/parties/logos/เพื่อไทย.jpg"
}
```

---

### 4. **info_mp_candidate.json** - Constituency Candidate Data

**Purpose**: All candidates running for MP seats in specific constituencies

**Key Fields**:
- `mp_app_id`: Candidate identifier (format: `{cons_id}_{candidate_no}`)
- `mp_app_no`: Candidate number on ballot
- `mp_app_party_id`: Party affiliation (integer)
- `mp_app_name`: Candidate full name
- `image_url`: Candidate portrait photo URL

**Relationships**:
- **Primary Key**: `mp_app_id`
- **Foreign Keys**:
  - Constituency: `cons_id` extracted from `mp_app_id` (e.g., "BKK_1" from "BKK_1_1")
  - Party: `mp_app_party_id` → `info_party_overview.json.id`
- **Links to**:
  - `stats_cons.json` → `result_province[].constituencies[].candidates[].mp_app_id`
  - `stats_party.json` → `result_party[].candidates[].mp_app_id`

**Example**:
```json
{
  "mp_app_id": "BKK_1_1",
  "mp_app_no": 1,
  "mp_app_party_id": 34,
  "mp_app_name": "นายสมชาย วงศ์สวัสดิ์",
  "image_url": "https://static-ectreport69.ect.go.th/data/candidates/portraits/กรุงเทพมหานคร_1_1.jpg"
}
```

---

### 5. **info_party_candidate.json** - Party List & PM Candidates

**Purpose**: Candidates for party list seats (proportional representation) and Prime Minister nominees

**Key Fields**:
- `party_no`: Party ballot number
- `party_list_candidates[]`: Array of party list candidates
  - `list_no`: Position on party list
  - `name`: Candidate name
  - `image_url`: Portrait URL
- `pm_candidates[]`: Array of PM candidates (same structure)

**Relationships**:
- **Foreign Key**: `party_no` → `info_party_overview.json.party_no`
- **Note**: Party list candidates don't compete in constituencies; they get seats based on proportional vote share

**Example**:
```json
{
  "party_no": 9,
  "party_list_candidates": [
    {
      "list_no": 1,
      "name": "นางสาวแพทองธาร ชินวัตร",
      "image_url": "https://cdn.ectscore69.ect.go.th/ect69/candidates/portraits/เพื่อไทย_1.jpg"
    }
  ],
  "pm_candidates": [...]
}
```

---

### 6. **stats_cons.json** - Constituency-Level Voting Statistics

**Purpose**: Detailed voting results organized by geographic hierarchy (national → province → constituency → candidate)

**Structure**:
```
National Summary
└── result_province[] (by province)
    ├── Province-level statistics
    ├── result_party[] (party performance in province)
    └── constituencies[] (by constituency)
        ├── Constituency-level statistics
        ├── candidates[] (individual candidate results)
        └── result_party[] (party performance in constituency)
```

**Key Fields**:

*National/Province/Constituency Level*:
- `turn_out`: Total voters who voted
- `valid_votes`, `invalid_votes`, `blank_votes`: Vote breakdown
- `party_list_turn_out`: Voters for party list ballot
- `party_list_valid_votes`: Valid party list votes
- `counted_vote_stations`: Polling stations counted
- `percent_count`: Percentage of stations reported

*Candidate Level (in constituencies)*:
- `mp_app_id`: Candidate identifier
- `mp_app_vote`: Votes received
- `mp_app_vote_percent`: Percentage of votes
- `mp_app_rank`: Ranking in constituency
- `party_id`: Candidate's party

*Party Level (in constituencies/provinces)*:
- `party_id`: Party identifier
- `party_list_vote`: Party list votes
- `party_cons_votes`: Constituency votes
- `first_mp_app_count`: Number of MPs elected

**Relationships**:
- `prov_id` → `info_province.json.prov_id`
- `cons_id` → `info_constituency.json.cons_id`
- `mp_app_id` → `info_mp_candidate.json.mp_app_id`
- `party_id` → `info_party_overview.json.id`

**Example**:
```json
{
  "turn_out": 34632581,
  "valid_votes": 31951912,
  "result_province": [
    {
      "prov_id": "BKK",
      "turn_out": 2921346,
      "constituencies": [
        {
          "cons_id": "BKK_1",
          "turn_out": 73357,
          "candidates": [
            {
              "mp_app_id": "BKK_1_1",
              "mp_app_vote": 53525,
              "mp_app_rank": 1,
              "party_id": 34
            }
          ]
        }
      ]
    }
  ]
}
```

---

### 7. **stats_party.json** - Party-Level National Statistics

**Purpose**: National voting results organized by political party

**Structure**:
```
National Summary
└── result_party[] (by party)
    ├── Party-level national statistics
    └── candidates[] (all candidates from this party)
```

**Key Fields**:

*Party Level*:
- `party_id`: Party identifier
- `party_vote`: Total party list votes nationally
- `party_vote_percent`: National party list vote percentage
- `party_list_count`: Number of party list MPs allocated
- `mp_app_vote`: Total constituency votes for party's candidates
- `first_mp_app_count`: Number of constituency MPs elected
- `candidates[]`: All party candidates with their results

*Candidate Level (within party)*:
- `mp_app_id`: Candidate identifier
- `mp_app_vote`: Votes received
- `mp_app_vote_percent`: Percentage within constituency
- `mp_app_rank`: Ranking in their constituency
- `party_id`: Party identifier (redundant but present)

**Relationships**:
- `party_id` → `info_party_overview.json.id`
- `mp_app_id` → `info_mp_candidate.json.mp_app_id`

**Example**:
```json
{
  "result_party": [
    {
      "party_id": 34,
      "party_vote": 5158066,
      "party_vote_percent": 14.89368,
      "first_mp_app_count": 58,
      "candidates": [
        {
          "mp_app_id": "BKK_1_1",
          "mp_app_vote": 53525,
          "mp_app_vote_percent": 72.98361,
          "mp_app_rank": 1,
          "party_id": 34
        }
      ]
    }
  ]
}
```

---

## Relationship Diagram

```
┌─────────────────────────┐
│  info_province.json     │
│  (Province Master)      │
│  PK: prov_id            │
└───────┬─────────────────┘
        │ 1:N
        ▼
┌─────────────────────────┐
│  info_constituency.json │
│  (Constituency Master)  │
│  PK: cons_id            │
│  FK: prov_id            │
└───────┬─────────────────┘
        │ 1:N
        ▼
┌─────────────────────────┐       ┌──────────────────────────┐
│  info_mp_candidate.json │◄──────┤  info_party_overview.json│
│  (Constituency Cand.)   │  N:1  │  (Party Master)          │
│  PK: mp_app_id          │       │  PK: id (party_id)       │
│  FK: cons_id (implicit) │       │  AK: party_no            │
│  FK: mp_app_party_id    │       └───────┬──────────────────┘
└───────┬─────────────────┘               │ 1:1
        │                                 ▼
        │                     ┌──────────────────────────┐
        │                     │ info_party_candidate.json│
        │                     │ (Party List & PM Cand.)  │
        │                     │ FK: party_no             │
        │                     └──────────────────────────┘
        │
        ▼
┌─────────────────────────┐       ┌──────────────────────────┐
│   stats_cons.json       │       │   stats_party.json       │
│   (Geographic Stats)    │       │   (Party-Level Stats)    │
│   - References:         │       │   - References:          │
│     • prov_id           │       │     • party_id           │
│     • cons_id           │       │     • mp_app_id          │
│     • mp_app_id         │       │                          │
│     • party_id          │       │   - Aggregates by party  │
│   - Aggregates by geo   │       └──────────────────────────┘
└─────────────────────────┘
```

---

## Key Identifier Patterns

| Identifier | Format | Example | Usage |
|------------|--------|---------|-------|
| `prov_id` | 3-letter code | `BKK`, `SPK`, `NBI` | Province identifier |
| `cons_id` | `{prov_id}_{number}` | `BKK_1`, `SPK_2` | Constituency identifier |
| `mp_app_id` | `{cons_id}_{number}` | `BKK_1_1`, `SPK_2_3` | Candidate identifier |
| `party_id` | Numeric string | `"34"`, `"254"` | Party identifier (primary) |
| `party_no` | Numeric string | `"9"`, `"1"` | Party ballot number |

---

## Thai Electoral System Context

### Two-Ballot System

1. **Constituency Ballot** (Ordinal)
   - Voters select one candidate from their constituency
   - 400 constituency MPs elected (first-past-the-post)
   - Data: `info_mp_candidate.json`, constituency votes in `stats_cons.json`

2. **Party List Ballot** (Proportional)
   - Voters select one political party
   - 100 party list MPs allocated proportionally
   - Data: `info_party_candidate.json`, party list votes in both stats files

### Data Separation

- **Constituency candidates**: Compete for direct seats in `info_mp_candidate.json`
- **Party list candidates**: Receive seats based on party's national vote share in `info_party_candidate.json`
- **PM candidates**: Parties nominate potential Prime Ministers in `info_party_candidate.json`

---

## Common Query Patterns

### 1. Find all candidates in a constituency

```
info_constituency.json → get cons_id
info_mp_candidate.json → filter by mp_app_id starts with cons_id
stats_cons.json → find constituency results with candidates[]
```

### 2. Get party's complete electoral performance

```
info_party_overview.json → get party details by party_id
stats_party.json → find party in result_party[] by party_id
  → Contains: national vote total, all candidates, MP count
```

### 3. Calculate provincial results

```
info_province.json → get prov_id
stats_cons.json → result_province[] find by prov_id
  → Sum all constituencies in province
```

### 4. Identify winning candidate in constituency

```
stats_cons.json → navigate to specific constituency
  → candidates[] → find mp_app_rank: 1
  → get mp_app_id of winner
info_mp_candidate.json → lookup full candidate details
```

---

## Data Integrity Notes

1. **Orphan constituency** (cons_no: 0): Some provinces have a special cons_id with _0 suffix, possibly for overseas/special voters
2. **Null values**: Some fields may be null (e.g., `party_list_count` before allocation)
3. **Percentage rounding**: Vote percentages may not sum to exactly 100% due to rounding
4. **Incomplete counts**: `percent_count` shows some stations haven't reported yet (dataset at 94.33%)
5. **Timestamps**: Both stats files have `last_update` field showing data freshness

---

## File Size & Complexity

| File | Approximate Lines | Complexity |
|------|------------------|------------|
| `info_province.json` | ~700 | Low (flat list) |
| `info_constituency.json` | ~4,800 | Low (flat list) |
| `info_party_overview.json` | ~500 | Low (flat list) |
| `info_mp_candidate.json` | ~24,000 | Low (flat list) |
| `info_party_candidate.json` | ~8,500 | Medium (nested) |
| `stats_cons.json` | **~183,600** | **High (deeply nested)** |
| `stats_party.json` | ~25,000 | Medium (nested) |

**Note**: `stats_cons.json` is the largest and most complex due to its hierarchical structure: National → 77 Provinces → 400+ Constituencies → 50+ Parties × Multiple Candidates

---

## Generated On

February 12, 2026

**Data Source**: Election Commission of Thailand (ECT)  
**Election**: General Election 69  
**Last Update**: 2026-02-10T10:45:50.294Z
