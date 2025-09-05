"""Step 4 Demo: Basic NLP Processing Pipeline

This demo showcases the core NLP functionality for analyzing LinkedIn posts,
including sentiment analysis, topic detection, named entity recognition,
and the complete processing pipeline.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from linkedin_analyzer.models.company import CompanyConfiguration, CompanyProfile, AnalysisSettings
    from linkedin_analyzer.models.linkedin_data import LinkedInPost, LinkedInProfile, EngagementMetrics, PostType, ContentSource
    from linkedin_analyzer.storage.memory_storage import CompanyConfigStorage
    from linkedin_analyzer.services.collection_service import LinkedInCollectionService
    from linkedin_analyzer.services.data_collector import MockDataCollector
    from linkedin_analyzer.services.analysis_service import AnalysisService
    from linkedin_analyzer.nlp.processing_pipeline import PipelineConfig
    from linkedin_analyzer.nlp.sentiment_analyzer import SentimentAnalyzer, SentimentMethod
    from linkedin_analyzer.nlp.topic_extractor import TopicExtractor
    from linkedin_analyzer.nlp.entity_recognizer import EntityRecognizer
    from linkedin_analyzer.nlp.processing_pipeline import NLPPipeline
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root and dependencies are installed")
    sys.exit(1)

from datetime import datetime
import time


def print_banner(title: str):
    """Print a banner for demo sections."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_section(title: str):
    """Print a section header."""
    print(f"\n📋 {title}")
    print("-" * 50)


def demo_sentiment_analysis():
    """Demonstrate sentiment analysis capabilities."""
    print_banner("SENTIMENT ANALYSIS DEMO")
    
    # Initialize sentiment analyzer
    analyzer = SentimentAnalyzer()
    
    # Test different sentiment examples
    test_texts = [
        ("Positive", "I absolutely love working at this amazing company! The team is incredible and the projects are so exciting. Best workplace ever!"),
        ("Negative", "Terrible experience with this company. Poor management, awful work environment, and no career growth opportunities. Waste of time."),
        ("Neutral", "The quarterly meeting is scheduled for next Tuesday at 2 PM. Please review the agenda beforehand and prepare your reports."),
        ("Mixed", "The company has great benefits and compensation, but the work-life balance could be improved. Management is hit or miss."),
    ]
    
    print(f"Available sentiment methods: {analyzer.get_available_methods()}")
    print()
    
    for sentiment_type, text in test_texts:
        print(f"🔍 Analyzing {sentiment_type} Text:")
        print(f"Text: \"{text[:80]}{'...' if len(text) > 80 else ''}\"")
        
        result = analyzer.analyze_text(text)
        
        if result:
            print(f"   Sentiment: {result.label.value.upper()}")
            print(f"   Score: {result.score:.3f}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Method: {result.method}")
        else:
            print("   ❌ Analysis failed")
        print()


def demo_topic_extraction():
    """Demonstrate topic extraction capabilities."""
    print_banner("TOPIC EXTRACTION DEMO")
    
    # Initialize topic extractor
    extractor = TopicExtractor(n_topics=3)
    
    # Sample business/tech texts
    sample_texts = [
        "Our company is launching an innovative AI-powered analytics platform for enterprise customers.",
        "The artificial intelligence revolution is transforming how businesses analyze customer data.",
        "Machine learning algorithms help companies process information and make data-driven decisions.",
        "Business intelligence tools powered by AI provide valuable insights for strategic planning.",
        "Our data science team develops cutting-edge software solutions using advanced technologies.",
        "Customer analytics and market research drive our product development and business strategy.",
        "The latest technology trends show increased adoption of AI and machine learning platforms.",
        "Data-driven decision making is crucial for modern businesses in competitive markets.",
    ]
    
    print(f"Available topic extraction methods: {extractor.get_available_methods()}")
    print(f"Analyzing {len(sample_texts)} sample texts...")
    print()
    
    # Extract topics
    start_time = time.time()
    topics = extractor.extract_topics(sample_texts)
    processing_time = time.time() - start_time
    
    if topics:
        print(f"✅ Found {len(topics)} topics (processed in {processing_time:.2f}s):")
        print()
        
        for i, topic in enumerate(topics, 1):
            print(f"📌 Topic {i}: {topic.topic_name}")
            print(f"   Relevance: {topic.relevance_score:.3f}")
            print(f"   Confidence: {topic.confidence:.3f}")
            print(f"   Method: {topic.method}")
            print(f"   Keywords: {', '.join(topic.keywords[:8])}")
            print()
    else:
        print("❌ No topics extracted")
    
    # Demonstrate keyword extraction
    print_section("Keyword Extraction")
    keywords = extractor.extract_keywords_from_texts(sample_texts, max_keywords=10)
    
    if keywords:
        print(f"🔑 Top {len(keywords)} keywords: {', '.join(keywords)}")
    else:
        print("❌ No keywords extracted")


