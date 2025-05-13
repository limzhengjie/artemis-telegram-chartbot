from artemisbot.chart.chart_generator import ChartGenerator

def test_chart_generation():
    # Initialize the chart generator
    generator = ChartGenerator()
    
    # Test parameters
    metrics = ["price"]
    tickers = ["solana"]
    asset_type = "chain"
    time_period = "1w"
    granularity = "1d"
    
    try:
        # Generate chart
        chart_image, chart_url, title, analysis = generator.generate_chart(
            metrics, tickers, asset_type, time_period, granularity
        )
        
        print("✅ Chart generation successful!")
        print(f"Title: {title}")
        print(f"URL: {chart_url}")
        print(f"Analysis: {analysis[:200]}..." if analysis else "No analysis generated")
        print(f"Image size: {len(chart_image)} bytes")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_chart_generation() 