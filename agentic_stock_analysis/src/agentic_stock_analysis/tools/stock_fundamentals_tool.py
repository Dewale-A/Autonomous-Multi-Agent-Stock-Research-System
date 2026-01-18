from crewai.tools import tool
import yfinance as yf
import json


@tool("stock_fundamentals")
def stock_fundamentals(ticker: str) -> str:
    """Fetches comprehensive financial ratios and fundamentals for a stock ticker."""
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        fundamentals = {
            "ticker": ticker.upper(),
            "company_name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "valuation": {
                "pe_ratio_trailing": info.get("trailingPE", "N/A"),
                "pe_ratio_forward": info.get("forwardPE", "N/A"),
                "price_to_book": info.get("priceToBook", "N/A"),
                "price_to_sales": info.get("priceToSalesTrailing12Months", "N/A"),
            },
            "profitability": {
                "gross_margin": info.get("grossMargins", "N/A"),
                "operating_margin": info.get("operatingMargins", "N/A"),
                "profit_margin": info.get("profitMargins", "N/A"),
                "roe": info.get("returnOnEquity", "N/A"),
            },
            "financial_health": {
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "current_ratio": info.get("currentRatio", "N/A"),
            },
            "per_share": {
                "eps_trailing": info.get("trailingEps", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
            },
            "analyst_data": {
                "target_mean": info.get("targetMeanPrice", "N/A"),
                "recommendation": info.get("recommendationKey", "N/A"),
            }
        }
        
        return json.dumps(fundamentals, indent=2, default=str)
        
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker}, indent=2)


@tool("compare_stocks")
def compare_stocks(tickers: str) -> str:
    """Compare fundamental metrics across multiple stocks (comma-separated)."""
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(",")]
        
        comparison = []
        for ticker in ticker_list[:10]:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                comparison.append({
                    "ticker": ticker,
                    "company": info.get("shortName", "N/A"),
                    "sector": info.get("sector", "N/A"),
                    "market_cap_B": round(info.get("marketCap", 0) / 1e9, 2) if info.get("marketCap") else "N/A",
                    "pe_ratio": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A",
                    "debt_to_equity": round(info.get("debtToEquity", 0), 2) if info.get("debtToEquity") else "N/A",
                    "roe_pct": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else "N/A",
                    "profit_margin_pct": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else "N/A",
                    "recommendation": info.get("recommendationKey", "N/A"),
                })
            except Exception as e:
                comparison.append({"ticker": ticker, "error": str(e)})
        
        return json.dumps({"comparison": comparison}, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@tool("stock_historical_data")
def stock_historical_data(ticker: str, period: str = "1mo") -> str:
    """Get historical price data with basic technical indicators."""
    try:
        import numpy as np
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period=period)
        
        if hist.empty:
            return json.dumps({"error": "No data found", "ticker": ticker}, indent=2)
        
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['SMA_20'].iloc[-1] if not hist['SMA_20'].isna().iloc[-1] else None
        sma_50 = hist['SMA_50'].iloc[-1] if not hist['SMA_50'].isna().iloc[-1] else None
        
        trend = "neutral"
        if sma_20 and sma_50:
            if current_price > sma_20 > sma_50:
                trend = "bullish"
            elif current_price < sma_20 < sma_50:
                trend = "bearish"
        
        returns = hist['Close'].pct_change().dropna()
        volatility = round(returns.std() * (252 ** 0.5) * 100, 2) if len(returns) > 1 else "N/A"
        
        return json.dumps({
            "ticker": ticker.upper(),
            "current_price": round(current_price, 2),
            "sma_20": round(sma_20, 2) if sma_20 else "N/A",
            "sma_50": round(sma_50, 2) if sma_50 else "N/A",
            "trend": trend,
            "volatility_pct": volatility,
            "period_high": round(hist['High'].max(), 2),
            "period_low": round(hist['Low'].min(), 2),
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker}, indent=2)