def demo_entity_recognition():
    """Demonstrate named entity recognition capabilities.""" 
    print_banner("NAMED ENTITY RECOGNITION DEMO")
    
    # Initialize entity recognizer
    recognizer = EntityRecognizer()
    
    # Test texts with various entity types
    test_texts = [
        ("Business Text", "John Smith, CEO of Microsoft, announced a $5 billion investment in AI research. The Seattle-based company will expand its operations."),
        ("Financial Text", "Apple reported quarterly revenue of $89.5 billion, up 15% from last year. The stock price increased 8% after the announcement."),
        ("Event Text", "Sarah Johnson from Google will speak at the Technology Summit 2024 in San Francisco on March 15th about machine learning innovations."),
        ("Product Text", "Amazon launched its new cloud computing service, AWS Analytics Pro, targeting enterprise customers in North America and Europe."),
    ]
    
    print(f"Available NER methods: {recognizer.get_available_methods()}")
    print()
    
    for text_type, text in test_texts:
        print(f"🔍 Analyzing {text_type}:")
        print(f"Text: \"{text}\"")
        print()
        
        # Extract entities
        start_time = time.time()
        entities = recognizer.extract_entities(text, company_context="Microsoft")
        processing_time = time.time() - start_time
        
        if entities:
            print(f"✅ Found {len(entities)} entities (processed in {processing_time:.3f}s):")
            
            # Group entities by type
            entities_by_type = {}
            for entity in entities:
                if entity.entity_type not in entities_by_type:
                    entities_by_type[entity.entity_type] = []
                entities_by_type[entity.entity_type].append(entity)
            
            for entity_type, type_entities in entities_by_type.items():
                print(f"   {entity_type.value}:")
                for entity in type_entities:
                    print(f"     - {entity.entity_text} (confidence: {entity.confidence:.3f})")
        else:
            print("   ❌ No entities found")
        print()


