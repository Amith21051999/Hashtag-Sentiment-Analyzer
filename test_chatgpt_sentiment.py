#!/usr/bin/env python3
"""
Test script for ChatGPT-powered sentiment analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sentiment_analyzer import sentiment_analyzer
import json

def test_sentiment_analysis():
    """Test the ChatGPT sentiment analyzer with sample tweets"""
    
    print("* Testing ChatGPT-Powered Sentiment Analysis")
    print("=" * 60)
    
    # Sample tweets with different sentiments
    test_tweets = [
        {
            'id': '1',
            'text': 'I absolutely love this new Python library! It makes coding so much easier 😍 #python',
            'author_id': 'user1',
            'created_at': '2025-01-15T10:00:00Z',
            'public_metrics': {'like_count': 25, 'retweet_count': 10}
        },
        {
            'id': '2', 
            'text': 'This is the worst bug I have ever encountered. Completely broken! 😡 #frustrated',
            'author_id': 'user2',
            'created_at': '2025-01-15T11:00:00Z',
            'public_metrics': {'like_count': 3, 'retweet_count': 1}
        },
        {
            'id': '3',
            'text': 'Just updating my documentation. Nothing exciting happening today. #work',
            'author_id': 'user3',
            'created_at': '2025-01-15T12:00:00Z',
            'public_metrics': {'like_count': 8, 'retweet_count': 2}
        },
        {
            'id': '4',
            'text': 'Yeah, right... this "amazing" feature is totally not working 🙄 #sarcasm',
            'author_id': 'user4',
            'created_at': '2025-01-15T13:00:00Z',
            'public_metrics': {'like_count': 15, 'retweet_count': 5}
        }
    ]
    
    print(f"📝 Analyzing {len(test_tweets)} sample tweets...")
    print("\nSample tweets:")
    for i, tweet in enumerate(test_tweets, 1):
        print(f"{i}. {tweet['text']}")
    
    print("\n" + "=" * 60)
    print("🤖 Running ChatGPT Analysis...")
    
    try:
        # Test the sentiment analyzer
        results = sentiment_analyzer.analyze_tweets_batch(test_tweets)
        
        print("✅ Analysis completed successfully!")
        print("\n📊 RESULTS:")
        
        # Display summary
        print(f"Total analyzed: {results['statistics']['total_analyzed']}")
        print(f"Average confidence: {results['statistics']['average_confidence']:.2f}")
        print(f"Analysis method: {results['api_usage']['analysis_method']}")
        
        if results['api_usage']['analysis_method'] == 'chatgpt':
            print(f"💰 Estimated cost: ${results['api_usage']['estimated_cost']:.4f}")
            print(f"🔧 API calls made: {results['api_usage']['calls_made']}")
        
        print(f"\n📈 Sentiment Breakdown:")
        breakdown = results['sentiment_breakdown']
        percentages = results['sentiment_percentages']
        
        print(f"  Positive: {breakdown['positive']} tweets ({percentages['positive']}%)")
        print(f"  Negative: {breakdown['negative']} tweets ({percentages['negative']}%)")
        print(f"  Neutral:  {breakdown['neutral']} tweets ({percentages['neutral']}%)")
        
        print(f"\n⭐ Sample Results:")
        for category in ['positive', 'negative', 'neutral']:
            samples = results['sample_tweets'][category]
            if samples:
                print(f"\n{category.upper()} Examples:")
                for sample in samples[:2]:  # Show first 2
                    print(f"  • \"{sample['text'][:60]}...\"")
                    print(f"    Score: {sample['score']}, Confidence: {sample['confidence']}")
                    if sample.get('reasoning'):
                        print(f"    Reasoning: {sample['reasoning']}")
                    if sample.get('detected_elements'):
                        elements = sample['detected_elements']
                        if elements.get('sarcasm'):
                            print(f"    🎭 Sarcasm detected!")
                        if elements.get('emoji_sentiment'):
                            print(f"    😊 Emoji sentiment: {elements['emoji_sentiment']}")
        
        # Show ChatGPT insights if available
        if 'chatgpt_insights' in results and results['chatgpt_insights']:
            insights = results['chatgpt_insights']
            print(f"\n🧠 ChatGPT Insights:")
            
            if 'advanced_detection' in insights:
                detection = insights['advanced_detection']
                print(f"  Sarcasm detected: {detection.get('sarcasm_detected', 0)} tweets")
                print(f"  Negation patterns: {detection.get('negation_patterns', 0)} tweets")
                
                emoji_analysis = detection.get('emoji_analysis', {})
                if any(emoji_analysis.values()):
                    print(f"  Emoji analysis: {emoji_analysis}")
            
            if 'analysis_quality' in insights:
                quality = insights['analysis_quality']
                print(f"  High confidence analyses: {quality.get('high_confidence_analyses', 0)}")
                print(f"  ChatGPT success rate: {quality.get('chatgpt_success_rate', 0):.1%}")
        
        print(f"\n🎯 Test completed successfully!")
        
        # Show individual tweet analyses for debugging
        if results.get('detailed_analyses'):
            print(f"\n🔍 Detailed Analysis:")
            for analysis in results['detailed_analyses'][:2]:  # Show first 2
                print(f"\nTweet: \"{analysis['original_text'][:50]}...\"")
                print(f"  Sentiment: {analysis['sentiment']}")
                print(f"  Score: {analysis['score']}")
                print(f"  Confidence: {analysis['confidence']}")
                print(f"  Method: {analysis['analysis_method']}")
                if analysis.get('reasoning'):
                    print(f"  Reasoning: {analysis['reasoning']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_single_tweet():
    """Test single tweet analysis"""
    print(f"\n" + "=" * 60)
    print("🔬 Testing Single Tweet Analysis")
    
    test_text = "This is amazing! I can't believe how well this works! * #awesome"
    print(f"Tweet: {test_text}")
    
    try:
        result = sentiment_analyzer.analyze_tweet(test_text)
        
        print(f"✅ Single tweet analysis completed!")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Score: {result['score']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Method: {result['analysis_method']}")
        
        if result.get('reasoning'):
            print(f"Reasoning: {result['reasoning']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Single tweet test failed: {e}")
        return False

if __name__ == "__main__":
    print("ChatGPT Sentiment Analysis Test Suite")
    print("This will test the ChatGPT-powered sentiment analyzer")
    
    # Check if OpenAI API key is available
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment")
        print("   The system will fall back to traditional sentiment analysis")
        print("   Add your OpenAI API key to .env file for full ChatGPT functionality")
    else:
        print("✅ OpenAI API key found - ChatGPT analysis enabled")
    
    print()
    
    # Run tests
    batch_success = test_sentiment_analysis()
    single_success = test_single_tweet()
    
    print(f"\n" + "=" * 60)
    print("🏁 TEST SUMMARY:")
    print(f"Batch Analysis: {'✅ PASSED' if batch_success else '❌ FAILED'}")
    print(f"Single Tweet:   {'✅ PASSED' if single_success else '❌ FAILED'}")
    
    if batch_success and single_success:
        print(f"\n🎉 All tests passed! ChatGPT sentiment analyzer is working correctly.")
        print(f"Ready to analyze real Twitter data with advanced AI sentiment analysis!")
    else:
        print(f"\n⚠️  Some tests failed. Check the error messages above.")