"""Mock Data Generator for LinkedIn Content

This module generates realistic mock LinkedIn posts and profiles
for testing and demonstration purposes without external API dependencies.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote

from ..models.linkedin_data import (
    LinkedInPost, LinkedInProfile, PostCollection, CollectionMetadata,
    EngagementMetrics, PostType, ContentSource
)
from ..models.company import CompanyConfiguration


class MockDataGenerator:
    """Generates realistic mock LinkedIn data for testing and demos."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the mock data generator.
        
        Args:
            seed: Random seed for reproducible data generation
        """
        if seed is not None:
            random.seed(seed)
        
        self._load_template_data()
    
    def _load_template_data(self) -> None:
        """Load template data for realistic content generation."""
        
        # Professional headlines by industry
        self.headlines = {
            "Technology": [
                "Senior Software Engineer at {company}",
                "Product Manager | AI & Machine Learning",
                "Full Stack Developer | React, Node.js, Python",
                "DevOps Engineer | Cloud Infrastructure Specialist",
                "Data Scientist | Analytics & ML",
                "Senior Frontend Developer | UI/UX",
                "Backend Engineer | Microservices Architecture",
                "Technical Lead | Software Development",
                "Solutions Architect | Enterprise Systems"
            ],
            "Finance": [
                "Senior Financial Analyst at {company}",
                "Investment Banking Associate",
                "Risk Management Specialist",
                "Corporate Finance Manager",
                "Financial Planning & Analysis",
                "Portfolio Manager | Equity Research",
                "Credit Risk Analyst",
                "Treasury Operations Manager"
            ],
            "Marketing": [
                "Digital Marketing Manager at {company}",
                "Content Marketing Specialist",
                "SEO & Growth Marketing",
                "Brand Marketing Manager",
                "Social Media Marketing Lead",
                "Product Marketing Manager",
                "Marketing Analytics Specialist",
                "Performance Marketing Manager"
            ],
            "Healthcare": [
                "Healthcare Data Analyst at {company}",
                "Medical Device Sales Representative",
                "Healthcare IT Consultant",
                "Clinical Research Associate",
                "Healthcare Operations Manager",
                "Medical Affairs Manager",
                "Pharmaceutical Sales Specialist"
            ],
            "default": [
                "Senior Manager at {company}",
                "Business Development Manager",
                "Operations Specialist",
                "Project Manager",
                "Customer Success Manager",
                "Business Analyst",
                "Account Manager",
                "Consultant"
            ]
        }
        
        # Post content templates by source type
        self.post_templates = {
            ContentSource.COMPANY_PAGE: [
                "Excited to announce our latest innovation in {industry}! 🚀\n\n{content_detail}\n\n#{hashtag1} #{hashtag2} #innovation",
                "We're proud to share that {company} has reached a new milestone! 🎉\n\n{achievement}\n\n#{hashtag1} #{hashtag2}",
                "Join our team! We're hiring talented professionals to help us {mission}.\n\n{job_details}\n\n#hiring #{hashtag1} #{hashtag2}",
                "Behind the scenes at {company}: {insight}\n\n{detail}\n\n#{hashtag1} #{hashtag2} #companylife",
                "Thrilled to welcome our new {role} to the {company} family! 👋\n\n{welcome_message}\n\n#{hashtag1} #{hashtag2} #teamgrowth"
            ],
            ContentSource.EMPLOYEE_POST: [
                "Another great day at {company}! Working on {project} with an amazing team. 💪\n\n{detail}\n\n#{hashtag1} #{hashtag2} #proudtowork",
                "Learned so much at today's {event} hosted by {company}. Key takeaways:\n\n{learnings}\n\n#{hashtag1} #{hashtag2} #growth",
                "6 months at {company} and loving every moment! The culture here is incredible. 🌟\n\n{culture_detail}\n\n#{hashtag1} #{hashtag2} #companyculture",
                "Grateful to be part of the {company} team working on {initiative}. Making a real impact! 🎯\n\n{impact_detail}\n\n#{hashtag1} #{hashtag2}",
                "Celebrating a major milestone with my {company} colleagues! {achievement}\n\n{celebration_detail}\n\n#{hashtag1} #{hashtag2} #teamwork"
            ],
            ContentSource.COMPANY_MENTION: [
                "Just had an amazing experience with {company}! Their {product_service} exceeded expectations. 🌟\n\n{experience_detail}\n\n#{hashtag1} #{hashtag2} #customerexperience",
                "Impressed by {company}'s commitment to {value}. This is how you build a sustainable business! 👏\n\n{detail}\n\n#{hashtag1} #{hashtag2}",
                "Great insights from {company} on {topic}. This is the future of {industry}! 🚀\n\n{insights}\n\n#{hashtag1} #{hashtag2} #innovation",
                "Partnering with {company} has been a game-changer for our business. {partnership_detail}\n\n#{hashtag1} #{hashtag2} #partnership",
                "Attended {company}'s {event} today. Fantastic speakers and networking! 🤝\n\n{event_highlights}\n\n#{hashtag1} #{hashtag2} #networking"
            ],
            ContentSource.HASHTAG_SEARCH: [
                "The latest trends in #{hashtag1} are fascinating! Here's what I'm seeing:\n\n{trend_analysis}\n\n#{hashtag2} #futureoftech",
                "#{hashtag1} is revolutionizing how we think about {topic}. Key developments:\n\n{developments}\n\n#{hashtag2} #innovation",
                "Why #{hashtag1} matters now more than ever: {reason}\n\n{explanation}\n\n#{hashtag2} #thoughtleadership",
                "My take on the #{hashtag1} space: {opinion}\n\n{supporting_points}\n\n#{hashtag2} #insights"
            ]
        }
        
        # Content details for realistic variation
        self.content_details = {
            "innovation": [
                "Our new AI-powered platform reduces processing time by 70%",
                "This breakthrough in machine learning will transform customer experience",
                "Introducing sustainable technology that cuts carbon emissions by 50%",
                "Revolutionary approach to data security using blockchain technology"
            ],
            "achievement": [
                "We've successfully served over 1 million customers worldwide",
                "Our team has grown by 200% this year while maintaining quality",
                "Achieved carbon-neutral operations ahead of our 2025 target",
                "Won the Innovation Award for our groundbreaking research"
            ],
            "culture": [
                "Everyone here is genuinely passionate about what we do",
                "The collaborative environment helps everyone grow professionally",
                "Work-life balance isn't just a buzzword here - it's lived daily",
                "Diversity and inclusion are core to our company DNA"
            ]
        }
        
        # Common locations for profiles
        self.locations = [
            "San Francisco Bay Area", "New York, NY", "London, UK", "Berlin, Germany",
            "Paris, France", "Toronto, Canada", "Amsterdam, Netherlands", "Singapore",
            "Sydney, Australia", "Tel Aviv, Israel", "Boston, MA", "Seattle, WA",
            "Chicago, IL", "Los Angeles, CA", "Barcelona, Spain", "Dublin, Ireland"
        ]
        
        # Common first and last names for profile generation
        self.first_names = [
            "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
            "Sarah", "Michael", "Emily", "David", "Jessica", "Daniel", "Ashley", "Christopher",
            "Amanda", "Matthew", "Jennifer", "Andrew", "Lisa", "Joshua", "Michelle", "James",
            "Emma", "John", "Olivia", "Robert", "Sophia", "William", "Isabella", "Benjamin"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
            "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
        ]
    
    def generate_profile(self, company: Optional[str] = None, is_employee: bool = False) -> LinkedInProfile:
        """Generate a realistic LinkedIn profile.
        
        Args:
            company: Company name for employee profiles
            is_employee: Whether this profile represents a company employee
            
        Returns:
            Generated LinkedIn profile
        """
        profile_id = f"linkedin_user_{uuid.uuid4().hex[:8]}"
        name = f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
        
        # Determine industry for headline selection
        industry = "default"
        if company:
            # Simple industry detection based on company name keywords
            company_lower = company.lower()
            if any(tech_word in company_lower for tech_word in ["tech", "software", "ai", "data", "digital"]):
                industry = "Technology"
            elif any(fin_word in company_lower for fin_word in ["bank", "finance", "capital", "investment"]):
                industry = "Finance"
            elif any(health_word in company_lower for health_word in ["health", "medical", "pharma", "bio"]):
                industry = "Healthcare"
            elif any(marketing_word in company_lower for marketing_word in ["marketing", "media", "advertising"]):
                industry = "Marketing"
        
        headline_template = random.choice(self.headlines.get(industry, self.headlines["default"]))
        headline = headline_template.format(company=company or "TechCorp")
        
        return LinkedInProfile(
            profile_id=profile_id,
            name=name,
            headline=headline,
            company=company,
            position=headline.split(" at ")[0] if " at " in headline else headline.split(" | ")[0],
            location=random.choice(self.locations),
            profile_url=f"https://www.linkedin.com/in/{name.lower().replace(' ', '-')}-{random.randint(1000, 9999)}",
            follower_count=random.randint(50, 10000),
            connection_count=random.randint(50, 500),
            is_company_employee=is_employee,
            verified=random.random() < 0.1  # 10% chance of being verified
        )
    
    def generate_engagement_metrics(self, post_type: PostType = PostType.POST) -> EngagementMetrics:
        """Generate realistic engagement metrics based on post type.
        
        Args:
            post_type: Type of post for engagement scaling
            
        Returns:
            Generated engagement metrics
        """
        # Base engagement ranges by post type
        base_ranges = {
            PostType.POST: (10, 200),
            PostType.ARTICLE: (50, 500),
            PostType.VIDEO: (20, 300),
            PostType.IMAGE: (15, 250),
            PostType.POLL: (30, 400),
            PostType.DOCUMENT: (5, 100)
        }
        
        min_eng, max_eng = base_ranges.get(post_type, (10, 200))
        
        # Generate likes (usually highest)
        likes = random.randint(min_eng, max_eng)
        
        # Comments are typically 5-20% of likes
        comments = random.randint(max(1, int(likes * 0.05)), int(likes * 0.2))
        
        # Shares are typically 2-10% of likes
        shares = random.randint(0, max(1, int(likes * 0.1)))
        
        # Views are 10-50x engagement for video content
        views = None
        if post_type in [PostType.VIDEO, PostType.ARTICLE]:
            total_engagement = likes + comments + shares
            views = random.randint(total_engagement * 10, total_engagement * 50)
        
        return EngagementMetrics(
            likes=likes,
            comments=comments,
            shares=shares,
            views=views
        )
    
    def generate_post_content(
        self, 
        company_config: CompanyConfiguration, 
        source: ContentSource,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate realistic post content based on company and source.
        
        Args:
            company_config: Company configuration for context
            source: Content source type
            language: Language code for content
            
        Returns:
            Dictionary with content and metadata
        """
        company_name = company_config.profile.name
        industry = company_config.profile.industry or "Technology"
        hashtags = company_config.profile.hashtags[:2]  # Use first 2 hashtags
        
        # Ensure we have at least 2 hashtags for templates
        if len(hashtags) < 2:
            default_hashtags = ["#innovation", "#technology", "#business", "#growth", "#team"]
            hashtags.extend(default_hashtags[:2 - len(hashtags)])
        
        # Clean hashtags (remove # if present)
        clean_hashtags = [tag.lstrip('#') for tag in hashtags]
        
        template = random.choice(self.post_templates.get(source, self.post_templates[ContentSource.COMPANY_PAGE]))
        
        # Generate content details based on context
        content_detail = random.choice(self.content_details.get("innovation", ["Amazing progress on our latest project!"]))
        achievement = random.choice(self.content_details.get("achievement", ["Reached a significant milestone!"]))
        culture_detail = random.choice(self.content_details.get("culture", ["Great teamwork and collaboration!"]))
        
        # Fill template with dynamic content
        content = template.format(
            company=company_name,
            industry=industry.lower(),
            hashtag1=clean_hashtags[0],
            hashtag2=clean_hashtags[1] if len(clean_hashtags) > 1 else "business",
            content_detail=content_detail,
            achievement=achievement,
            culture_detail=culture_detail,
            mission="transform the industry",
            job_details="Apply now for exciting opportunities!",
            insight="how we build amazing products",
            detail="It's all about the team and culture",
            role="Software Engineer",
            welcome_message="Welcome to the team!",
            project="innovative solutions",
            event="tech conference",
            learnings="• Innovation drives success\n• Teamwork makes the dream work\n• Customer focus is key",
            initiative="sustainable technology",
            impact_detail="Creating positive change in our community",
            celebration_detail="Team effort made this possible!",
            product_service="customer service",
            experience_detail="Professional, efficient, and friendly service",
            value="sustainability and innovation",
            topic="artificial intelligence",
            insights="The future is bright with AI integration",
            partnership_detail="Collaborative innovation at its best",
            event_highlights="Great presentations and meaningful connections",
            trend_analysis="• Growing adoption rates\n• Improved user experience\n• Cost-effective solutions",
            developments="• New frameworks\n• Better tooling\n• Enhanced security",
            reason="digital transformation acceleration",
            explanation="Companies need modern solutions to stay competitive",
            opinion="the space is evolving rapidly",
            supporting_points="• Market demand is high\n• Technology is maturing\n• ROI is proven"
        )
        
        # Extract hashtags and mentions from generated content
        import re
        hashtags_in_content = re.findall(r'#\w+', content)
        mentions_in_content = re.findall(r'@\w+', content)
        
        return {
            "content": content,
            "hashtags": hashtags_in_content,
            "mentions": mentions_in_content,
            "company_mentioned": company_name.lower() in content.lower()
        }
    
    def generate_post(
        self, 
        company_config: CompanyConfiguration,
        source: ContentSource,
        author: Optional[LinkedInProfile] = None,
        days_ago: int = 0,
        language: str = "en"
    ) -> LinkedInPost:
        """Generate a realistic LinkedIn post.
        
        Args:
            company_config: Company configuration for context
            source: How this content was collected
            author: Post author (will be generated if None)
            days_ago: How many days ago the post was published
            language: Content language
            
        Returns:
            Generated LinkedIn post
        """
        post_id = f"linkedin_post_{uuid.uuid4().hex[:12]}"
        
        # Generate author if not provided
        if author is None:
            is_employee = source == ContentSource.EMPLOYEE_POST
            author = self.generate_profile(
                company=company_config.profile.name if is_employee else None,
                is_employee=is_employee
            )
        
        # Generate post content
        content_data = self.generate_post_content(company_config, source, language)
        
        # Random post type (mostly posts with some variety)
        post_type = random.choices(
            [PostType.POST, PostType.ARTICLE, PostType.VIDEO, PostType.IMAGE, PostType.POLL],
            weights=[60, 15, 15, 8, 2]
        )[0]
        
        # Generate engagement metrics
        engagement = self.generate_engagement_metrics(post_type)
        
        # Calculate publication time
        published_at = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        # Generate URLs if applicable
        images = []
        video_url = None
        links = []
        
        if post_type == PostType.IMAGE:
            images = [f"https://media.licdn.com/image_{random.randint(1000, 9999)}.jpg"]
        elif post_type == PostType.VIDEO:
            video_url = f"https://media.licdn.com/video_{random.randint(1000, 9999)}.mp4"
        
        # Random chance of external links
        if random.random() < 0.3:  # 30% chance
            links = [f"https://{company_config.profile.email_domain}/blog/{random.randint(1, 100)}"]
        
        post_url = f"https://www.linkedin.com/posts/{author.profile_id}_{random.randint(1000000, 9999999)}"
        
        # Calculate sentiment and relevance scores
        sentiment_score = random.uniform(-0.2, 0.8)  # Generally positive sentiment
        if source == ContentSource.COMPANY_PAGE:
            sentiment_score = random.uniform(0.3, 0.9)  # Company posts are more positive
        
        relevance_score = random.uniform(0.6, 1.0)
        if source == ContentSource.HASHTAG_SEARCH:
            relevance_score = random.uniform(0.3, 0.8)  # Hashtag searches may be less relevant
        
        return LinkedInPost(
            post_id=post_id,
            author=author,
            content=content_data["content"],
            post_type=post_type,
            language=language,
            published_at=published_at,
            engagement=engagement,
            hashtags=content_data["hashtags"],
            mentions=content_data["mentions"],
            links=links,
            images=images,
            video_url=video_url,
            post_url=post_url,
            source=source,
            company_mentioned=content_data["company_mentioned"],
            sentiment_score=sentiment_score,
            relevance_score=relevance_score,
            metadata={
                "generated": True,
                "industry": company_config.profile.industry,
                "company_size": company_config.profile.size
            }
        )
    
    def generate_post_collection(
        self,
        company_config: CompanyConfiguration,
        num_posts: int = 50,
        date_range_days: int = 30
    ) -> PostCollection:
        """Generate a complete post collection for a company.
        
        Args:
            company_config: Company configuration
            num_posts: Total number of posts to generate
            date_range_days: Date range for post generation
            
        Returns:
            Complete post collection with metadata
        """
        collection_id = f"collection_{uuid.uuid4().hex[:12]}"
        
        # Create collection metadata
        start_date = datetime.utcnow() - timedelta(days=date_range_days)
        end_date = datetime.utcnow()
        
        metadata = CollectionMetadata(
            collection_id=collection_id,
            company_name=company_config.profile.name,
            date_range_start=start_date,
            date_range_end=end_date,
            sources_collected=[
                ContentSource.COMPANY_PAGE,
                ContentSource.EMPLOYEE_POST,
                ContentSource.COMPANY_MENTION,
                ContentSource.HASHTAG_SEARCH
            ],
            languages=company_config.settings.languages,
            collection_status="completed"
        )
        
        collection = PostCollection(metadata=metadata)
        
        # Distribute posts across sources
        source_distribution = {
            ContentSource.COMPANY_PAGE: 0.2,      # 20% official company posts
            ContentSource.EMPLOYEE_POST: 0.4,    # 40% employee posts
            ContentSource.COMPANY_MENTION: 0.25, # 25% mentions
            ContentSource.HASHTAG_SEARCH: 0.15   # 15% hashtag searches
        }
        
        # Generate posts for each source
        for source, ratio in source_distribution.items():
            source_posts = int(num_posts * ratio)
            
            for i in range(source_posts):
                # Random days ago within date range
                days_ago = random.randint(0, date_range_days)
                
                # Random language from company settings
                language = random.choice(company_config.settings.languages)
                
                post = self.generate_post(
                    company_config=company_config,
                    source=source,
                    days_ago=days_ago,
                    language=language
                )
                
                collection.add_post(post)
        
        # Mark collection as completed
        collection.metadata.collection_completed_at = datetime.utcnow()
        collection.metadata.collection_status = "completed"
        
        return collection