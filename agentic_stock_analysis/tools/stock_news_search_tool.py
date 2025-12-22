from crewai.tools import tool
from typing import Optional
import json


@tool("stock_news_search")
def stock_news_search(query: str, max_results: int = 5) -> str:
    """
    Search for stock market news and financial headlines.
    
    Args:
        query: Search query for stock news (e.g., ticker symbol, company name, or topic)
        max_results: Maximum number of news items to return (default: 5)
    
    Returns:
        JSON string containing news articles with title, source, summary, and sentiment
    """
    try:
        import yfinance as yf
        
        ticker = yf.Ticker(query.upper())
        news = ticker.news
        
        if news:
            articles = []
            for i, article in enumerate(news[:max_results]):
                articles.append({
                    "title": article.get("title", "N/A"),
                    "publisher": article.get("publisher", "N/A"),
                    "link": article.get("link", "N/A"),
                    "published": article.get("providerPublishTime", "N/A"),
                    "type": article.get("type", "N/A"),
                    "related_tickers": article.get("relatedTickers", [])
                })
            
            return json.dumps({
                "query": query,
                "total_results": len(articles),
                "articles": articles
            }, indent=2)
        else:
            return json.dumps({
                "query": query,
                "total_results": 0,
                "articles": [],
                "message": f"No news found for '{query}'."
            }, indent=2)
            
    except Exception as e:
        return json.dumps({"error": str(e), "query": query}, indent=2)


@tool("market_trending_tickers")
def market_trending_tickers() -> str:
    """Get currently trending and most active tickers in the market."""
    try:
        import yfinance as yf
        
        trending_data = {"trending_tickers": [], "market_indices": []}
        
        indices = {"^GSPC": "S&P 500", "^DJI": "Dow Jones", "^IXIC": "NASDAQ", "^VIX": "VIX"}
        
        for symbol, name in indices.items():
            try:
                idx = yf.Ticker(symbol)
                hist = idx.history(period="2d")
                if len(hist) >= 2:
                    prev_close = hist['Close'].iloc[-2]
                    current = hist['Close'].iloc[-1]
                    change_pct = ((current - prev_close) / prev_close) * 100
                    trending_data["market_indices"].append({
                        "index": name, "symbol": symbol,
                        "current": round(current, 2), "change_percent": round(change_pct, 2)
                    })
            except:
                continue
        
        popular_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", 
                          "JPM", "V", "UNH", "XOM", "JNJ", "WMT", "PG", "MA"]
        
        movers = []
        for ticker in popular_tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2d")
                if len(hist) >= 2:
                    prev_close = hist['Close'].iloc[-2]
                    current = hist['Close'].iloc[-1]
                    volume = hist['Volume'].iloc[-1]
                    change_pct = ((current - prev_close) / prev_close) * 100
                    movers.append({
                        "ticker": ticker, "price": round(current, 2),
                        "change_percent": round(change_pct, 2), "volume": int(volume)
                    })
            except:
                continue
        
        movers_sorted = sorted(movers, key=lambda x: abs(x["change_percent"]), reverse=True)
        trending_data["trending_tickers"] = movers_sorted[:10]
        trending_data["top_gainers"] = sorted(movers, key=lambda x: x["change_percent"], reverse=True)[:5]
        trending_data["top_losers"] = sorted(movers, key=lambda x: x["change_percent"])[:5]
        
        return json.dumps(trending_data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@tool("sector_performance")
def sector_performance() -> str:
    """Get current sector performance data using sector ETFs."""
    try:
        import yfinance as yf
        
        sector_etfs = {
            "XLK": "Technology", "XLF": "Financials", "XLV": "Healthcare",
            "XLE": "Energy", "XLY": "Consumer Discretionary", "XLP": "Consumer Staples",
            "XLI": "Industrials", "XLB": "Materials", "XLU": "Utilities"
        }
        
        sector_data = []
        for etf, sector in sector_etfs.items():
            try:
                ticker = yf.Ticker(etf)
                hist = ticker.history(period="5d")
                if len(hist) >= 2:
                    prev_close = hist['Close'].iloc[-2]
                    current = hist['Close'].iloc[-1]
                    daily_change = ((current - prev_close) / prev_close) * 100
                    sector_data.append({
                        "sector": sector, "etf": etf,
                        "price": round(current, 2), "daily_change_pct": round(daily_change, 2)
                    })
            except:
                continue
        
        sector_data = sorted(sector_data, key=lambda x: x["daily_change_pct"], reverse=True)
        return json.dumps({"sectors": sector_data}, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

