**Project Blueprint: LinkedIn Company Analysis Tool**
=====================================================

**1\. Architecture**
--------------------

The application will be a **Streamlit** web app with a modular backend. It will use a configuration-driven design, where a CompanyConfig class is the central object passed through the pipeline.

**2\. High-Level Phases**
-------------------------

*   **Foundation & Configuration Core:** Set up the project, define the company configuration schema, and build the core validation logic.
    
*   **Mock Data Collection & Processing:** Build and test the data processing pipeline using mock data, avoiding LinkedIn API complexities initially.
    
*   **NLP Analysis Modules:** Implement and integrate the core NLP analysis functions (Sentiment, NER, Topics).
    
*   **Streamlit Web Interface:** Build the UI, integrating all previous components and adding export functionality.
    
*   **Integration with Real Data Source:** Replace the mock data collector with a real LinkedIn data source (e.g., API wrapper or scraper).
    
*   **Productionization:** Add authentication, monitoring, error handling, and deployment configuration.
    

### **Phase 1: Foundation & Configuration Core**

This phase establishes the project structure and the heart of the application: the company configuration model.

#### **Chunk 1.1: Project Setup & CompanyConfig Pydantic Model**

*   **Atomic Step 1.1.1:** Initialize a new Python project with a requirements.txt containing pydantic, pytest, python-dotenv. Create the initial project structure.
    
*   **Atomic Step 1.1.2:** Define the CompanyConfig Pydantic model in config.py based on the provided JSON schema. This model will handle validation.
    
*   **Atomic Step 1.1.3:** Write unit tests for the CompanyConfig model, testing valid inputs and invalid inputs (e.g., invalid URL, missing name).
    

#### **Chunk 1.2: Configuration Manager**

*   **Atomic Step 1.2.1:** Create a ConfigManager class with methods to save(config: CompanyConfig, filename) and load(filename) -> CompanyConfig using JSON.
    
*   **Atomic Step 1.2.2:** Write tests for ConfigManager to ensure configurations are correctly serialized and deserialized without data loss.
    

**Validation Demo:** A working Python script that creates a CompanyConfig object for a test company (e.g., "Apple Inc."), validates it, saves it to a JSON file, loads it back, and validates again. All tests pass.

### **Phase 2: Mock Data Collection & Processing**

Build the pipeline's structure with fake data to validate the flow before dealing with real data.

#### **Chunk 2.1: Data Models & Mock Collector**

*   **Atomic Step 2.1.1:** Define a Post Pydantic model in models.py (e.g., text, date, author, url, likes).
    
*   **Atomic Step 2.1.2:** Create an abstract base class BaseCollector with a method def fetch\_posts(config: CompanyConfig) -> List\[Post\]:.
    
*   **Atomic Step 2.1.3:** Implement a MockCollector that inherits from BaseCollector. It should generate a list of fake Post objects using the company name and aliases from the provided CompanyConfig.
    

#### **Chunk 2.2: Data Cleaning Processor**

*   **Atomic Step 2.2.1:** Create a DataProcessor class with a clean\_posts(posts: List\[Post\], config: CompanyConfig) -> List\[Post\] method. Initially, it should just lowercase the text and filter by the configured languages using a simple keyword check.
    
*   **Atomic Step 2.2.2:** Write tests for DataProcessor.clean\_posts, ensuring it filters languages correctly and handles empty lists.
    

**Validation Demo:** A script that loads a CompanyConfig, uses the MockCollector to generate fake posts, and then runs them through the DataProcessor. Print the input and output to show the cleaning process. All tests pass.

### **Phase 3: NLP Analysis Modules**

Implement the core value-add features. We'll start with simple, rule-based methods and later replace them with ML models.

#### **Chunk 3.1: Sentiment Analysis**

*   **Atomic Step 3.1.1:** Create an NLPProcessor class. Add a method analyze\_sentiment(posts: List\[Post\]) -> List\[Post\] that adds a sentiment: float field to each post. Use a very simple rule-based approach.
    
*   **Atomic Step 3.1.2:** Write tests for the analyze\_sentiment method with posts containing known positive and negative words.
    

#### **Chunk 3.2: Topic Detection (Keyword Extraction)**

*   **Atomic Step 3.2.1:** Add a method extract\_topics(posts: List\[Post\], config: CompanyConfig) -> Dict\[str, int\] to the NLPProcessor. It should return a frequency count of significant words (stopwords removed), prioritizing the company's keywords and hashtags.
    
*   **Atomic Step 3.2.2:** Test extract\_topics with mock posts containing the company's keywords and ensure they are ranked highly.
    

**Validation Demo:** A script that runs the mock posts through both analyze\_sentiment and extract\_topics and prints the results, showing sentiments per post and a topic frequency dictionary.

### **Phase 4: Streamlit Web Interface**

Integrate the components into a cohesive UI. Build the interface incrementally.

#### **Chunk 4.1: Company Configuration UI**

*   **Atomic Step 4.1.1:** Set up a basic Streamlit app (app.py). Create a form using st.form that collects inputs for the CompanyConfig (name, aliases, domain, etc.).
    
*   **Atomic Step 4.1.2:** On form submission, validate the inputs by creating a CompanyConfig object. Display validation errors from Pydantic in the UI.
    

#### **Chunk 4.2: Analysis Dashboard UI**

*   **Atomic Step 4.2.1:** Add a button to trigger the analysis. When clicked, the app should run the full pipeline: MockCollector -> DataProcessor -> NLPProcessor.
    
*   **Atomic Step 4.2.2:** Display the results using Streamlit components: show a table of posts, a bar chart of topic frequencies (st.bar\_chart), and a summary statistic for average sentiment.
    

#### **Chunk 4.3: Export and Save Configuration**

*   **Atomic Step 4.3.1:** Add a button to export the results as a CSV using st.download\_button. The filename should incorporate the company.name.
    
*   **Atomic Step 4.3.2:** Add a button to save the CompanyConfig using the ConfigManager.
    

**Validation Demo:** A fully interactive Streamlit app. The user can input a company configuration, run a mock analysis, see the results visually, and download a CSV. This is a complete, demo-ready prototype.