def demo_processing_pipeline():
    """Demonstrate the complete NLP processing pipeline."""
    print_banner("NLP PROCESSING PIPELINE DEMO")
    
    # Initialize pipeline with custom config
    config = PipelineConfig(
        max_topics_per_text=3,
        min_texts_for_topics=3,
        enable_parallel_processing=False,  # Disabled for demo clarity
        detect_language=True
    )
    
    pipeline = NLPPipeline(config)
    
    # Check pipeline component status
    print("🔧 Pipeline Component Status:")
    status = pipeline.get_component_status()
    for component, available in status.items():
        if isinstance(available, bool):
            status_icon = "✅" if available else "❌"
            print(f"   {component}: {status_icon}")
        else:
            print(f"   {component}_methods: {available}")
    print()
    
    # Create sample LinkedIn posts with proper schema
    sample_posts = [
        LinkedInPost(
            post_id="post_1",
            author=LinkedInProfile(
                profile_id="alice-chen-123",
                name="Alice Chen",
                headline="AI Product Manager at TechCorp",
                company="TechCorp",
                position="AI Product Manager",
                location="San Francisco, CA",
                is_company_employee=True
            ),
            content="Excited to announce our new AI product launch! This innovative solution will revolutionize data analytics for enterprises. #AI #innovation #technology",
            published_at=datetime.now(),
            engagement=EngagementMetrics(likes=125, comments=23, shares=15),
            post_type=PostType.POST,
            source=ContentSource.EMPLOYEE_POST,
            company_mentioned=True,
            hashtags=["#AI", "#innovation", "#technology"]
        ),
        LinkedInPost(
            post_id="post_2", 
            author=LinkedInProfile(
                profile_id="bob-martinez-456",
                name="Bob Martinez",
                headline="Senior Developer at TechCorp",
                company="TechCorp",
                position="Senior Developer",
                location="New York, NY",
                is_company_employee=True
            ),
            content="Unfortunately disappointed with recent company changes. The new policies are affecting team morale and productivity. We need better communication from leadership.",
            published_at=datetime.now(),
            engagement=EngagementMetrics(likes=45, comments=67, shares=8),
            post_type=PostType.POST,
            source=ContentSource.EMPLOYEE_POST,
            company_mentioned=True
        ),
        LinkedInPost(
            post_id="post_3",
            author=LinkedInProfile(
                profile_id="carol-davis-789",
                name="Carol Davis",
                headline="CFO at TechCorp",
                company="TechCorp",
                position="Chief Financial Officer",
                location="Boston, MA",
                is_company_employee=True
            ),
            content="Quarterly results show steady growth. Revenue increased 12% to $150 million. Our data science team contributed significantly to business intelligence improvements.",
            published_at=datetime.now(),
            engagement=EngagementMetrics(likes=89, comments=12, shares=22),
            post_type=PostType.POST,
            source=ContentSource.COMPANY_PAGE,
            company_mentioned=True
        ),
        LinkedInPost(
            post_id="post_4",
            author=LinkedInProfile(
                profile_id="david-kim-101",
                name="David Kim",
                headline="Software Engineer at StartupCo",
                company="StartupCo",
                position="Software Engineer",
                location="Austin, TX",
                is_company_employee=False
            ),
            content="Great networking event last night! Met amazing professionals from Microsoft, Google, and Amazon. The future of machine learning looks bright. #networking #ML",
            published_at=datetime.now(),
            engagement=EngagementMetrics(likes=78, comments=19, shares=11),
            post_type=PostType.POST,
            source=ContentSource.COMPANY_MENTION,
            company_mentioned=False,
            hashtags=["#networking", "#ML"]
        ),
    ]
    
    print(f"📊 Processing {len(sample_posts)} LinkedIn posts...")
    print()
    
    # Process posts through pipeline
    start_time = time.time()
    results = pipeline.process_posts_batch(sample_posts, company_context="TechCorp")
    processing_time = time.time() - start_time
    
    print(f"✅ Processed {len(results)}/{len(sample_posts)} posts successfully")
    print(f"   Total processing time: {processing_time:.2f} seconds")
    print(f"   Average time per post: {processing_time/len(sample_posts):.3f} seconds")
    print()
    
    # Display results for each post
    for i, result in enumerate(results, 1):
        print(f"📝 Post {i}: {result.post_id}")
        print(f"   Text: \"{sample_posts[i-1].content[:80]}...\"")
        
        # Sentiment
        if result.sentiment:
            print(f"   Sentiment: {result.sentiment.label.value.upper()} "
                  f"(score: {result.sentiment.score:.3f}, "
                  f"confidence: {result.sentiment.confidence:.3f})")
        
        # Topics  
        if result.topics:
            topic_names = [topic.topic_name for topic in result.topics[:2]]
            print(f"   Topics: {', '.join(topic_names)}")
        
        # Entities
        if result.entities:
            entities_summary = {}
            for entity in result.entities[:5]:  # Top 5 entities
                if entity.entity_type not in entities_summary:
                    entities_summary[entity.entity_type] = []
                entities_summary[entity.entity_type].append(entity.entity_text)
            
            for entity_type, texts in entities_summary.items():
                print(f"   {entity_type.value}: {', '.join(texts)}")
        
        # Processing stats
        if result.processing_time_ms:
            print(f"   Processing time: {result.processing_time_ms:.1f}ms")
        
        if result.language:
            print(f"   Language: {result.language}")
        
        print()
    
    # Display processing statistics
    print_section("Processing Statistics")
    stats = pipeline.get_processing_stats()
    print(f"Success rates:")
    print(f"   Sentiment analysis: {stats['success_rates']['sentiment']:.1%}")
    print(f"   Topic extraction: {stats['success_rates']['topics']:.1%}")
    print(f"   Entity recognition: {stats['success_rates']['entities']:.1%}")
    
    if stats['error_count'] > 0:
        print(f"Errors encountered: {stats['error_count']}")


