# ✅ TODO: LinkedIn Company Analysis Tool

A structured checklist to track progress across all phases of the project.

---

## Phase 1: Foundation & Configuration Core

### Chunk 1.1: Project Setup & CompanyConfig Pydantic Model
- [ ] **1.1.1** Initialize new Python project with `pyproject.toml`
  - [ ] Add dependencies: `pydantic`, `pytest`, `python-dotenv`
  - [ ] Create initial project structure (`src/`, `tests/`, etc.)
- [ ] **1.1.2** Define `CompanyConfig` Pydantic model in `config.py`
  - [ ] Include validation rules (name, domain, aliases, languages, etc.)
- [ ] **1.1.3** Write unit tests for `CompanyConfig`
  - [ ] Test valid inputs
  - [ ] Test invalid inputs (e.g., invalid URL, missing fields)

### Chunk 1.2: Configuration Manager
- [ ] **1.2.1** Create `ConfigManager` class
  - [ ] Implement `save(config: CompanyConfig, filename)`
  - [ ] Implement `load(filename) -> CompanyConfig`
- [ ] **1.2.2** Write tests for `ConfigManager`
  - [ ] Verify correct serialization
  - [ ] Verify deserialization without data loss

### Validation Demo
- [ ] Script to:
  - [ ] Create a `CompanyConfig` for a test company (e.g., Apple Inc.)
  - [ ] Validate -> Save -> Load -> Re-validate
  - [ ] Ensure all tests pass

### Documentation
- [ ] Implementation Doc: describe config schema, validation, and manager logic
- [ ] Test Doc: outline test coverage for `CompanyConfig` + `ConfigManager`
- [ ] Demo Doc: show how to run the validation script

---

## Phase 2: Mock Data Collection & Processing

### Chunk 2.1: Data Models & Mock Collector
- [ ] **2.1.1** Define `Post` Pydantic model in `models.py`
  - [ ] Fields: `text`, `date`, `author`, `url`, `likes`
- [ ] **2.1.2** Create abstract class `BaseCollector`
  - [ ] Method: `fetch_posts(config: CompanyConfig) -> List[Post]`
- [ ] **2.1.3** Implement `MockCollector` (inherits from `BaseCollector`)
  - [ ] Generate fake posts using company name and aliases

### Chunk 2.2: Data Cleaning Processor
- [ ] **2.2.1** Create `DataProcessor` class
  - [ ] Method: `clean_posts(posts, config) -> List[Post]`
  - [ ] Lowercase text, filter by languages
- [ ] **2.2.2** Write tests for `DataProcessor`
  - [ ] Validate language filtering
  - [ ] Handle empty lists

### Validation Demo
- [ ] Script to:
  - [ ] Load `CompanyConfig`
  - [ ] Use `MockCollector` → generate posts
  - [ ] Run `DataProcessor` → clean posts
  - [ ] Print input/output
  - [ ] Ensure all tests pass

### Documentation
- [ ] Implementation Doc: describe `Post` model, collectors, and processors
- [ ] Test Doc: outline test strategy for collectors & processors
- [ ] Demo Doc: show how to run mock collection and cleaning

---

## Phase 3: NLP Analysis Modules

### Chunk 3.1: Sentiment Analysis
- [ ] **3.1.1** Create `NLPProcessor` class
  - [ ] Add `analyze_sentiment(posts) -> List[Post]`
  - [ ] Append `sentiment: float` to posts
- [ ] **3.1.2** Write tests for `analyze_sentiment`
  - [ ] Positive/negative word detection

### Chunk 3.2: Topic Detection (Keyword Extraction)
- [ ] **3.2.1** Add `extract_topics(posts, config) -> Dict[str, int]`
  - [ ] Remove stopwords
  - [ ] Count frequencies
  - [ ] Prioritize company keywords & hashtags
- [ ] **3.2.2** Test `extract_topics`
  - [ ] Ensure company keywords are ranked highly

### Validation Demo
- [ ] Script to:
  - [ ] Run mock posts through `analyze_sentiment`
  - [ ] Run mock posts through `extract_topics`
  - [ ] Print sentiments + frequency dictionary

### Documentation
- [ ] Implementation Doc: explain NLP pipeline & logic for sentiment + topics
- [ ] Test Doc: detail test inputs/outputs for NLP modules
- [ ] Demo Doc: guide to running sentiment & topic demo

---

## Phase 4: Streamlit Web Interface

### Chunk 4.1: Company Configuration UI
- [ ] **4.1.1** Create `app.py` with Streamlit
  - [ ] Form (`st.form`) for CompanyConfig inputs
- [ ] **4.1.2** Validate inputs in UI
  - [ ] Show Pydantic validation errors in Streamlit

### Chunk 4.2: Analysis Dashboard UI
- [ ] **4.2.1** Add “Run Analysis” button
  - [ ] Execute pipeline: `MockCollector -> DataProcessor -> NLPProcessor`
- [ ] **4.2.2** Display results
  - [ ] Table of posts
  - [ ] Bar chart of topics (`st.bar_chart`)
  - [ ] Summary statistic (average sentiment)

### Chunk 4.3: Export and Save Configuration
- [ ] **4.3.1** Add export button
  - [ ] Download results as CSV (`st.download_button`)
  - [ ] Filename includes `company.name`
- [ ] **4.3.2** Add button to save CompanyConfig
  - [ ] Use `ConfigManager`

### Validation Demo
- [ ] Interactive Streamlit app:
  - [ ] Input configuration
  - [ ] Run mock analysis
  - [ ] Visualize results
  - [ ] Export CSV
  - [ ] Save config
  - [ ] Prototype demo-ready

### Documentation
- [ ] Implementation Doc: describe Streamlit architecture & UI flows
- [ ] Test Doc: outline UI validation, button functionality, export flow
- [ ] Demo Doc: walkthrough for demoing the Streamlit app

---

## Phase 5: Integration with Real Data Source (Future)
- [ ] Replace `MockCollector` with real LinkedIn data source
- [ ] Implement API wrapper or scraper
- [ ] Update pipeline tests with real data

### Validation Demo
- [ ] Script/UI to:
  - [ ] Load a real company configuration
  - [ ] Fetch live LinkedIn posts
  - [ ] Run them through `DataProcessor` + `NLPProcessor`
  - [ ] Compare mock vs real outputs
  - [ ] Ensure consistent results

### Documentation
- [ ] Implementation Doc: detail real data integration & handling
- [ ] Test Doc: describe live data test strategy & reliability checks
- [ ] Demo Doc: instructions for running live data demo

---

## Phase 6: Productionization (Future)
- [ ] Add authentication (user login, sessions)
- [ ] Add monitoring (logging, error tracking)
- [ ] Add error handling (graceful fallbacks)
- [ ] Set up deployment (Docker, CI/CD, hosting)

### Validation Demo
- [ ] Deploy a staging version
  - [ ] Test authentication workflow
  - [ ] Verify monitoring dashboards/logging
  - [ ] Trigger error cases for resilience testing
  - [ ] Confirm deployment pipeline runs end-to-end

### Documentation
- [ ] Implementation Doc: describe production setup, auth, monitoring
- [ ] Test Doc: document test coverage for productionization features
- [ ] Demo Doc: step-by-step guide for staging demo

---