def demo_analysis_service():
    """Demonstrate the complete analysis service."""
    print_banner("ANALYSIS SERVICE DEMO")
    
    # Initialize services
    storage = CompanyConfigStorage()
    mock_collector = MockDataCollector()
    collection_service = LinkedInCollectionService(collector=mock_collector)
    analysis_service = AnalysisService(collection_service, storage)
    
    # Create company configuration
    company_profile = CompanyProfile(
        name="DemoTech Corp",
        linkedin_url="https://www.linkedin.com/company/demotech",
        aliases=["DemoTech", "Demo Technology"],
        email_domain="demotech.com",
        hashtags=["#demotech", "#innovation"],
        keywords=["technology", "AI", "software"],
        industry="Technology",
        size="medium"
    )
    
    analysis_settings = AnalysisSettings(
        date_range="30d",
        include_employees=True,
        include_mentions=True,
        sentiment_threshold=0.1,
        languages=["en"]
    )
    
    company_config = CompanyConfiguration(
        profile=company_profile,
        settings=analysis_settings
    )
    
    # Store company configuration
    stored_config = storage.create(company_config)
    print(f"✅ Company configuration created: {stored_config.profile.name}")
    print()
    
    # Analyze company posts
    print("🔄 Starting company analysis...")
    start_time = time.time()
    
    summary = analysis_service.analyze_company_posts(
        company_name=company_profile.name,
        force_refresh=True
    )
    
    analysis_time = time.time() - start_time
    
    if summary:
        print(f"✅ Analysis completed in {analysis_time:.2f} seconds")
        print()
        
        # Display analysis summary
        print_section("Analysis Summary")
        print(f"Company: {summary.company_name}")
        print(f"Posts analyzed: {summary.post_count}")
        print(f"Date range: {summary.date_range}")
        print(f"Average sentiment: {summary.avg_sentiment_score:.3f}")
        print()
        
        print("Sentiment Distribution:")
        for sentiment, count in summary.sentiment_distribution.items():
            percentage = (count / summary.post_count * 100) if summary.post_count > 0 else 0
            print(f"   {sentiment.value.capitalize()}: {count} posts ({percentage:.1f}%)")
        print()
        
        if summary.sentiment_trend:
            print(f"Sentiment trend: {summary.sentiment_trend}")
            print()
        
        if summary.top_topics:
            print(f"Top {len(summary.top_topics)} Topics:")
            for i, topic in enumerate(summary.top_topics[:3], 1):
                print(f"   {i}. {topic.topic_name} (relevance: {topic.relevance_score:.3f})")
            print()
        
        if summary.key_entities:
            print(f"Key entities found: {len(summary.key_entities)}")
            # Group entities by type
            entity_counts = {}
            for entity_type, count in summary.entity_types_count.items():
                entity_counts[entity_type.value] = count
            
            for entity_type, count in list(entity_counts.items())[:5]:
                print(f"   {entity_type}: {count}")
            print()
        
        print(f"Topic diversity score: {summary.topic_diversity:.3f}")
        
        processing_summary = summary.processing_summary
        if processing_summary:
            total_time = processing_summary.get("total_processing_time_ms", 0)
            avg_time = processing_summary.get("avg_processing_time_per_post_ms", 0)
            print(f"Processing time: {total_time:.1f}ms total, {avg_time:.1f}ms per post")
    else:
        print("❌ Analysis failed")
    
    # Display service status
    print_section("Service Status")
    service_status = analysis_service.get_service_status()
    print(f"Service initialized: {service_status['initialized']}")
    print(f"Companies analyzed: {service_status['companies_analyzed']}")
    print(f"Active jobs: {service_status['active_jobs']}")
    print(f"Total jobs: {service_status['total_jobs']}")


def main():
    """Run the complete Step 4 demo."""
    print("🚀 LinkedIn Company Analysis Tool - Step 4 Demo")
    print("   Basic NLP Processing Pipeline")
    print(f"   Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all demo components
        demo_sentiment_analysis()
        demo_topic_extraction() 
        demo_entity_recognition()
        demo_processing_pipeline()
        demo_analysis_service()
        
        print_banner("DEMO COMPLETED SUCCESSFULLY")
        print("✅ All NLP components are working correctly!")
        print("🎉 Step 4 implementation is complete and functional.")
        print()
        print("Next steps:")
        print("- Run tests: poetry run pytest tests/nlp/ -v")
        print("- Start the server: poetry run uvicorn src.linkedin_analyzer.main:app --reload")
        print("- Try the analysis API: POST /analysis/companies/{name}/analyze")
        
    except KeyboardInterrupt:
        print("\n\n❌ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())